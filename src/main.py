import logging
from volvo import authorize
from mqtt import update_loop, connect
from const import VERSION
from util import set_tz, setup_logging, set_mqtt_settings, validate_settings


if __name__ == '__main__':
    setup_logging()
    logging.info("Starting volvo2mqtt version " + VERSION)
    validate_settings()
    set_tz()
    set_mqtt_settings()
    connect()
    authorize()
    update_loop()
