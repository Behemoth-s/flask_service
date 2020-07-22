from flask import Flask
from flask_restful import Api
import logging
import os
import sys
import json

# set logger
logging.basicConfig(filename='C:\\Temp\\flask_service.log', level=logging.DEBUG,
                    format='[flaskapp] %(levelname)-7.7s %(message)s')

# create app
app = Flask(__name__)
# create api
api = Api(app)


# load custom config
def resource_path(relative_path):
    """ Get absolute path to resource, works for dev and for PyInstaller """
    try:
        # PyInstaller creates a temp folder and stores path in _MEIPASS
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.environ.get("_MEIPASS2", os.path.abspath("."))
    return os.path.join(base_path, relative_path)


custom_config_file = resource_path('custom_config.json')
if os.path.isfile(custom_config_file):
    app.logger.info('load custom config from file {}'.format(custom_config_file))
    custom_config = json.load(open(resource_path('custom_config.json')))
else:
    app.logger.error('custom config file {} not found'.format(custom_config_file))
    custom_config = {}
