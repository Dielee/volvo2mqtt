import pytz
import os
from config import settings

TZ = None


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
