import paho.mqtt.client
import json
import logging

with open("conf.json", "r", encoding="utf-8") as file:
    config = json.load(file)

broker = config["conf"]["mqtt"]["broker"]
port = config["conf"]["mqtt"]["port"]

def on_connect(client, userdata, flags, reason_code, properties):
    sensors = userdata["sensors"]
    for sensor_id in sensors:
        model = sensors[sensor_id]["model"]
        topic = f"WECC/{model}/{sensor_id}/sensor"
        client.subscribe(topic)
    
def on_message(client, userdata, msg):
    try:
        sensor_id = msg.topic.split("/")[2]
        payload = msg.payload.decode("utf-8")
        data = json.loads(payload)
        measure_time = data["time"].replace(" ", "T")
        pm25 = None
        for sensor in data["data"]:
            if sensor["sensor"] == "pm2_5":
                pm25 = sensor["value"]
                break

        if pm25 is None:
            return
        if pm25 < 0:
            return

        project_control_no = userdata["sensors"][sensor_id]["project_control_no"]

    except Exception as e:
        logging.error(f"MQTT資料處理失敗: {e}")
        return
    
    receive_sensor_data = userdata["receive_sensor_data"]
    receive_sensor_data(project_control_no, pm25, measure_time)

def start_mqtt(sensors, receive_sensor_data):
    client = paho.mqtt.client.Client(
        paho.mqtt.client.CallbackAPIVersion.VERSION2,
        userdata = {
            "sensors": sensors,
            "receive_sensor_data": receive_sensor_data
            }
    )

    client.on_connect = on_connect
    client.on_message = on_message

    client.reconnect_delay_set(min_delay=1, max_delay=60)

    client.connect(broker, port)
    client.loop_forever()