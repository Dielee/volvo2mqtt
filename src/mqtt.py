import time
import paho.mqtt.client as mqtt
import json
import volvo
import util
from threading import Thread, Timer
from datetime import datetime
from babel.dates import format_datetime
from config import settings
from const import CLIMATE_START_URL, CLIMATE_STOP_URL, CAR_LOCK_URL, \
            CAR_UNLOCK_URL, availability_topic


mqtt_client: mqtt.Client
subscribed_topics = []
assumed_climate_state = {}
last_data_update = None
climate_timer = {}
door_status = {}


def connect():
    client = mqtt.Client("volvoAAOS2mqtt")
    client.will_set(availability_topic, "offline", 0, False)
    if settings["mqtt"]["username"] and settings["mqtt"]["password"]:
        client.username_pw_set(settings["mqtt"]["username"], settings["mqtt"]["password"])
    port = 1883
    if util.keys_exists(settings["mqtt"], "port"):
        conf_port = settings["mqtt"]["port"]
        if isinstance(conf_port, int):
            if conf_port > 0:
                port = settings["mqtt"]["port"]
    client.connect(settings["mqtt"]["broker"], port)
    client.loop_start()
    client.on_message = on_message
    client.on_disconnect = on_disconnect
    client.on_connect = on_connect

    global mqtt_client
    mqtt_client = client


def on_connect(client, userdata, flags, rc):
    send_heartbeat()
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
        global assumed_climate_state, climate_timer, door_status
        if payload == "ON":
            # Start the api call in another thread for HA performance
            Thread(target=volvo.api_call, args=(CLIMATE_START_URL, "POST", vin)).start()

            # Start door check thread to turn off climate if driver door is opened
            door_thread = Thread(target=volvo.check_door_status, args=(vin, ))
            door_thread.start()
            door_status[vin] = door_thread
            # Starting timer to disable climate after 30 mins

            climate_timer[vin] = Timer(30 * 60, volvo.disable_climate, (vin, ))
            climate_timer[vin].start()
            # Set and update switch status

            assumed_climate_state[vin] = "ON"
            update_car_data()
        elif payload == "OFF":
            # Start the api call in another thread for HA performance
            Thread(target=volvo.api_call, args=(CLIMATE_STOP_URL, "POST", vin)).start()

            # Stop door check thread if running
            if door_status[vin].is_alive():
                door_status[vin].do_run = False

            # Stop climate timer if active
            if climate_timer[vin].is_alive():
                climate_timer[vin].cancel()

            # Set and update switch status
            assumed_climate_state[vin] = "OFF"
            update_car_data()
    elif "lock_status" in msg.topic:
        if payload == "LOCK":
            volvo.api_call(CAR_LOCK_URL, "POST", vin)

            # Force set unlocked state in HA because of slow api response
            update_car_data(True, {"entity_id": "lock_status", "vin": vin, "state": "LOCKED"})
        elif payload == "UNLOCK":
            volvo.api_call(CAR_UNLOCK_URL, "POST", vin)

            # Force set unlocked state in HA because of slow api response
            update_car_data(True, {"entity_id": "lock_status", "vin": vin, "state": "UNLOCKED"})
    elif "update_data" in msg.topic:
        if payload == "PRESS":
            update_car_data(True)


def update_loop():
    create_ha_devices()
    while True:
        print("Sending mqtt update...")
        send_heartbeat()
        update_car_data()
        print("Mqtt update done. Next run in " + str(settings["updateInterval"]) + " seconds.")
        time.sleep(settings["updateInterval"])


def update_car_data(force_update=False, overwrite={}):
    global last_data_update
    last_data_update = format_datetime(datetime.now(util.TZ), format="medium", locale=settings["babelLocale"])
    for vin in volvo.vins:
        for entity in volvo.supported_endpoints[vin]:
            if entity["domain"] == "button":
                continue

            ov_entity_id = ""
            ov_vin = ""
            ov_state = ""
            if bool(overwrite):
                ov_entity_id = overwrite["entity_id"]
                ov_vin = overwrite["vin"]
                ov_state = overwrite["state"]

            if entity["id"] == "climate_status":
                state = assumed_climate_state[vin]
            elif entity["id"] == "last_data_update":
                state = last_data_update
            else:
                if entity["id"] == ov_entity_id and vin == ov_vin:
                    state = ov_state
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
                        "unique_id": f"volvoAAOS2mqtt_{vin}_{entity['id']}",
                        "availability_topic": availability_topic
                    }
            if entity.get("device_class"):
                config["device_class"] = entity["device_class"]

            if entity.get("unit"):
                config["unit_of_measurement"] = entity["unit"]

            if entity.get("domain") == "device_tracker":
                config["json_attributes_topic"] = f"homeassistant/{entity['domain']}/{vin}_{entity['id']}/attributes"

            if entity.get("domain") in ["switch", "lock", "button"]:
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
    send_heartbeat()


def send_heartbeat():
    mqtt_client.publish(availability_topic, "online")
