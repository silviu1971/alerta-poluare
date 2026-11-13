#!/usr/bin/env python3
"""
Alertă poluare Iași - Telegram Bot
Rulează la fiecare 2 ore
"""

import requests
import os
from datetime import datetime

TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN", "9165222784:AAHXCQ2TFz8Gi20jOSU1-muzIUk_3R_uV-0")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID", "683894763")
API_URL = "https://silviugurlui.base44.app/functions/prognoza"
THRESHOLD = 100

ZONES = [
    {"name": "Podu de Piatră", "lat": 47.157, "lon": 27.575},
    {"name": "Centru", "lat": 47.160, "lon": 27.590},
    {"name": "Copou", "lat": 47.175, "lon": 27.570},
    {"name": "Tătărași", "lat": 47.165, "lon": 27.610},
    {"name": "Nicolina", "lat": 47.145, "lon": 27.600},
    {"name": "Galata", "lat": 47.140, "lon": 27.560},
]

def send_telegram(message):
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    data = {"chat_id": TELEGRAM_CHAT_ID, "text": message, "parse_mode": "HTML"}
    try:
        r = requests.post(url, data=data, timeout=10)
        return r.status_code == 200
    except:
        return False

def check_zone(zone):
    try:
        r = requests.get(f"{API_URL}?lat={zone['lat']}&lon={zone['lon']}", timeout=15)
        return r.json()
    except:
        return None

def main():
    now = datetime.now()
    max_zone = None
    max_pm10 = 0
    max_hour = 0
    
    for zone in ZONES:
        data = check_zone(zone)
        if not data:
            continue
        pm10_values = data.get("pm10", [])
        hours = data.get("hours", [])
        for h, pm in zip(hours, pm10_values):
            if pm > max_pm10:
                max_pm10 = pm
                max_zone = zone["name"]
                max_hour = h
    
    if max_pm10 >= THRESHOLD and max_zone:
        # Date meteo exemplu (poți adăuga preluare reală dacă API-ul le oferă)
        msg = f"""⚠️ ALERTĂ POLUARE IAȘI

Cea mai poluată zonă va fi {max_zone}
Ora estimată: {max_hour:02d}:00
PM10 estimat: {int(max_pm10)} µg/m³

Vânt: 1.2 m/s din NE
Umiditate: 87%
Temperatură: 6°C
Inversiune termică: da

Pentru detalii privind orice zonă din Iași și evoluția pe 2 zile consultați:
https://silviugurlui.ro/poluare"""
        send_telegram(msg)
        print(f"Alert sent: {max_zone} {max_pm10} at {max_hour}")
    else:
        print(f"No alert. Max PM10: {max_pm10}")

if __name__ == "__main__":
    main()
