import logging
import pytz
import os
import sys
from logging import handlers
from datetime import datetime
from const import units
from config import settings
from pathlib import Path

TZ = None


def get_icon_between(icon_list, state):
    icon = None
    for s in icon_list:
        if s["to"] <= state <= s["from"]:
            icon = s["icon"]
    return icon


def setup_logging():
    log_location = "volvo2mqtt.log"
    if os.environ.get("IS_HA_ADDON"):
        check_existing_folder()
        log_location = "/addons/volvo2mqtt/log/volvo2mqtt.log"

    logging.Formatter.converter = lambda *args: datetime.now(tz=TZ).timetuple()
    file_log_handler = logging.handlers.RotatingFileHandler(log_location, maxBytes=1000000, backupCount=1)
    formatter = logging.Formatter(
        '%(asctime)s volvo2mqtt [%(process)d] - %(levelname)s: %(message)s',
        '%b %d %H:%M:%S')
    file_log_handler.setFormatter(formatter)
    logger = logging.getLogger()

    console_log_handler = logging.StreamHandler(sys.stdout)
    console_log_handler.setFormatter(formatter)

    logger.addHandler(console_log_handler)
    logger.addHandler(file_log_handler)

    logger.setLevel(logging.INFO)
    if "debug" in settings:
        if settings["debug"]:
            logger.setLevel(logging.DEBUG)


def check_existing_folder():
    Path("/addons/volvo2mqtt/log/").mkdir(parents=True, exist_ok=True)


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

