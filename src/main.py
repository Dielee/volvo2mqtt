import logging
from volvo import authorize
from mqtt import update_loop, connect
from const import VERSION
from util import set_tz, setup_logging


if __name__ == '__main__':
    set_tz()
    setup_logging()
    logging.info("Starting volvo2mqtt version " + VERSION)
    authorize()
    connect()
    update_loop()
