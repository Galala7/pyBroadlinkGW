#!/usr/bin/python

from __future__ import print_function

import binascii
import os
import sys

import yaml
import pyrm2

# from pyrm2 import myrm, init_connection, send_command, get_temp, learn_ir

CONFIG_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "config.yml")

rm = None

if os.path.isfile(CONFIG_FILE):
    with open(CONFIG_FILE, 'r') as ymlfile:
        cfg = yaml.load(ymlfile)
        if not cfg:
            cfg = {}
else:
    print("no config.yaml file found, exiting")
    sys.exit()


def record():
    devices = cfg["DEVICES"].keys()
    dev_name = get_choice("Choose device or 'n' add a new device", devices, append=True)
    if dev_name in devices:
        # update known device
        commands = cfg["DEVICES"][dev_name].keys()
    else:
        # print("Enter command name: ", end="")
        # command = raw_input().upper()
        commands = []
    command = get_choice("Choose command to update or 'n' for new command", commands,
                         append=True)

    ir_packet = binascii.hexlify(rm.learn_ir())

    if dev_name in devices:
        cfg["DEVICES"][dev_name][command] = ir_packet
    else:
        cfg["DEVICES"][dev_name] = {command: ir_packet}

    print("Saving command {0} for device {1}\n".format(command, dev_name))


def play():
    devices = cfg["DEVICES"].keys()
    dev_name = get_choice("Choose device number or 'q' to quit", devices)

    commands = cfg["DEVICES"][dev_name].keys()
    command = get_choice("Choose command to send to {0}".format(dev_name.title()), commands)

    ir_packet = binascii.unhexlify(cfg["DEVICES"][dev_name][command])
    rm.send_command(ir_packet)


def display_temp():
    print("Current temperatura is {0} degrees.\n".format(rm.get_temp()))


def my_exit():
    with open(CONFIG_FILE, 'w') as ymlfile:
        yaml.dump(cfg, ymlfile)
    sys.exit()


def get_choice(text, choices, append=False, quit_func=my_exit):
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


def menu():
    mainMenuOptions = {"Get Temperature": display_temp,
                       "Learn new command": record,
                       "Play": play
                       }

    while True:
        choice = get_choice("Broadlink connector", mainMenuOptions.keys())
        mainMenuOptions[choice]()


if __name__ == '__main__':
    rm = pyrm2.myrm()
    menu()
    # mainMenu.open()
