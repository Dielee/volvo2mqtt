import requests
import mqtt
import util
from datetime import datetime, timedelta
from config import settings
from babel.dates import format_datetime
from const import charging_system_states, charging_connection_states, door_states, window_states, \
    OAUTH_URL, VEHICLES_URL, VEHICLE_DETAILS_URL, RECHARGE_STATE_URL, CLIMATE_START_URL, \
    WINDOWS_STATE_URL, LOCK_STATE_URL, TYRE_STATE_URL, supported_entities, BATTERY_CHARGE_STATE_URL, \
    STATISTICS_URL

session = requests.Session()
session.headers = {
    "vcc-api-key": settings["volvoData"]["vccapikey"],
    "content-type": "application/json",
    "accept": "*/*"
}

token_expires_at: datetime
refresh_token = None
vins = []
supported_endpoints = {}
cached_requests = {}


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
        token_expires_at = datetime.now(util.TZ) + timedelta(seconds=(data["expires_in"] - 30))
        refresh_token = data["refresh_token"]

        get_vehicles()
        check_supported_endpoints()
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
        token_expires_at = datetime.now(util.TZ) + timedelta(seconds=(data["expires_in"] - 30))
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
            error = vehicles.json()
            if util.keys_exists(error["error"], "message"):
                raise Exception(
                    "Error getting vehicles: " + str(vehicles.status_code) + ". " + error["error"]["message"])
            else:
                raise Exception(
                    "Unkown Error getting vehicles: " + str(vehicles.status_code))
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


def check_supported_endpoints():
    global supported_endpoints
    for vin in vins:
        supported_endpoints[vin] = []
        for entity in supported_entities:
            if entity["id"] == "battery_charge_level" and entity["url"] == BATTERY_CHARGE_STATE_URL \
                    and any("battery_charge_level" in d["id"] for d in supported_endpoints[vin]):
                # If battery charge level could be found in recharge-api, skip the second battery charge sensor
                continue

            if entity.get('url'):
                state = api_call(entity["url"], "GET", vin, entity["id"])
            else:
                state = ""

            if state is not None:
                print("Success! " + entity["name"] + " is supported by your vehicle.")
                supported_endpoints[vin].append(entity)
            else:
                print("Failed, " + entity["name"] + " is unfortunately not supported by your vehicle.")


def initialize_climate(vins):
    for vin in vins:
        mqtt.assumed_climate_state[vin] = "OFF"


def disable_climate(vin):
    print("Turning climate off by timer!")
    mqtt.assumed_climate_state[vin] = "OFF"
    mqtt.update_car_data()


def api_call(url, method, vin, sensor_id=None, force_update=False):
    global token_expires_at
    if datetime.now(util.TZ) >= token_expires_at:
        refresh_auth()

    if url in [RECHARGE_STATE_URL, WINDOWS_STATE_URL, LOCK_STATE_URL, TYRE_STATE_URL, STATISTICS_URL]:
        # Minimize API calls for endpoints with multiple values
        response = cached_request(url, method, vin, force_update)
        if response is None:
            # Exception caught while getting data from volvo api, doing nothing
            return None
    elif method == "GET":
        print("Starting " + method + " call against " + url)
        try:
            response = session.get(url.format(vin), timeout=15)
        except requests.exceptions.RequestException as e:
            print("Error getting data: " + str(e))
            return ""
    elif method == "POST":
        print("Starting " + method + " call against " + url)
        try:
            response = session.post(url.format(vin), timeout=20)
        except requests.exceptions.RequestException as e:
            print("Error getting data: " + str(e))
            return ""
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
            mqtt.assumed_climate_state[vin] = "OFF"
            mqtt.update_car_data()
        else:
            print("API Call failed. Status Code: " + str(response.status_code) + ". Error: " + response.text)
        return ""
    return parse_api_data(data, sensor_id)


