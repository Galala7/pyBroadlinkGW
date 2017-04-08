#!/usr/bin/python

from flask import Flask, Response
import json
import time
from flask_restful import Resource, Api
import pyrm2
import binascii
import yaml
import os

CONFIG_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "config.yml")

app = Flask(__name__)
api = Api(app)


class Temperature(Resource):
    def get(self):
        return {'Temperature': _RM.get_temp()}


class IRDevice(Resource):
    def get(self, device, ops):
        return self.post(device, ops)

    def post(self, device, ops):
        response = {'status': 'failed'}
        try:
            for op in ops.split('+'):
                ir_packet = binascii.unhexlify(cfg["DEVICES"][device.upper()][op.upper()])
                _RM.send_command(ir_packet)
                response = Response({'status': 'success'}, 200, mimetype='application/json')
                app.logger.debug('Sent code {0} to device {1}'.format(op, device))
                time.sleep(0.1)
        except Exception as e:
            app.logger.error("Error doing command {0} - {1}".format(ops, e))
            pass
        return response


api.add_resource(Temperature, '/get_temp')
api.add_resource(IRDevice, '/<device>/<ops>')

if os.path.isfile(CONFIG_FILE):
    with open(CONFIG_FILE, 'r') as ymlfile:
        cfg = yaml.load(ymlfile)
        if not cfg:
            cfg = {}
else:
    cfg = {}

if __name__ == '__main__':
    _RM = pyrm2.myrm()
    app.run(debug=False, host='0.0.0.0', port=3141)
