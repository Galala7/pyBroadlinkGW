from __future__ import print_function
import broadlink
import menu
import sys
import os
import yaml
import time
import base64
import binascii

CONFIG_FILE = "config.yml"

if os.path.isfile(CONFIG_FILE):
    with open(CONFIG_FILE, 'r') as ymlfile:
        cfg = yaml.load(ymlfile)
        if not cfg:
            cfg = {}
else:
    cfg = {}

myrm = None


def init_connection():
    print("Connecting to Broadlink RM2 Pro device...")
    devices = broadlink.discover()
    if not devices:
        quit("error!  discover problem")
    if not devices.auth():
        quit("error! can't authenticate")
    # print "connected!"
    return devices


def get_temp():
    temp = myrm.check_temperature()

    # retry if needed
    start_time = time.time()
    while temp is None and time.time() < start_time + 5:
        time.sleep(0.5)
        temp = myrm.check_temperature()

    # print (temp + "\n")
    return temp


def exit():
    with open(CONFIG_FILE, 'w') as ymlfile:
        yaml.dump(cfg, ymlfile)
    sys.exit()


def learn_ir():
    print("Entering learning mode.....", end='')
    myrm.enter_learning()
    print("Transmit IR signal now!")
    start_time = time.time()

    ir_packet = None
    while not ir_packet and time.time() < (start_time + 60 * 5):
        ir_packet = myrm.check_data()
        if not ir_packet:
            time.sleep(1)
    return ir_packet


def record():
    devices = cfg["DEVICES"].keys()
    dev_name = get_choice("Choose device number or 'n' add a new device", devices, append=True)
    if dev_name in devices:
        # update known device
        commands = cfg["DEVICES"][dev_name].keys()
        command = get_choice("Choose command update or 'n' for new command{0}".format(dev_name.title()), commands,
                             append=True)
    else:
        print("Enter command name", end="")
        command = raw_input().upper()

    ir_packet = binascii.hexlify(learn_ir())
    # ir_packet = base64.encodestring(learn_ir())

    if dev_name in devices:
        # if cfg["DEVICES"][dev_name].has_key(command):
        #     cfg["DEVICES"][dev_name][command] = ir_packet
        # else:
        cfg["DEVICES"][dev_name][command] = ir_packet
    else:
        cfg["DEVICES"] = {
            dev_name: {
                command: ir_packet
            }
        }
    print("Saving command {0} for device {1}".format(command, dev_name))


def play():
    devices = cfg["DEVICES"].keys()
    dev_name = get_choice("Choose device number or 'q' to quit", devices)

    commands = cfg["DEVICES"][dev_name].keys()
    command = get_choice("Choose command to send to {0}".format(dev_name.title()), commands)

    ir_packet = binascii.unhexlify(cfg["DEVICES"][dev_name][command])
    # ir_packet = base64.decodestring(cfg["DEVICES"][dev_name][command])
    myrm.send_data(ir_packet)


def get_choice(text, choices, append=False, quit_func=exit):
    """

    :param text: str. String to print as title to the options menu
    :param choices: list of str to choose from
    :param append: bool. Should allow entering new value?
    :param quit_func: quit_func. change to False to prevent user from quiting the program
    :return: str
    """

    options = {}
    # Add options
    for i, choice in enumerate(choices):
        options[str(i + 1)] = choice
    # add append option
    if append:
        options["n"] = "Enter New Value"
    # add quit option
    if quit_func:
        options["q"] = "Quit Program"

    choice = ''
    while choice not in options.keys():
        print("\n" + text)
        for i in sorted(options):
            print("{0}. {1}".format(i, options[i]))
        print("Choice number: ", end="")
        choice = raw_input()
        print(choice)
    if append and choice.lower() == "n":
        print("Enter new value: ", end='')
        new_val = raw_input()
        return new_val
    if quit_func and choice.lower() == "q":
        quit_func()
    return options[choice.lower()]


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
