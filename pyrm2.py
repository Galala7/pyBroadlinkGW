from __future__ import print_function

import time

import broadlink


class myrm:
    def __init__(self):
        self.myrm = None
        self.init_connection()

    def init_connection(self):
        devices = None
        try:
            print("Connecting to Broadlink RM2 Pro device...")
            devices = broadlink.discover()
            if not devices:
                quit("error!  discover problem")
            if not devices.auth():
                quit("error! can't authenticate")
                # print "connected!"
        except Exception as e:
            print("init failed! {0}".format(e))
            quit()
        self.myrm = devices

    def send_command(self, command):
        """
        sends an ir packet using rm2.
        :param command: binary ir packet to send
        :return: bool. True on success
        """
        for i in xrange(5):
            try:
                self.myrm.send_data(command)
            except Exception as e:
                print("failed sending ir packet, {0} - {1}".format(i, e))
                time.sleep(0.1)
                pass
            else:
                return True
        return False

    def get_temp(self):
        temp = self.myrm.check_temperature()
        start_time = time.time()
        while temp is None and time.time() < start_time + 5:
            time.sleep(0.5)
            temp = self.myrm.check_temperature()
        return temp

    def learn_ir(self):
        print("Entering learning mode.....", end='')
        self.myrm.enter_learning()
        print("Transmit IR signal now!")
        start_time = time.time()

        ir_packet = None
        while not ir_packet and time.time() < (start_time + 60 * 5):
            try:
                ir_packet = self.myrm.check_data()
                if not ir_packet:
                    time.sleep(1)
            except Exception as e:
                print("failed learning ir code, {0}".format(e))
                time.sleep(0.1)
                pass
        return ir_packet
