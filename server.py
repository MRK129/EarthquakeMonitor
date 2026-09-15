from fastapi import FastAPI
from datetime import datetime
import os
import json
import urllib.request
import urllib.parse
import time

app = FastAPI(
    title="Earthquake Monitor Server"
)

latest_data = {
    "ax": 0.0,
    "ay": 0.0,
    "az": 0.0,
    "magnitude": 0.0,
    "rms": 0.0,
    "frequency": 0.0,
    "amplitude": 0.0,
    "status": "NORMAL",
    "level": "NORMAL",
    "timestamp": None
}

# -----------------------------------------------------
# Notification settings
# -----------------------------------------------------

TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")

last_alert_time = 0
ALERT_COOLDOWN = 60


def send_telegram(message):

    global last_alert_time

    if not TELEGRAM_BOT_TOKEN or not TELEGRAM_CHAT_ID:
        print("Telegram notification not configured.")
        return

    now = time.time()

    if now - last_alert_time < ALERT_COOLDOWN:
        print("Alert cooldown active.")
        return

    url = (
        "https://api.telegram.org/bot"
        + TELEGRAM_BOT_TOKEN
        + "/sendMessage"
    )

    data = urllib.parse.urlencode({
        "chat_id": TELEGRAM_CHAT_ID,
        "text": message
    }).encode()

    try:
        request = urllib.request.Request(
            url,
            data=data,
            method="POST"
        )

        with urllib.request.urlopen(request, timeout=10) as response:
            print("Telegram response:", response.status)

        last_alert_time = now

    except Exception as e:
        print("Telegram error:", e)


@app.get("/")
def home():
    return {
        "status": "online",
        "system": "Earthquake Monitor"
    }


@app.get("/status")
def status():
    return {
        "server": "online",
        "time": datetime.now().isoformat()
    }


@app.post("/sensor")
def receive_sensor_data(data: dict):

    global latest_data

    rms = float(data.get("rms", 0.0))

    # -------------------------------------------------
    # Server-side intensity classification
    # -------------------------------------------------

    if rms < 0.025:
        level = "NORMAL"

    elif rms < 0.070:
        level = "YELLOW"

    elif rms < 0.170:
        level = "ORANGE"

    else:
        level = "RED"


    if level == "NORMAL":
        status = "NORMAL"
    else:
        status = "DETECTED"


    latest_data = {
        "ax": data.get("ax", 0.0),
        "ay": data.get("ay", 0.0),
        "az": data.get("az", 0.0),
        "magnitude": data.get("magnitude", 0.0),
        "rms": rms,
        "frequency": data.get("frequency", 0.0),
        "amplitude": data.get("amplitude", 0.0),
        "status": status,
        "level": level,
        "timestamp": datetime.now().isoformat()
    }


    print("Sensor data received:")
    print(latest_data)


    # -------------------------------------------------
    # Phone alert
    # -------------------------------------------------

    if level == "ORANGE" or level == "RED":

        message = (
            "⚠️ EARTHQUAKE MONITOR ALERT\n\n"
            "Seismic vibration anomaly detected.\n\n"
            f"Level: {level}\n"
            f"RMS: {rms:.3f} g\n"
            f"Frequency: {float(data.get('frequency', 0.0)):.2f} Hz\n"
            f"Amplitude: {float(data.get('amplitude', 0.0)):.3f} g\n\n"
            "This is a vibration anomaly alert, "
            "not a guaranteed earthquake prediction."
        )

        send_telegram(message)


    return {
        "status": "received",
        "data": latest_data
    }


@app.get("/sensor")
def get_sensor_data():
    return latest_data
