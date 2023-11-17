from config import settings

VERSION = "v1.8.13"

OAUTH_URL = "https://volvoid.eu.volvocars.com/as/token.oauth2"
VEHICLES_URL = "https://api.volvocars.com/connected-vehicle/v1/vehicles"
VEHICLE_DETAILS_URL = "https://api.volvocars.com/connected-vehicle/v1/vehicles/{0}"
WINDOWS_STATE_URL = "https://api.volvocars.com/connected-vehicle/v2/vehicles/{0}/windows"
CLIMATE_START_URL = "https://api.volvocars.com/connected-vehicle/v2/vehicles/{0}/commands/climatization-start"
CLIMATE_STOP_URL = "https://api.volvocars.com/connected-vehicle/v2/vehicles/{0}/commands/climatization-stop"
LOCK_STATE_URL = "https://api.volvocars.com/connected-vehicle/v2/vehicles/{0}/doors"
CAR_LOCK_URL = "https://api.volvocars.com/connected-vehicle/v2/vehicles/{0}/commands/lock"
CAR_UNLOCK_URL = "https://api.volvocars.com/connected-vehicle/v2/vehicles/{0}/commands/unlock"
RECHARGE_STATE_URL = "https://api.volvocars.com/energy/v1/vehicles/{0}/recharge-status"
ODOMETER_STATE_URL = "https://api.volvocars.com/connected-vehicle/v2/vehicles/{0}/odometer"
LOCATION_STATE_URL = "https://api.volvocars.com/location/v1/vehicles/{0}/location"
TYRE_STATE_URL = "https://api.volvocars.com/connected-vehicle/v2/vehicles/{0}/tyres"
ENGINE_STATE_URL = "https://api.volvocars.com/connected-vehicle/v2/vehicles/{0}/engine-status"
BATTERY_CHARGE_STATE_URL = "https://api.volvocars.com/connected-vehicle/v1/vehicles/{0}/battery-charge-level"
FUEL_STATE_URL = "https://api.volvocars.com/connected-vehicle/v2/vehicles/{0}/fuel"
STATISTICS_URL = "https://api.volvocars.com/connected-vehicle/v2/vehicles/{0}/statistics"
ENGINE_DIAGNOSTICS_URL = "https://api.volvocars.com/connected-vehicle/v2/vehicles/{0}/engine"
VEHICLE_DIAGNOSTICS_URL = "https://api.volvocars.com/connected-vehicle/v2/vehicles/{0}/diagnostics"

units = {
            "en_GB": {
                "divider": 1.60934,
                "electric_range": {"unit": "mi"},
                "odometer": {"unit": "mi"},
                "average_speed": {"unit": "mph"},
                "distance_to_empty": {"unit": "mi"},
                "distance_to_service": {"unit": "mi"}
            },
            "en_US": {
                "divider": 1.60934,
                "electric_range": {"unit": "mi"},
                "odometer": {"unit": "mi"},
                "average_speed": {"unit": "mph"},
                "distance_to_empty": {"unit": "mi"},
                "distance_to_service": {"unit": "mi"}
            }
        }

availability_topic = "volvoAAOS2mqtt/availability"

charging_system_states = {"CHARGING_SYSTEM_CHARGING": "Charging", "CHARGING_SYSTEM_IDLE": "Idle",
                          "CHARGING_SYSTEM_FAULT": "Fault", "CHARGING_SYSTEM_UNSPECIFIED": "Unspecified"}

charging_connection_states = {"CONNECTION_STATUS_DISCONNECTED": "Disconnected", "CONNECTION_STATUS_UNSPECIFIED": "Unspecified",
                              "CONNECTION_STATUS_CONNECTED_DC": "Connected DC", "CONNECTION_STATUS_CONNECTED_AC": "Connected AC",
                              "CONNECTION_STATUS_FAULT": "Fault"}

window_states = {"CLOSED": "OFF", "OPEN": "ON", "AJAR": "ON"}
door_states = {"CLOSED": "OFF", "OPEN": "ON", "UNSPECIFIED": "UNKNOWN", "AJAR": "ON"}
engine_states = {"RUNNING": "ON", "STOPPED": "OFF", "true": "ON", "false": "OFF"}

