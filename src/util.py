import logging
import pytz
import os
import re
import sys
import config
import json
from google_play_scraper import app
from logging import handlers
from datetime import datetime
from const import units
from config import settings
from pathlib import Path

TZ = None
SENSITIVE_PATTERNS = [
    r"[A-Z0-9]{17}",  # VIN
    r"\d{1,2}\.\d{5,16}",  # Location
    r"[a-z0-9]{32}"  # VCCAPIKEY
]


class SensitiveDataFilter(logging.Filter):
    def __init__(self, patterns=None):
        super().__init__()
        self.patterns = patterns or []

    def filter(self, record: logging.LogRecord) -> bool:
        for pattern in self.patterns:
            record.msg = re.sub(pattern, "<REDACTED>", record.msg)
        return True

def get_volvo_app_version():
    result = app(
        'se.volvo.vcc',
        lang='en',
        country='us'
    )

    if "version" in result:
        return result["version"]
    else:
        return "5.37.0"

def get_token_path():
    token_path = ".token"
    if os.environ.get("IS_HA_ADDON"):
        check_existing_folder("/addons/volvo2mqtt/token/")
        token_path = "/addons/volvo2mqtt/token/.token"

    return token_path

def save_to_json(data, token_path):
    with open(token_path, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=4)

def get_icon_between(icon_list, state):
    icon = None
    for s in icon_list:
        if s["to"] <= state < s["from"]:
            icon = s["icon"]
    return icon


def setup_logging():
    log_location = "volvo2mqtt.log"
    if os.environ.get("IS_HA_ADDON"):
        check_existing_folder("/addons/volvo2mqtt/log/")
        log_location = "/addons/volvo2mqtt/log/volvo2mqtt.log"

    logging.Formatter.converter = lambda *args: datetime.now(tz=TZ).timetuple()
    file_log_handler = logging.handlers.RotatingFileHandler(log_location, maxBytes=1000000, backupCount=1)
    formatter = logging.Formatter(
        '%(asctime)s volvo2mqtt [%(process)d] - %(levelname)s: %(message)s',
        '%b %d %H:%M:%S')
    file_log_handler.setFormatter(formatter)

    if "debug" in settings:
        if settings["debug"]:
            sensitive_data_filter = SensitiveDataFilter(SENSITIVE_PATTERNS)
            file_log_handler.addFilter(sensitive_data_filter)

    console_log_handler = logging.StreamHandler(sys.stdout)
    console_log_handler.setFormatter(formatter)

    logger = logging.getLogger()
    logger.addHandler(console_log_handler)
    logger.addHandler(file_log_handler)
    logging.getLogger("urllib3").setLevel(logging.WARNING)

    logger.setLevel(logging.INFO)
    if "debug" in settings:
        if settings["debug"]:
            logger.setLevel(logging.DEBUG)

    if "disable_logging" in settings:
        if settings["disable_logging"]:
            logger.setLevel(logging.ERROR)


def check_existing_folder(path):
    Path(path).mkdir(parents=True, exist_ok=True)


def keys_exists(element, *keys):
    """"
    Check if *keys (nested) exists in `element` (dict).
    Thanks stackoverflow: https://stackoverflow.com/questions/43491287/elegant-way-to-check-if-a-nested-key-exists-in-a-dict
    """
    if not isinstance(element, dict):
        raise AttributeError('keys_exists() expects dict as first argument.')
    if len(keys) == 0:
        raise AttributeError('keys_exists() expects at least two arguments, one given.')

    _element = element
    for key in keys:
        try:
            _element = _element[key]
        except KeyError:
            return False
    return True


def set_tz():
    global TZ
    env_tz = os.environ.get("TZ")
    settings_tz = settings.get("TZ")
    if env_tz:
        TZ = pytz.timezone(env_tz)
    elif settings_tz:
        TZ = pytz.timezone(settings_tz)
    else:
        raise Exception("No timezone setting found! Please read the README!")


def convert_metric_values(value):
    if keys_exists(units, settings["babelLocale"]):
        divider = units[settings["babelLocale"]]["divider"]
        return round((float(value) / divider), 2)
    else:
        return value


def set_mqtt_settings():
    if os.environ.get("IS_HA_ADDON"):
        if config.settings["mqtt"]["broker"] != "auto_broker" \
                or config.settings["mqtt"]["port"] != "auto_port" \
                or config.settings["mqtt"]["username"] != "auto_user" \
                or config.settings["mqtt"]["password"] != "auto_password":
            # If settings were manually set, use the manually set settings
            return None

        broker_host = os.getenv("MQTTHOST", None)
        broker_port = os.getenv("MQTTPORT", None)
        broker_user = os.getenv("MQTTUSER", None)
        broker_pass = os.getenv("MQTTPASS", None)

        if not broker_host or not broker_port:
            raise Exception("MQTT connection could not be established. Please check if your MQTT Add-On is running!")

        logging.debug("MQTT Credentials - Host " + broker_host + " Port: " + str(broker_port) +
                      " User: " + str(broker_user) + " Pass: " + str(broker_pass))

        config.settings["mqtt"]["broker"] = broker_host
        config.settings["mqtt"]["port"] = broker_port
        config.settings["mqtt"]["username"] = broker_user
        config.settings["mqtt"]["password"] = broker_pass


def validate_settings():
    if not os.environ.get("DEV_MODE"):
        setting_keys = settings.volvoData["vccapikey"]
        if isinstance(setting_keys, list):
            if len(setting_keys) > 3:
                raise Exception("Settings invalid! Maximum allowed vccapikeys are three!")

        update_interval = settings["updateInterval"]
        if update_interval < 60:
            raise Exception("Settings invalid! Minimum allowed update interval is 60 seconds!")
