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
    Settings.ProductionMode = False   
    Settings.MultiprocessMode = False
    print("Name set to " + str(__name__))
    print("Multiprocessing set to " + str(Settings.MultiprocessMode))
    Server.InstantiateServer()                               
    serve(TransLogger(BsFlaskRoutes.create_app(), setup_console_handler=True), listen='0.0.0.0:5001', ident="biosim")
elif __name__ == "__biosim__":
    Settings.ProductionMode = False   
    Settings.MultiprocessMode = False
    print("Name set to " + str(__name__))
    print("Multiprocessing set to " + str(Settings.MultiprocessMode))
    Server.InstantiateServer()                               
