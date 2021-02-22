'''
Entry point of the biosim module. 

@author: M. Fortin and R. Saint-Amant, Canadian Forest Service, August 2020
@copyright: Her Majesty the Queen in right of Canada
'''
from paste.translogger import TransLogger 
from waitress import serve

from biosim.bsflaskroutes import BsFlaskRoutes

if __name__ == "__main__":
    print("Name set to " + str(__name__))
    app = BsFlaskRoutes.create_app()                
    url = "0.0.0.0:" + str(app.config["PORT"])
    serve(TransLogger(app, setup_console_handler=True), listen=url, ident="BioSIM web API") 