icon_states = {
    "lock_status": {"UNLOCKED": "lock-open-alert", "LOCKED": "lock", "UNLOCKING": "lock-reset", "LOCKING": "lock-reset"},
    "door_front_left": {"ON": "car-door", "OFF": "car-door-lock"},
    "door_front_right": {"ON": "car-door", "OFF": "car-door-lock"},
    "door_rear_left": {"ON": "car-door", "OFF": "car-door-lock"},
    "door_rear_right": {"ON": "car-door", "OFF": "car-door-lock"},
    "engine_state": {"ON": "engine-outline", "OFF": "engine-off-outline"},
    "battery_charge_level": [
                    {"from": 100, "to": 100, "icon": "battery"},
                    {"from": 99, "to": 90, "icon": "battery-90"},
                    {"from": 89, "to": 80, "icon": "battery-80"},
                    {"from": 79, "to": 70, "icon": "battery-70"},
                    {"from": 69, "to": 60, "icon": "battery-60"},
                    {"from": 59, "to": 50, "icon": "battery-50"},
                    {"from": 49, "to": 40, "icon": "battery-40"},
                    {"from": 39, "to": 30, "icon": "battery-30"},
                    {"from": 29, "to": 20, "icon": "battery-20"},
                    {"from": 19, "to": 10, "icon": "battery-10"},
                    {"from": 9, "to": 0, "icon": "battery-alert-variant-outline"},
    ]
}

