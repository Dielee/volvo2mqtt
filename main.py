from volvo import authorize
from mqtt import update_loop, connect
from const import VERSION

if __name__ == '__main__':
    print("Starting volvo2mqtt version " + VERSION)
    authorize()
    connect()
    update_loop()
