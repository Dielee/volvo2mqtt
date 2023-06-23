from config import settings

VERSION = "v1.3.1"

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
BATTERY_CHARGE_STATE_URL = "https://api.volvocars.com/connected-vehicle/v2/vehicles/{0}/battery-charge-level"
FUEL_STATE_URL = "https://api.volvocars.com/connected-vehicle/v2/vehicles/{0}/fuel"

charging_system_states = {"CHARGING_SYSTEM_CHARGING": "Charging", "CHARGING_SYSTEM_IDLE": "Idle",
                          "CHARGING_SYSTEM_FAULT": "Fault", "CHARGING_SYSTEM_UNSPECIFIED": "Unspecified"}

charging_connection_states = {"CONNECTION_STATUS_DISCONNECTED": "Disconnected", "CONNECTION_STATUS_UNSPECIFIED": "Unspecified",
                              "CONNECTION_STATUS_CONNECTED_DC": "Connected DC", "CONNECTION_STATUS_CONNECTED_AC": "Connected AC"}

supported_entities = [
                        {"name": "Battery Charge Level", "domain": "sensor", "id": "battery_charge_level", "unit": "%", "icon": "car-battery", "url": RECHARGE_STATE_URL},
                        {"name": "Battery Charge Level", "domain": "sensor", "id": "battery_charge_level", "unit": "%", "icon": "car-battery", "url": BATTERY_CHARGE_STATE_URL},
                        {"name": "Electric Range", "domain": "sensor", "id": "electric_range", "unit": "km" if settings["babelLocale"] != "en_US" else "mi", "icon": "map-marker-distance", "url": RECHARGE_STATE_URL},
                        {"name": "Estimated Charging Time", "domain": "sensor", "id": "estimated_charging_time", "unit": "minutes", "icon": "timer-sync-outline", "url": RECHARGE_STATE_URL},
                        {"name": "Charging System Status", "domain": "sensor", "id": "charging_system_status", "icon": "ev-station", "url": RECHARGE_STATE_URL},
                        {"name": "Charging Connection Status", "domain": "sensor", "id": "charging_connection_status", "icon": "ev-plug-ccs2", "url": RECHARGE_STATE_URL},
                        {"name": "Estimated Charging Finish Time", "domain": "sensor", "id": "estimated_charging_finish_time", "icon": "timer-sync-outline", "url": RECHARGE_STATE_URL},
                        {"name": "Odometer", "domain": "sensor", "id": "odometer", "unit": "km" if settings["babelLocale"] != "en_US" else "mi", "icon": "counter", "url": ODOMETER_STATE_URL},
                        {"name": "Last Data Update", "domain": "sensor", "id": "last_data_update", "icon": "timer", "url": ""},
                        {"name": "Window Front Left", "domain": "sensor", "id": "window_front_left", "icon": "car-door-lock", "url": WINDOWS_STATE_URL},
                        {"name": "Window Front Right", "domain": "sensor", "id": "window_front_right", "icon": "car-door-lock", "url": WINDOWS_STATE_URL},
                        {"name": "Window Rear Left", "domain": "sensor", "id": "window_rear_left", "icon": "car-door-lock", "url": WINDOWS_STATE_URL},
                        {"name": "Window Rear Right", "domain": "sensor", "id": "window_rear_right", "icon": "car-door-lock", "url": WINDOWS_STATE_URL},
                        {"name": "Door Front Left", "domain": "sensor", "id": "door_front_left", "icon": "car-door-lock", "url": LOCK_STATE_URL},
                        {"name": "Door Front Right", "domain": "sensor", "id": "door_front_right", "icon": "car-door-lock", "url": LOCK_STATE_URL},
                        {"name": "Door Rear Left", "domain": "sensor", "id": "door_rear_left", "icon": "car-door-lock", "url": LOCK_STATE_URL},
                        {"name": "Door Rear Right", "domain": "sensor", "id": "door_rear_right", "icon": "car-door-lock", "url": LOCK_STATE_URL},
                        {"name": "Tailgate", "domain": "sensor", "id": "tailgate", "icon": "car-door-lock", "url": LOCK_STATE_URL},
                        {"name": "Engine Hood", "domain": "sensor", "id": "engine_hood", "icon": "car-door-lock", "url": LOCK_STATE_URL},
                        {"name": "Tank Lid", "domain": "sensor", "id": "tank_lid", "icon": "car-door-lock", "url": LOCK_STATE_URL},
                        {"name": "Air Conditioning", "domain": "switch", "id": "climate_status", "icon": "air-conditioner"},
                        {"name": "Lock state", "domain": "lock", "id": "lock_status", "icon": "lock", "url": LOCK_STATE_URL},
                        {"name": "Force Update Data", "domain": "button", "id": "update_data", "icon": "update", "url": ""},
                        {"name": "Location", "domain": "device_tracker", "id": "location", "icon": "map-marker-radius", "url": LOCATION_STATE_URL},
                        {"name": "Tire Front Left", "domain": "sensor", "id": "tyre_front_left", "icon": "car-tire-alert", "url": TYRE_STATE_URL},
                        {"name": "Tire Front Right", "domain": "sensor", "id": "tyre_front_right", "icon": "car-tire-alert", "url": TYRE_STATE_URL},
                        {"name": "Tire Rear Left", "domain": "sensor", "id": "tyre_rear_left", "icon": "car-tire-alert", "url": TYRE_STATE_URL},
                        {"name": "Tire Rear Right", "domain": "sensor", "id": "tyre_rear_right", "icon": "car-tire-alert", "url": TYRE_STATE_URL},
                        {"name": "Engine State", "domain": "sensor", "id": "engine_state", "icon": "engine", "url": ENGINE_STATE_URL},
                        {"name": "Fuel Level", "domain": "sensor", "id": "fuel_level", "unit": "liters", "icon": "fuel", "url": FUEL_STATE_URL}
]
