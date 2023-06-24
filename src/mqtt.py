import time
import paho.mqtt.client as mqtt
import json
import volvo
from threading import Thread, Timer
from datetime import datetime
from babel.dates import format_datetime
from config import settings
from const import CLIMATE_START_URL, CLIMATE_STOP_URL, CAR_LOCK_URL, \
            CAR_UNLOCK_URL


mqtt_client: mqtt.Client
subscribed_topics = []
assumed_climate_state = {}
last_data_update = None
climate_timer = {}


def connect():
    client = mqtt.Client("volvoAAOS2mqtt")
    if settings["mqtt"]["username"] and settings["mqtt"]["password"]:
        client.username_pw_set(settings["mqtt"]["username"], settings["mqtt"]["password"])
    client.connect(settings["mqtt"]["broker"])
    client.loop_start()
    client.on_message = on_message
    client.on_disconnect = on_disconnect
    client.on_connect = on_connect

    global mqtt_client
    mqtt_client = client


def on_connect(client, userdata, flags, rc):
    if len(subscribed_topics) > 0:
        for topic in subscribed_topics:
            mqtt_client.subscribe(topic)


def on_disconnect(client, userdata,  rc):
    print("MQTT disconnected, reconnecting automatically")


def on_message(client, userdata, msg):
    try:
        vin = msg.topic.split('/')[2].split('_')[0]
    except IndexError:
        print("Error - Cannot get vin from MQTT topic!")
        return None

    payload = msg.payload.decode("UTF-8")
    if "climate_status" in msg.topic:
        global assumed_climate_state, climate_timer
        if payload == "ON":
            api_thread = Thread(target=volvo.api_call, args=(CLIMATE_START_URL, "POST", vin))
            api_thread.start()
            assumed_climate_state[vin] = "ON"
            # Starting timer to disable climate after 30 mins
            climate_timer[vin] = Timer(30 * 60, volvo.disable_climate, (vin, ))
            climate_timer[vin].start()
            update_car_data()
        elif payload == "OFF":
            api_thread = Thread(target=volvo.api_call, args=(CLIMATE_STOP_URL, "POST", vin))
            api_thread.start()
            assumed_climate_state[vin] = "OFF"
            # Stop timer if active
            if climate_timer[vin].is_alive():
                climate_timer[vin].cancel()
            update_car_data()
    elif "lock_status" in msg.topic:
        if payload == "LOCK":
            volvo.api_call(CAR_LOCK_URL, "POST", vin)
            update_car_data(True)
        elif payload == "UNLOCK":
            volvo.api_call(CAR_UNLOCK_URL, "POST", vin)
            update_car_data(True)
    elif "update_data" in msg.topic:
        if payload == "PRESS":
            update_car_data(True)


def update_loop():
    create_ha_devices()
    while True:
        print("Sending mqtt update...")
        update_car_data()
        print("Mqtt update done. Next run in " + str(settings["updateInterval"]) + " seconds.")
        time.sleep(settings["updateInterval"])


def update_car_data(force_update=False):
    global last_data_update
    last_data_update = format_datetime(datetime.now(), format="medium", locale=settings["babelLocale"])
    for vin in volvo.vins:
        for entity in volvo.supported_endpoints[vin]:
            if entity["domain"] == "button":
                continue

            if entity["id"] == "climate_status":
                state = assumed_climate_state[vin]
            elif entity["id"] == "last_data_update":
                state = last_data_update
            else:
                state = volvo.api_call(entity["url"], "GET", vin, entity["id"], force_update)

            if entity["domain"] == "device_tracker":
                topic = f"homeassistant/{entity['domain']}/{vin}_{entity['id']}/attributes"
            else:
                topic = f"homeassistant/{entity['domain']}/{vin}_{entity['id']}/state"

            mqtt_client.publish(
                topic,
                json.dumps(state) if isinstance(state, dict) else state
            )


def create_ha_devices():
    global subscribed_topics
    for vin in volvo.vins:
        device = volvo.get_vehicle_details(vin)
        for entity in volvo.supported_endpoints[vin]:
            config = {
                        "name": entity['name'],
                        "object_id": f"volvo_{vin}_{entity['id']}",
                        "schema": "state",
                        "icon": f"mdi:{entity['icon']}",
                        "state_topic": f"homeassistant/{entity['domain']}/{vin}_{entity['id']}/state",
                        "device": device,
                        "unique_id": f"volvoAAOS2mqtt_{vin}_{entity['id']}"
                    }
            if entity.get('unit'):
                config["unit_of_measurement"] = entity["unit"]

            if entity.get('domain') == "device_tracker":
                config["json_attributes_topic"] = f"homeassistant/{entity['domain']}/{vin}_{entity['id']}/attributes"

            if entity.get('domain') in ["switch", "lock", "button"]:
                command_topic = f"homeassistant/{entity['domain']}/{vin}_{entity['id']}/command"
                config["command_topic"] = command_topic
                subscribed_topics.append(command_topic)
                mqtt_client.subscribe(command_topic)

            mqtt_client.publish(
                f"homeassistant/{entity['domain']}/volvoAAOS2mqtt/{vin}_{entity['id']}/config",
                json.dumps(config),
                retain=True
            )
    time.sleep(2)
