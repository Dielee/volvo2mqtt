import logging
import pytz
import os
from logging import handlers
import sys
from const import units
from config import settings

TZ = None


def setup_logging():
    file_log_handler = logging.handlers.RotatingFileHandler('volvo2mqtt.log', maxBytes=1000000, backupCount=1)
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

