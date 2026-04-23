import network, socket, json, time, gc, utime
from machine import Pin, Timer, I2C

gc.collect()

# ===== WIFI =====
SSID = ''
PWD  = ''

# ===== LED =====
led = Pin("LED", Pin.OUT)
Timer(-1).init(period=1000, mode=Timer.PERIODIC, callback=lambda t: led.toggle())

# ===== HARDWARE =====
LEDS = {5:Pin(2,1),4:Pin(3,1),3:Pin(18,1),2:Pin(19,1),1:Pin(20,1)}
buzzer = Pin(15, Pin.OUT)
alarm_timer = Timer(-1)

level = 5
bericht = "VEILIG"
alarm = False

# ===== LCD =====
class LCD:
    def __init__(self,i2c,addr):
        self.i2c=i2c; self.addr=addr; self.bl=8
        utime.sleep_ms(20)
        for x in [0x30,0x30,0x30,0x20]: self._w(x)
        for x in [0x28,0x0C,0x06,0x01]: self.cmd(x)

    def _w(self,v):
        self.i2c.writeto(self.addr,bytes([v|self.bl]))
        self.i2c.writeto(self.addr,bytes([v|self.bl|4]))
        self.i2c.writeto(self.addr,bytes([v|self.bl]))

    def cmd(self,c):
        self._w(c&0xF0); self._w((c<<4)&0xF0)
        if c<=3: utime.sleep_ms(2)

    def txt(self,s,row=0):
        self.cmd(0x80 | (0x40 if row else 0))
        for ch in s:
            v=ord(ch)
            self._w(v&0xF0|1); self._w((v<<4)&0xF0|1)

def pad(s):
    return (str(s)+" "*16)[:16]

i2c = I2C(0,sda=Pin(0),scl=Pin(1),freq=100000)
addr = i2c.scan()[0]
lcd = LCD(i2c, addr)

def show(a,b=""):
    lcd.cmd(1)
    lcd.txt(pad(a),0)
    lcd.txt(pad(b),1)

# ===== DEFCON =====
def standaard(l):
    return {5:"VEILIG",4:"LAAG RISICO",3:"VERHOOGD",2:"HOGE DREIGING",1:"ALARM"}.get(l,"?")

def reset():
    for x in LEDS.values(): x.value(0)
    buzzer.value(0)

def alarm_cb(t):
    global alarm
    alarm = not alarm
    LEDS[1].value(alarm)
    buzzer.value(alarm)

def set_level(l,msg=None):
    global level, bericht
    try: l=int(l)
    except: return False
    if l<1 or l>5: return False

    alarm_timer.deinit()
    reset()

    level = l
    bericht = msg if msg else standaard(l)

    if l==1:
        alarm_timer.init(period=300,mode=Timer.PERIODIC,callback=alarm_cb)
    else:
        LEDS[l].value(1)

    show("DEFCON {}".format(l), bericht)
    return True

# ===== WIFI =====
wlan = network.WLAN(network.STA_IF)
wlan.active(True)
wlan.connect(SSID,PWD)
while not wlan.isconnected(): time.sleep(0.5)

ip = wlan.ifconfig()[0]
print("Server:", ip)

# ===== FILE SERVER =====
def serve_file(conn, name, ctype="text/html"):
    try:
        with open(name) as f:
            data = f.read()
        res = "HTTP/1.1 200 OK\r\nContent-Type: {}\r\n\r\n{}".format(ctype, data)
    except:
        res = "HTTP/1.1 404 Not Found\r\n\r\nfile"
    conn.send(res)

# ===== SERVER =====
s = socket.socket()
s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
s.bind(('',80))
s.listen(1)

set_level(5,"ONLINE")

while True:
    try:
        conn, addr = s.accept()
        req = conn.recv(1024).decode('utf-8','ignore')
        first = req.split("\r\n")[0]

        # ===== UI =====
        if "GET / " in first:
            serve_file(conn, "index.html")
            continue

        elif "GET /warpnet.css" in first:
            serve_file(conn, "warpnet.css", "text/css")
            continue

        # ===== API =====
        if "GET /status" in first:
            body = {"level":level,"message":bericht}

        elif "POST /alert" in first:
            try:
                data = json.loads(req.split("\r\n\r\n")[1])
                ok = set_level(data.get("level"),data.get("message"))
                body = {"success":ok}
            except:
                body = {"error":"json"}

        elif "POST /message" in first:
            try:
                data = json.loads(req.split("\r\n\r\n")[1])
                bericht = str(data.get("message",""))
                show("DEFCON {}".format(level), bericht)
                body = {"success":True}
            except:
                body = {"error":"json"}

        else:
            body = {"error":"endpoint"}

        res = "HTTP/1.1 200 OK\r\nContent-Type: application/json\r\n\r\n"+json.dumps(body)
        conn.send(res)

    except Exception as e:
        print("err:", e)

    finally:
        try: conn.close()
        except: pass
        gc.collect()
