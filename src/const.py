VERSION = "v1.0.10"

OAUTH_URL = "https://volvoid.eu.volvocars.com/as/token.oauth2"
VEHICLES_URL = "https://api.volvocars.com/connected-vehicle/v1/vehicles"
VEHICLE_DETAILS_URL = "https://api.volvocars.com/connected-vehicle/v1/vehicles/{0}"
WINDOW_STATUS_URL = "https://api.volvocars.com/connected-vehicle/v1/vehicles/{0}/windows"
CLIMATE_START_URL = "https://api.volvocars.com/connected-vehicle/v2/vehicles/{0}/commands/climatization-start"
CLIMATE_STOP_URL = "https://api.volvocars.com/connected-vehicle/v2/vehicles/{0}/commands/climatization-stop"
CAR_LOCK_STATE_URL = "https://api.volvocars.com/connected-vehicle/v2/vehicles/{0}/doors"
CAR_LOCK_URL = "https://api.volvocars.com/connected-vehicle/v2/vehicles/{0}/commands/lock"
CAR_UNLOCK_URL = "https://api.volvocars.com/connected-vehicle/v2/vehicles/{0}/commands/unlock"
RECHARGE_STATUS_URL = "https://api.volvocars.com/energy/v1/vehicles/{0}/recharge-status"

charging_system_states = {"CHARGING_SYSTEM_CHARGING": "Charging", "CHARGING_SYSTEM_IDLE": "Idle",
                          "CHARGING_SYSTEM_FAULT": "Fault", "CHARGING_SYSTEM_UNSPECIFIED": "Unspecified"}

supported_sensors = [
                        {"name": "Battery Charge Level", "id": "battery_charge_level", "unit": "%", "icon": "car-battery", "url": RECHARGE_STATUS_URL},
                        {"name": "Electric Range", "id": "electric_range", "unit": "km", "icon": "map-marker-distance", "url": RECHARGE_STATUS_URL},
                        {"name": "Estimated Charging Time", "id": "estimated_charging_time", "unit": "minutes", "icon": "timer-sync-outline", "url": RECHARGE_STATUS_URL},
                        {"name": "Charging System Status", "id": "charging_system_status", "icon": "ev-plug-ccs2", "url": RECHARGE_STATUS_URL},
                        {"name": "Estimated Charging Finish Time", "id": "estimated_charging_finish_time", "icon": "timer-sync-outline", "url": RECHARGE_STATUS_URL},
                        {"name": "Last Data Update", "id": "last_data_update", "icon": "timer", "url": ""}
]

supported_switches = [
                        {"name": "Air Conditioning", "id": "climate_status", "icon": "air-conditioner"},
]

supported_locks = [
                        {"name": "Lock state", "id": "lock_status", "icon": "lock", "url": CAR_LOCK_STATE_URL}
]

supported_buttons = [
                        {"name": "Update Data", "id": "update_data", "icon": "update", "url": ""}
]