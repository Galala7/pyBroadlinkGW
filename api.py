from flask import Flask, Response
import json
import time
from flask_restful import Resource, Api
from pyrm2 import myrm
import binascii
import yaml
import os

app = Flask(__name__)
api = Api(app)


class HelloWorld(Resource):
    def get(self):
        return {'hello': 'world'}


class Temperature(Resource):
    def get(self):
        return {'Temperature': _RM.get_temp()}


class IRDevice(Resource):
    def post(self, device, ops):
        response = {'status': 'failed'}
        try:
            for op in ops.split('+'):
                ir_packet = binascii.unhexlify(cfg["DEVICES"][device.upper()][op.upper()])
                _RM.send_command(ir_packet)
                json_string = json.dumps({'status': 'success'})
                response = Response({'status': 'success'}, 200, mimetype='application/json')
                app.logger.debug('Sent code {0} to device {1}'.format(op, device))
                time.sleep(0.1)
        except Exception as e:
            app.logger.error("Error doing command {0} - {1}".format(ops,e))
            pass
        return response


api.add_resource(HelloWorld, '/')
api.add_resource(Temperature, '/get_temp')
api.add_resource(IRDevice, '/<device>/<ops>')

_RM = myrm()
CONFIG_FILE = "config.yml"

if os.path.isfile(CONFIG_FILE):
    with open(CONFIG_FILE, 'r') as ymlfile:
        cfg = yaml.load(ymlfile)
        if not cfg:
            cfg = {}
else:
    cfg = {}

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=3141)