supported_entities = [
                        {"name": "Battery Charge Level", "domain": "sensor", "device_class": "battery", "id": "battery_charge_level", "unit": "%", "icon": "car-battery", "url": RECHARGE_STATE_URL, "state_class": "measurement"},
                        {"name": "Battery Charge Level", "domain": "sensor", "device_class": "battery", "id": "battery_charge_level", "unit": "%", "icon": "car-battery", "url": BATTERY_CHARGE_STATE_URL, "state_class": "measurement"},
                        {"name": "Electric Range", "domain": "sensor", "id": "electric_range", "unit": "km" if not units.get(settings["babelLocale"]) else units[settings["babelLocale"]]["electric_range"]["unit"], "icon": "map-marker-distance", "url": RECHARGE_STATE_URL, "state_class": "measurement"},
                        {"name": "Estimated Charging Time", "domain": "sensor", "id": "estimated_charging_time", "unit": "minutes", "icon": "timer-sync-outline", "url": RECHARGE_STATE_URL, "state_class": "measurement"},
                        {"name": "Charging System Status", "domain": "sensor", "id": "charging_system_status", "icon": "ev-station", "url": RECHARGE_STATE_URL},
                        {"name": "Charging Connection Status", "domain": "sensor", "id": "charging_connection_status", "icon": "ev-plug-ccs2", "url": RECHARGE_STATE_URL},
                        {"name": "Estimated Charging Finish Time", "domain": "sensor", "id": "estimated_charging_finish_time", "icon": "timer-sync-outline", "url": RECHARGE_STATE_URL},
                        {"name": "Odometer", "domain": "sensor", "id": "odometer", "unit": "km" if not units.get(settings["babelLocale"]) else units[settings["babelLocale"]]["odometer"]["unit"], "icon": "counter", "url": ODOMETER_STATE_URL, "state_class":"total_increasing"},
                        {"name": "Last Data Update", "domain": "sensor", "id": "last_data_update", "icon": "timer", "url": ""},
                        {"name": "Active schedules", "domain": "sensor", "id": "active_schedules", "icon": "timer", "url": ""},
                        {"name": "Window Front Left", "domain": "binary_sensor", "device_class": "window", "id": "window_front_left", "icon": "car-door-lock", "url": WINDOWS_STATE_URL},
                        {"name": "Window Front Right", "domain": "binary_sensor", "device_class": "window", "id": "window_front_right", "icon": "car-door-lock", "url": WINDOWS_STATE_URL},
                        {"name": "Window Rear Left", "domain": "binary_sensor", "device_class": "window", "id": "window_rear_left", "icon": "car-door-lock", "url": WINDOWS_STATE_URL},
                        {"name": "Window Rear Right", "domain": "binary_sensor", "device_class": "window", "id": "window_rear_right", "icon": "car-door-lock", "url": WINDOWS_STATE_URL},
                        {"name": "Door Front Left", "domain": "binary_sensor", "device_class": "door", "id": "door_front_left", "icon": "car-door-lock", "url": LOCK_STATE_URL},
                        {"name": "Door Front Right", "domain": "binary_sensor", "device_class": "door", "id": "door_front_right", "icon": "car-door-lock", "url": LOCK_STATE_URL},
                        {"name": "Door Rear Left", "domain": "binary_sensor", "device_class": "door", "id": "door_rear_left", "icon": "car-door-lock", "url": LOCK_STATE_URL},
                        {"name": "Door Rear Right", "domain": "binary_sensor", "device_class": "door", "id": "door_rear_right", "icon": "car-door-lock", "url": LOCK_STATE_URL},
                        {"name": "Tailgate", "domain": "binary_sensor", "device_class": "door", "id": "tailgate", "icon": "car-door-lock", "url": LOCK_STATE_URL},
                        {"name": "Engine Hood", "domain": "binary_sensor", "device_class": "door", "id": "engine_hood", "icon": "car-door-lock", "url": LOCK_STATE_URL},
                        {"name": "Tank Lid", "domain": "binary_sensor", "device_class": "door", "id": "tank_lid", "icon": "car-door-lock", "url": LOCK_STATE_URL},
                        {"name": "Sunroof", "domain": "binary_sensor", "device_class": "door", "id": "sunroof", "icon": "car-door-lock", "url": WINDOWS_STATE_URL},
                        {"name": "Air Conditioning", "domain": "switch", "id": "climate_status", "icon": "air-conditioner"},
                        {"name": "Lock state", "domain": "lock", "id": "lock_status", "icon": "lock", "url": LOCK_STATE_URL},
                        {"name": "Force Update Data", "domain": "button", "id": "update_data", "icon": "update", "url": ""},
                        {"name": "Location", "domain": "device_tracker", "id": "location", "icon": "map-marker-radius", "url": LOCATION_STATE_URL},
                        {"name": "Tire Front Left", "domain": "sensor", "id": "tyre_front_left", "icon": "car-tire-alert", "url": TYRE_STATE_URL},
                        {"name": "Tire Front Right", "domain": "sensor", "id": "tyre_front_right", "icon": "car-tire-alert", "url": TYRE_STATE_URL},
                        {"name": "Tire Rear Left", "domain": "sensor", "id": "tyre_rear_left", "icon": "car-tire-alert", "url": TYRE_STATE_URL},
                        {"name": "Tire Rear Right", "domain": "sensor", "id": "tyre_rear_right", "icon": "car-tire-alert", "url": TYRE_STATE_URL},
                        {"name": "Engine State", "domain": "binary_sensor", "device_class": "running", "id": "engine_state", "icon": "engine", "url": ENGINE_STATE_URL},
                        {"name": "Fuel Level", "domain": "sensor", "id": "fuel_level", "unit": "liters", "icon": "fuel", "url": FUEL_STATE_URL, "state_class": "measurement"},
                        {"name": "Average Fuel Consumption", "domain": "sensor", "id": "average_fuel_consumption", "unit": "liters", "icon": "fuel", "url": STATISTICS_URL},
                        {"name": "Distance to Empty", "domain": "sensor", "id": "distance_to_empty", "unit": "km" if not units.get(settings["babelLocale"]) else units[settings["babelLocale"]]["distance_to_empty"]["unit"], "icon": "map-marker-distance", "url": STATISTICS_URL, "state_class": "measurement"},
                        {"name": "Average Speed", "domain": "sensor", "id": "average_speed", "unit": "km/h" if not units.get(settings["babelLocale"]) else units[settings["babelLocale"]]["average_speed"]["unit"], "icon": "speedometer", "url": STATISTICS_URL, "state_class": "measurement"},
                        {"name": "Hours to Service", "domain": "sensor", "id": "hours_to_service", "unit": "hour", "icon": "wrench-clock", "url": VEHICLE_DIAGNOSTICS_URL},
                        {"name": "Distance to Service", "domain": "sensor", "id": "km_to_service", "unit": "km" if not units.get(settings["babelLocale"]) else units[settings["babelLocale"]]["distance_to_service"]["unit"], "icon": "wrench-clock", "url": VEHICLE_DIAGNOSTICS_URL},
                        {"name": "Time to Service", "domain": "sensor", "id": "time_to_service", "icon": "wrench-clock", "url": VEHICLE_DIAGNOSTICS_URL},
                        {"name": "Service warning status", "domain": "sensor", "id": "service_warning_status", "icon": "alert-outline", "url": VEHICLE_DIAGNOSTICS_URL},
                        {"name": "Service warning trigger", "domain": "sensor", "id": "service_warning_trigger", "icon": "alert-outline", "url": VEHICLE_DIAGNOSTICS_URL}
]

old_entity_ids = ["months_to_service"]
