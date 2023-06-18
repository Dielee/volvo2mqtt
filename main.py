from volvo import authorize
from mqtt import update_loop, connect

if __name__ == '__main__':
    authorize()
    connect()
    update_loop()
