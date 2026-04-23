# DEFCON systeem (Pico W)

<img width="509" height="358" alt="image" src="https://github.com/user-attachments/assets/e8506bc5-e517-4971-b683-cc7f7cfa4ca4" />

Een simpel project met een Raspberry Pi Pico W waarbij je een DEFCON level kan instellen via een webpagina of via curl.

Het systeem stuurt:
- LEDs (per level)
- een buzzer (bij alarm)
- een LCD scherm met status/bericht

---

## Wat kan het?

- DEFCON 1 t/m 5 instellen
- bericht sturen naar LCD
- bedienen via browser
- bedienen via curl

---

## Gebruik

### Web UI
Ga naar:
http://<IP-van-je-pico>

Daar kun je op knoppen drukken of een bericht sturen.

---

### API (curl)

Level zetten:
curl -X POST http://<IP>/alert -d '{"level":1}'

Bericht sturen:
curl -X POST http://<IP>/message -d '{"message":"test"}'

Status checken:
curl http://<IP>/status

---

## Hardware

- LEDs op:
  - GP2
  - GP3
  - GP18
  - GP19
  - GP20
- Buzzer op GP15
- LCD via I2C (GP0 + GP1)

---

## Setup

1. Zet MicroPython op je Pico
2. Open Thonny
3. Upload deze bestanden naar de Pico:
   - main.py
   - index.html
   - warpnet.css
4. Vul je WiFi in in main.py
5. Run de code

---

## Opmerking

- Alles draait op de Pico zelf (ook de webpagina)
- Geen login of beveiliging
- Werkt alleen op lokaal netwerk

---

## Ideeën voor later

- live status in de UI
- betere styling
- misschien een wachtwoord erop
