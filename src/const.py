from config import settings

VERSION = "v1.1.2"

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

charging_system_states = {"CHARGING_SYSTEM_CHARGING": "Charging", "CHARGING_SYSTEM_IDLE": "Idle",
                          "CHARGING_SYSTEM_FAULT": "Fault", "CHARGING_SYSTEM_UNSPECIFIED": "Unspecified"}

supported_sensors = [
                        {"name": "Battery Charge Level", "id": "battery_charge_level", "unit": "%", "icon": "car-battery", "url": RECHARGE_STATE_URL},
                        {"name": "Electric Range", "id": "electric_range", "unit": "km" if settings["babelLocale"] != "en_US" else "mi", "icon": "map-marker-distance", "url": RECHARGE_STATE_URL},
                        {"name": "Estimated Charging Time", "id": "estimated_charging_time", "unit": "minutes", "icon": "timer-sync-outline", "url": RECHARGE_STATE_URL},
                        {"name": "Charging System Status", "id": "charging_system_status", "icon": "ev-plug-ccs2", "url": RECHARGE_STATE_URL},
                        {"name": "Estimated Charging Finish Time", "id": "estimated_charging_finish_time", "icon": "timer-sync-outline", "url": RECHARGE_STATE_URL},
                        {"name": "Odometer", "id": "odometer", "unit": "km" if settings["babelLocale"] != "en_US" else "mi", "icon": "counter", "url": ODOMETER_STATE_URL},
                        {"name": "Last Data Update", "id": "last_data_update", "icon": "timer", "url": ""},
                        {"name": "Window Front Left", "id": "window_front_left", "icon": "car-door-lock", "url": WINDOWS_STATE_URL},
                        {"name": "Window Front Right", "id": "window_front_right", "icon": "car-door-lock", "url": WINDOWS_STATE_URL},
                        {"name": "Window Rear Left", "id": "window_rear_left", "icon": "car-door-lock", "url": WINDOWS_STATE_URL},
                        {"name": "Window Rear Right", "id": "window_rear_right", "icon": "car-door-lock", "url": WINDOWS_STATE_URL},
                        {"name": "Door Front Left", "id": "door_front_left", "icon": "car-door-lock", "url": LOCK_STATE_URL},
                        {"name": "Door Front Right", "id": "door_front_right", "icon": "car-door-lock", "url": LOCK_STATE_URL},
                        {"name": "Door Rear Left", "id": "door_rear_left", "icon": "car-door-lock", "url": LOCK_STATE_URL},
                        {"name": "Door Rear Right", "id": "door_rear_right", "icon": "car-door-lock", "url": LOCK_STATE_URL},
                        {"name": "Tailgate", "id": "tailgate", "icon": "car-door-lock", "url": LOCK_STATE_URL},
                        {"name": "Engine Hood", "id": "engine_hood", "icon": "car-door-lock", "url": LOCK_STATE_URL},
                        {"name": "Tank Lid", "id": "tank_lid", "icon": "car-door-lock", "url": LOCK_STATE_URL}
]

supported_switches = [
                        {"name": "Air Conditioning", "id": "climate_status", "icon": "air-conditioner"},
]

supported_locks = [
                        {"name": "Lock state", "id": "lock_status", "icon": "lock", "url": LOCK_STATE_URL}
]

supported_buttons = [
                        {"name": "Force Update Data", "id": "update_data", "icon": "update", "url": ""}
]
