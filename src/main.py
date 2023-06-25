from volvo import authorize
from mqtt import update_loop, connect
from const import VERSION
from util import set_tz


if __name__ == '__main__':
    print("Starting volvo2mqtt version " + VERSION)
    set_tz()
    authorize()
    connect()
    update_loop()
