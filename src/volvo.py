import requests
from datetime import datetime, timedelta
import mqtt
from config import settings
from babel.dates import format_datetime
from util import keys_exists
from const import charging_system_states, CLIMATE_START_URL, \
    OAUTH_URL, VEHICLES_URL, VEHICLE_DETAILS_URL, RECHARGE_STATE_URL, \
    WINDOWS_STATE_URL, LOCK_STATE_URL

session = requests.Session()
session.headers = {
                "vcc-api-key": settings["volvoData"]["vccapikey"],
                "content-type": "application/json",
                "accept": "*/*"
}

token_expires_at: datetime
refresh_token = None
vins = []
recharge_cached_api_response = {}
recharge_api_last_update = {}
window_cached_api_response = {}
window_api_last_update = {}
door_cached_api_response = {}
door_api_last_update = {}


def authorize():
    headers = {
                "authorization": "Basic aDRZZjBiOlU4WWtTYlZsNnh3c2c1WVFxWmZyZ1ZtSWFEcGhPc3kxUENhVXNpY1F0bzNUUjVrd2FKc2U0QVpkZ2ZJZmNMeXc=",
                "content-type": "application/x-www-form-urlencoded",
                "accept": "application/json"
    }

    body = {
            "username": settings.volvoData["username"],
            "password": settings.volvoData["password"],
            "grant_type": "password",
            "scope": "openid email profile care_by_volvo:financial_information:invoice:read care_by_volvo:financial_information:payment_method care_by_volvo:subscription:read customer:attributes customer:attributes:write order:attributes vehicle:attributes tsp_customer_api:all conve:brake_status conve:climatization_start_stop conve:command_accessibility conve:commands conve:diagnostics_engine_status conve:diagnostics_workshop conve:doors_status conve:engine_status conve:environment conve:fuel_status conve:honk_flash conve:lock conve:lock_status conve:navigation conve:odometer_status conve:trip_statistics conve:tyre_status conve:unlock conve:vehicle_relation conve:warnings conve:windows_status energy:battery_charge_level energy:charging_connection_status energy:charging_system_status energy:electric_range energy:estimated_charging_time energy:recharge_status vehicle:attributes"
    }
    auth = requests.post(OAUTH_URL, data=body, headers=headers)
    if auth.status_code == 200:
        data = auth.json()
        session.headers.update({'authorization': "Bearer " + data["access_token"]})

        global token_expires_at, refresh_token
        token_expires_at = datetime.now() + timedelta(seconds=(data["expires_in"] - 30))
        refresh_token = data["refresh_token"]

        get_vehicles()
    else:
        message = auth.json()
        raise Exception(message["error_description"])


def refresh_auth():
    print("Refreshing credentials")
    global refresh_token
    headers = {
                "authorization": "Basic aDRZZjBiOlU4WWtTYlZsNnh3c2c1WVFxWmZyZ1ZtSWFEcGhPc3kxUENhVXNpY1F0bzNUUjVrd2FKc2U0QVpkZ2ZJZmNMeXc=",
                "content-type": "application/x-www-form-urlencoded",
                "accept": "application/json"
    }

    body = {
            "grant_type": "refresh_token",
            "refresh_token": refresh_token
    }
    auth = requests.post(OAUTH_URL, data=body, headers=headers)
    if auth.status_code == 200:
        data = auth.json()
        session.headers.update({'authorization': "Bearer " + data["access_token"]})

        global token_expires_at
        token_expires_at = datetime.now() + timedelta(seconds=(data["expires_in"] - 30))
        refresh_token = data["refresh_token"]


def get_vehicles():
    global vins
    if not settings.volvoData["vin"]:
        vehicles = session.get(VEHICLES_URL)
        if vehicles.status_code == 200:
            data = vehicles.json()
            if len(data["data"]) > 0:
                for vehicle in data["data"]:
                    vins.append(vehicle["vin"])
            else:
                raise Exception("No vehicle in account " + settings.volvoData["username"] + " found.")
        else:
            raise Exception("Error getting vehicles: " + str(vehicles.status_code))
    else:
        if isinstance(settings.volvoData["vin"], list):
            # If setting is a list, copy
            vins = settings.volvoData["vin"]
        else:
            # If setting is a string, append to list
            vins.append(settings.volvoData["vin"])

    if len(vins) == 0:
        raise Exception("No vehicle found, exiting application!")
    else:
        initialize_climate(vins)
        print("Vin: " + str(vins) + " found!")


