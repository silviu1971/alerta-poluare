#!/usr/bin/env python3
"""
Alertă poluare Iași - Telegram Bot
Rulează la fiecare 2 ore pe Render
"""

import requests
import os
from datetime import datetime

TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN", "9165222784:AAHXCQ2TFz8Gi20jOSU1-muzIUk_3R_uV-0")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID", "683894763")
API_URL = "https://silviugurlui.base44.app/functions/prognoza"
THRESHOLD_WARNING = 100
THRESHOLD_INSTANT = 200
HOURS_AHEAD = 6

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
    current_hour = now.hour
    warnings = []
    instant = []
    
    for zone in ZONES:
        data = check_zone(zone)
        if not data:
            continue
        
        pm10_values = data.get("pm10", [])
        hours = data.get("hours", [])
        
        for h, pm in zip(hours, pm10_values):
            if h == current_hour and pm > THRESHOLD_INSTANT:
                instant.append({"zone": zone["name"], "pm10": pm, "hour": h})
            
            hours_until = (h - current_hour) % 24
            if 0 < hours_until <= HOURS_AHEAD and pm > THRESHOLD_WARNING:
                warnings.append({"zone": zone["name"], "pm10": pm, "hour": h, "hours_until": hours_until})
    
    if instant:
        msg = "🚨 <b>ALERTĂ INSTANT - POLUARE EXTREMĂ</b>\n\n"
        for a in instant:
            msg += f"📍 <b>{a['zone']}</b>: {a['pm10']} µg/m³\n"
        msg += "\n👉 <a href='https://silviugurlui.ro/poluare'>Verifică harta</a>"
        send_telegram(msg)
    
    if warnings:
        msg = "⚠️ <b>PROGNOZĂ POLUARE RIDICATĂ</b>\n\n"
        for a in warnings:
            msg += f"📍 <b>{a['zone']}</b>: {a['pm10']} µg/m³ (peste {a['hours_until']}h)\n"
        msg += "\n👉 <a href='https://silviugurlui.ro/poluare'>Verifică harta</a>"
        send_telegram(msg)
    
    print(f"Check complete: {len(instant)} instant, {len(warnings)} warnings")

if __name__ == "__main__":
    main()