def cached_request(url, method, vin, force_update=False):
    global cached_requests
    if not util.keys_exists(cached_requests, vin + "_" + url):
        # No API Data cached, get fresh data from API
        print("Starting " + method + " call against " + url)
        try:
            response = session.get(url.format(vin), timeout=15)
        except requests.exceptions.RequestException as e:
            print("Error getting data: " + str(e))
            return None

        data = {"response": response, "last_update": datetime.now(util.TZ)}
        cached_requests[vin + "_" + url] = data
    else:
        if (datetime.now(util.TZ) - cached_requests[vin + "_" + url]["last_update"]).total_seconds() >= settings["updateInterval"] \
                or (force_update and (datetime.now(util.TZ) - cached_requests[vin + "_" + url]["last_update"]).total_seconds() >= 2):
            # Old Data in Cache, or force mode active, updating
            print("Starting " + method + " call against " + url)
            try:
                response = session.get(url.format(vin), timeout=15)
            except requests.exceptions.RequestException as e:
                print("Error getting data: " + str(e))
                return None
            data = {"response": response, "last_update": datetime.now(util.TZ)}
            cached_requests[vin + "_" + url] = data
        else:
            # Data is up do date, returning cached data
            response = cached_requests[vin + "_" + url]["response"]
    return response


def parse_api_data(data, sensor_id=None):
    data = data["data"]
    if sensor_id == "battery_charge_level":
        return data["batteryChargeLevel"]["value"] if util.keys_exists(data, "batteryChargeLevel") else None
    elif sensor_id == "electric_range":
        return data["electricRange"]["value"] if util.keys_exists(data, "electricRange") else None
    elif sensor_id == "charging_system_status":
        return charging_system_states[data["chargingSystemStatus"]["value"]] if util.keys_exists(data,
                                                                                            "chargingSystemStatus") else None
    elif sensor_id == "charging_connection_status":
        return charging_connection_states[data["chargingConnectionStatus"]["value"]] if util.keys_exists(data,
                                                                                                    "chargingConnectionStatus") else None
    elif sensor_id == "estimated_charging_time":
        if util.keys_exists(data, "chargingSystemStatus"):
            charging_system_state = charging_system_states[data["chargingSystemStatus"]["value"]]
            if charging_system_state == "Charging":
                return data["estimatedChargingTime"]["value"] if util.keys_exists(data, "estimatedChargingTime") else ""
            else:
                return 0
        else:
            return None
    elif sensor_id == "estimated_charging_finish_time":
        if util.keys_exists(data, "chargingSystemStatus"):
            charging_system_state = charging_system_states[data["chargingSystemStatus"]["value"]]
            if charging_system_state == "Charging":
                charging_time = int(data["estimatedChargingTime"]["value"] if util.keys_exists(data, "estimatedChargingTime")
                                    else 0)
                charging_finished = datetime.now(util.TZ) + timedelta(minutes=charging_time)
                return format_datetime(charging_finished, format="medium", locale=settings["babelLocale"])
            else:
                return ""
        else:
            return None
    elif sensor_id == "lock_status":
        return data["carLocked"]["value"] if util.keys_exists(data, "carLocked") else None
    elif sensor_id == "odometer":
        multiplier = 1
        if util.keys_exists(settings["volvoData"], "odometerMultiplier"):
            multiplier = settings["volvoData"]["odometerMultiplier"]
            if isinstance(multiplier, str):
                multiplier = 1
            elif multiplier < 1:
                multiplier = 1
        return int(data["odometer"]["value"]) * multiplier if util.keys_exists(data, "odometer") else None
    elif sensor_id == "window_front_left":
        return window_states[data["frontLeftWindowOpen"]["value"]] if util.keys_exists(data, "frontLeftWindowOpen") \
            else None
    elif sensor_id == "window_front_right":
        return window_states[data["frontRightWindowOpen"]["value"]] if util.keys_exists(data, "frontRightWindowOpen") \
            else None
    elif sensor_id == "window_rear_left":
        return window_states[data["rearLeftWindowOpen"]["value"]] if util.keys_exists(data, "rearLeftWindowOpen") \
            else None
    elif sensor_id == "window_rear_right":
        return window_states[data["rearRightWindowOpen"]["value"]] if util.keys_exists(data, "rearRightWindowOpen") \
            else None
    elif sensor_id == "door_front_left":
        return door_states[data["frontLeftDoorOpen"]["value"]] if util.keys_exists(data, "frontLeftDoorOpen") else None
    elif sensor_id == "door_front_right":
        return door_states[data["frontRightDoorOpen"]["value"]] if util.keys_exists(data, "frontRightDoorOpen") else None
    elif sensor_id == "door_rear_left":
        return door_states[data["rearLeftDoorOpen"]["value"]] if util.keys_exists(data, "rearLeftDoorOpen") else None
    elif sensor_id == "door_rear_right":
        return door_states[data["rearRightDoorOpen"]["value"]] if util.keys_exists(data, "rearRightDoorOpen") else None
    elif sensor_id == "tailgate":
        return door_states[data["tailGateOpen"]["value"]] if util.keys_exists(data, "tailGateOpen") else None
    elif sensor_id == "sunroof":
        return door_states[data["sunRoofOpen"]["value"]] if util.keys_exists(data, "sunRoofOpen") else None
    elif sensor_id == "engine_hood":
        return door_states[data["hoodOpen"]["value"]] if util.keys_exists(data, "hoodOpen") else None
    elif sensor_id == "tank_lid":
        return door_states[data["tankLidOpen"]["value"]] if util.keys_exists(data, "tankLidOpen") else None
    elif sensor_id == "tyre_front_left":
        return data["frontLeftTyrePressure"]["value"] if util.keys_exists(data, "frontLeftTyrePressure") else None
    elif sensor_id == "tyre_front_right":
        return data["frontRightTyrePressure"]["value"] if util.keys_exists(data, "frontRightTyrePressure") else None
    elif sensor_id == "tyre_rear_left":
        return data["rearLeftTyrePressure"]["value"] if util.keys_exists(data, "rearLeftTyrePressure") else None
    elif sensor_id == "tyre_rear_right":
        return data["rearRightTyrePressure"]["value"] if util.keys_exists(data, "rearRightTyrePressure") else None
    elif sensor_id == "engine_state":
        return data["engineRunning"]["value"] if util.keys_exists(data, "engineRunning") else None
    elif sensor_id == "fuel_level":
        if util.keys_exists(data, "fuelAmount"):
            fuel_amount = int(data["fuelAmount"]["value"])
            if fuel_amount > 0:
                return fuel_amount
            else:
                return None
        else:
            return None
    elif sensor_id == "average_fuel_consumption":
        if util.keys_exists(data, "averageFuelConsumption"):
            average_fuel_con = float(data["averageFuelConsumption"]["value"])
            if average_fuel_con > 0:
                multiplier = 1
                if util.keys_exists(settings["volvoData"], "averageFuelConsumptionMultiplier"):
                    multiplier = settings["volvoData"]["averageFuelConsumptionMultiplier"]
                    if isinstance(multiplier, str):
                        multiplier = 1
                    elif multiplier < 1:
                        multiplier = 1
                return average_fuel_con * multiplier
            else:
                return None
        else:
            return None
    elif sensor_id == "average_speed":
        if util.keys_exists(data, "averageSpeed"):
            average_speed = int(data["averageSpeed"]["value"])
            if average_speed > 1:
                divider = 1
                if util.keys_exists(settings["volvoData"], "averageSpeedDivider"):
                    divider = settings["volvoData"]["averageSpeedDivider"]
                    if isinstance(divider, str):
                        divider = 1
                    elif divider < 1:
                        divider = 1
                return average_speed / divider
            else:
                return None
        else:
            return None
    elif sensor_id == "location":
        coordinates = {}
        if util.keys_exists(data, "geometry"):
            raw_data = data["geometry"]
            if util.keys_exists(raw_data, "coordinates"):
                coordinates = {"longitude": raw_data["coordinates"][0],
                               "latitude": raw_data["coordinates"][1],
                               "gps_accuracy": 1}
        return coordinates
    else:
        return None