def get_vehicle_details(vin):
    response = session.get(VEHICLE_DETAILS_URL.format(vin), timeout=15)
    if response.status_code == 200:
        data = response.json()["data"]
        if "debug" in settings:
            if settings["debug"]:
                print(response.text)
        device = {
                            "identifiers": [f"volvoAAOS2mqtt_{vin}"],
                            "manufacturer": "Volvo",
                            "model": data['descriptions']['model'],
                            "name": f"{data['descriptions']['model']} ({data['modelYear']}) - {vin}",
                 }
    elif response.status_code == 500 and not settings.volvoData["vin"]:
        # Workaround for some cars that are not returning vehicle details
        device = {
                            "identifiers": [f"volvoAAOS2mqtt_{vin}"],
                            "manufacturer": "Volvo",
                            "model": vin,
                            "name": f"Volvo - {vin}",
                 }
    else:
        raise Exception("Getting vehicle details failed. Status Code: " + str(response.status_code) +
                        ". Error: " + response.text)

    return device


def initialize_climate(vins):
    for vin in vins:
        mqtt.assumed_climate_state[vin] = "OFF"


def disable_climate(vin):
    print("Turning climate off by timer!")
    mqtt.assumed_climate_state[vin] = "OFF"
    mqtt.update_car_data()


def api_call(url, method, vin, sensor_id=None, force_update=False):
    global token_expires_at
    if datetime.now() >= token_expires_at:
        refresh_auth()

    if url == RECHARGE_STATE_URL:
        # Minimize API calls for recharge state
        response = pull_recharge_api(url, method, vin, force_update)
    elif url == WINDOWS_STATE_URL:
        # Minimize API calls for window state
        response = pull_window_api(url, method, vin, force_update)
    elif url == LOCK_STATE_URL:
        # Minimize API calls for door state
        response = pull_door_api(url, method, vin, force_update)
    elif method == "GET":
        print("Starting " + method + " call against " + url)
        response = session.get(url.format(vin), timeout=15)
    elif method == "POST":
        print("Starting " + method + " call against " + url)
        response = session.post(url.format(vin), timeout=20)
    else:
        print("Unkown method posted: " + method + ". Returning nothing")
        return ""

    if response.status_code == 200:
        data = response.json()
        if "debug" in settings:
            if settings["debug"]:
                print(response.text)
    else:
        if url == CLIMATE_START_URL and response.status_code == 503:
            print("Car in use, cannot start pre climatization")
            mqtt.assumed_climate_state = "OFF"
            mqtt.update_car_data()
        else:
            print("API Call failed. Status Code: " + str(response.status_code) + ". Error: " + response.text)
        return ""
    return parse_api_data(data, sensor_id)


def pull_door_api(url, method, vin, force_update=False):
    global door_cached_api_response, door_api_last_update
    if not vin in door_cached_api_response or force_update:
        # No API Data for vin cached, get fresh data from API
        print("Starting " + method + " call against " + url)
        response = session.get(url.format(vin), timeout=15)
        door_cached_api_response[vin] = response
        door_api_last_update[vin] = datetime.now()
    else:
        if (datetime.now() - door_api_last_update[vin]).total_seconds() >= settings["updateInterval"]:
            # Old Data in Cache, updating
            print("Starting " + method + " call against " + url)
            response = session.get(url.format(vin), timeout=15)
            door_cached_api_response[vin] = response
            door_api_last_update[vin] = datetime.now()
        else:
            # Data is up do date, returning cached data
            response = door_cached_api_response[vin]
    return response


def pull_window_api(url, method, vin, force_update=False):
    global window_cached_api_response, window_api_last_update
    if not vin in window_cached_api_response or force_update:
        # No API Data for vin cached, get fresh data from API
        print("Starting " + method + " call against " + url)
        response = session.get(url.format(vin), timeout=15)
        window_cached_api_response[vin] = response
        window_api_last_update[vin] = datetime.now()
    else:
        if (datetime.now() - window_api_last_update[vin]).total_seconds() >= settings["updateInterval"]:
            # Old Data in Cache, updating
            print("Starting " + method + " call against " + url)
            response = session.get(url.format(vin), timeout=15)
            window_cached_api_response[vin] = response
            window_api_last_update[vin] = datetime.now()
        else:
            # Data is up do date, returning cached data
            response = window_cached_api_response[vin]
    return response


