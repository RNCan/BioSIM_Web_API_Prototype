'''
Entry point of the biosim module. 

@author: M. Fortin and R. Saint-Amant, Canadian Forest Service, August 2020
@copyright: Her Majesty the Queen in right of Canada
'''
from biosim.bsserver import Server
from biosim.bssettings import Settings
from paste.translogger import TransLogger 
from waitress import serve

from biosim.bsflaskroutes import BsFlaskRoutes


if __name__ == "__main__":
    Settings.ProductionMode = True   
    Settings.MultiprocessMode = True
    print("Name set to " + str(__name__))
    print("Multiprocessing set to " + str(Settings.MultiprocessMode))
    Server.InstantiateServer()                               
    serve(TransLogger(BsFlaskRoutes.create_app(), setup_console_handler=True), listen='0.0.0.0:5000', ident="biosim")
    
