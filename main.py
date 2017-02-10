import broadlink
import menu
import sys
import os
import yaml
import time
import base64

CONFIG_FILE = "config.yml"

if os.path.isfile(CONFIG_FILE):
    with open(CONFIG_FILE, 'r') as ymlfile:
        cfg = yaml.load(ymlfile)
        if not cfg:
            cfg = {}
else:
    cfg = {}

myrm = None

a = {"assadas": 12, "dasdas": {
    "dasda": 3
}}


def init_connection():
    print "Connecting to Broadlink RM2 Pro device..."
    devices = broadlink.discover()
    if not devices:
        quit("error!  discover problem")
    if not devices.auth():
        quit("error! can't authenticate")
    print "connected!"
    return devices


def get_temp():
    temp = myrm.check_temperature()
    if type(temp) is None:
        return 100
    print (temp + "\n")
    return temp


def exit():
    with open(CONFIG_FILE, 'w') as ymlfile:
        yaml.dump(cfg, ymlfile)
    sys.exit()


def learn_ir():
    print "Entering learning mode. Transmit IR signal now"
    myrm.enter_learning()
    start_time = time.time()

    ir_packet = None
    while not ir_packet and time.time() < (start_time + 60 * 5):
        ir_packet = myrm.check_data()
        if not ir_packet:
            time.sleep(1)
    return ir_packet


def record():
    print "Enter device name"
    dev_name = raw_input().upper()
    print "Enter command name"
    cmd_name = raw_input().upper()
    ir_packet = base64.encodestring(learn_ir())
    cfg["DEVICES"] = {
        dev_name: {
            cmd_name: ir_packet
        }
    }
    print "Saving command {0} for device {1}".format(cmd_name, dev_name)


def play():
    print "Choose device:"

    devices = cfg["DEVICES"].keys()

    for dev_name, i in enumerate(devices):
        print "{0}. {1}".format(i, dev_name)

    dev_name = int(raw_input())
    commands = cfg["DEVICES"][devices[dev_name]].keys()

    print "choose command:"
    for command, i in enumerate(commands):
        print "{0}. {1}".format(i, command)
    command = int(raw_input())

    ir_packet = base64.decodestring(cfg["DEVICES"][devices[dev_name]][commands[command]])
    myrm.send_data(ir_packet)


mainMenu = menu.Menu("Broadlink connector\n Choose option:")
mainMenu.implicit()

options = [("Get Temperature", get_temp),
           ("Learn new command", record),
           ("Play", play),
           ("Quit", exit),
           ]

mainMenu.addOptions(options)

if __name__ == '__main__':
    myrm = init_connection()

    mainMenu.open()
