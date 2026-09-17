import mqtt
import requests
import json
import logging

logging.basicConfig(
    filename="app.log",
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s"
)

with open("conf.json", "r", encoding="utf-8") as file:
    config = json.load(file)
sensors = config["sensors"]


api_url = config["conf"]["api"]["url"]
api_key = config["conf"]["api"]["key"]

def receive_sensor_data(project_control_no, pm25, measure_time):

    data = {
    "projectControlNo": project_control_no,
    "sitePM25": pm25,
    "siteMeasureTime": measure_time
    }

    headers = {
        "Content-Type": "application/json",
        "x-api-key": api_key
    }

    try:
        response = requests.post(
            api_url,
            json=data,
            headers=headers,
            timeout=10
        )

        logging.info(f"API回傳: {response.status_code} {response.text}，上傳的資料: {data}")

    except requests.exceptions.RequestException as e:
        logging.error(f"API連線失敗: {e}")
        return

mqtt.start_mqtt(sensors, receive_sensor_data)