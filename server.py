from fastapi import FastAPI
from datetime import datetime

app = FastAPI(title="Earthquake Monitor Server")

latest_data = {
    "ax": 0.0,
    "ay": 0.0,
    "az": 0.0,
    "magnitude": 0.0,
    "timestamp": None
}


@app.get("/")
def home():
    return {
        "status": "online",
        "system": "Earthquake Monitor"
    }


@app.post("/sensor")
def receive_sensor_data(data: dict):
    global latest_data

    latest_data = {
        "ax": data.get("ax", 0.0),
        "ay": data.get("ay", 0.0),
        "az": data.get("az", 0.0),
        "magnitude": data.get("magnitude", 0.0),
        "timestamp": datetime.now().isoformat()
    }

    print("Sensor data received:")
    print(latest_data)

    return {
        "status": "received",
        "data": latest_data
    }


@app.get("/sensor")
def get_sensor_data():
    return latest_data