def pull_recharge_api(url, method, vin, force_update=False):
    global recharge_cached_api_response, recharge_api_last_update
    if not vin in recharge_cached_api_response or force_update:
        # No API Data for vin cached, get fresh data from API
        print("Starting " + method + " call against " + url)
        response = session.get(url.format(vin), timeout=15)
        recharge_cached_api_response[vin] = response
        recharge_api_last_update[vin] = datetime.now()
    else:
        if (datetime.now() - recharge_api_last_update[vin]).total_seconds() >= settings["updateInterval"]:
            # Old Data in Cache, updating
            print("Starting " + method + " call against " + url)
            response = session.get(url.format(vin), timeout=15)
            recharge_cached_api_response[vin] = response
            recharge_api_last_update[vin] = datetime.now()
        else:
            # Data is up do date, returning cached data
            response = recharge_cached_api_response[vin]
    return response


def parse_api_data(data, sensor_id=None):
    data = data["data"]
    if sensor_id == "battery_charge_level":
        return data["batteryChargeLevel"]["value"] if keys_exists(data, "batteryChargeLevel") else 0
    elif sensor_id == "electric_range":
        return data["electricRange"]["value"] if keys_exists(data, "electricRange") else 0
    elif sensor_id == "charging_system_status":
        return charging_system_states[data["chargingSystemStatus"]["value"]] if keys_exists(data, "chargingSystemStatus") else ""
    elif sensor_id == "estimated_charging_time":
        if keys_exists(data, "chargingSystemStatus"):
            charging_system_state = charging_system_states[data["chargingSystemStatus"]["value"]]
            if charging_system_state == "Charging":
                return data["estimatedChargingTime"]["value"] if keys_exists(data, "estimatedChargingTime") else ""
            else:
                return 0
        else:
            return ""
    elif sensor_id == "estimated_charging_finish_time":
        if keys_exists(data, "chargingSystemStatus"):
            charging_system_state = charging_system_states[data["chargingSystemStatus"]["value"]]
            if charging_system_state == "Charging":
                charging_time = int(data["estimatedChargingTime"]["value"] if keys_exists(data, "estimatedChargingTime")
                                    else 0)
                charging_finished = datetime.now() + timedelta(minutes=charging_time)
                return format_datetime(charging_finished, format="medium", locale=settings["babelLocale"])
            else:
                return ""
        else:
            return ""
    elif sensor_id == "lock_status":
        return data["carLocked"]["value"] if keys_exists(data, "carLocked") else ""
    elif sensor_id == "odometer":
        return data["odometer"]["value"] if keys_exists(data, "odometer") else 0
    elif sensor_id == "window_front_left":
        return data["frontLeftWindowOpen"]["value"] if keys_exists(data, "frontLeftWindowOpen") else ""
    elif sensor_id == "window_front_right":
        return data["frontRightWindowOpen"]["value"] if keys_exists(data, "frontRightWindowOpen") else ""
    elif sensor_id == "window_rear_left":
        return data["rearLeftWindowOpen"]["value"] if keys_exists(data, "rearLeftWindowOpen") else ""
    elif sensor_id == "window_rear_right":
        return data["rearRightWindowOpen"]["value"] if keys_exists(data, "rearRightWindowOpen") else ""
    elif sensor_id == "door_front_left":
        return data["frontLeftDoorOpen"]["value"] if keys_exists(data, "frontLeftDoorOpen") else ""
    elif sensor_id == "door_front_right":
        return data["frontRightDoorOpen"]["value"] if keys_exists(data, "frontRightDoorOpen") else ""
    elif sensor_id == "door_rear_left":
        return data["rearLeftDoorOpen"]["value"] if keys_exists(data, "rearLeftDoorOpen") else ""
    elif sensor_id == "door_rear_right":
        return data["rearRightDoorOpen"]["value"] if keys_exists(data, "rearRightDoorOpen") else ""
    elif sensor_id == "tailgate":
        return data["tailGateOpen"]["value"] if keys_exists(data, "tailGateOpen") else ""
    elif sensor_id == "engine_hood":
        return data["hoodOpen"]["value"] if keys_exists(data, "hoodOpen") else ""
    elif sensor_id == "tank_lid":
        return data["tankLidOpen"]["value"] if keys_exists(data, "tankLidOpen") else ""
    elif sensor_id == "location":
        coordinates = {}
        if keys_exists(data, "geometry"):
            raw_data = data["geometry"]
            if keys_exists(raw_data, "coordinates"):
                coordinates = {"longitude": raw_data["coordinates"][0],
                               "latitude": raw_data["coordinates"][1],
                               "gps_accuracy": 1}
        return coordinates
    else:
        return ""
