'''
Entry point of the biosim module. 

@author: M. Fortin and R. Saint-Amant, Canadian Forest Service, August 2020
@copyright: Her Majesty the Queen in right of Canada
'''
from biosim.bsrequest import WeatherGeneratorRequest, NormalsRequest, ModelRequest , \
    WeatherGeneratorEpheremalRequest, BioSimRequestException, \
    SimpleModelRequest, TeleIODictList
from biosim.bsserver import Server
from biosim.bssettings import Settings
from biosim.bsutility import BioSimUtility
from flask import Flask 
import flask
from flask.globals import request
from flask.helpers import make_response
from flask.json import jsonify
from paste.translogger import TransLogger 
from waitress import serve

from biosim.bsflaskroutes import BsFlaskRoutes

if __name__ == "__main__":
    print("Name set to " + str(__name__))
    app = BsFlaskRoutes.create_app()                
    url = "0.0.0.0:" + str(app.config["PORT"])
    serve(TransLogger(app, setup_console_handler=True), listen=url, ident="BioSIM web API") 
elif __name__ == "__biosim__":
    print("Name set to " + str(__name__))
    app = BsFlaskRoutes.create_app(allowEnvironmentalSettings=False)       ## to make sure it does not work in multiprocess         
    url = "0.0.0.0:" + str(app.config["PORT"])
    serve(TransLogger(app, setup_console_handler=True), listen=url, ident="BioSIM web API") 
