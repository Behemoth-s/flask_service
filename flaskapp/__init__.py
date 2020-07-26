from flask import Flask
from flask_restful import Api
import logging

# set logger
logging.basicConfig(filename='C:\\Temp\\flask-service.log', level=logging.DEBUG,
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
# create app
app = Flask(__name__)

# create api
api = Api(app)
