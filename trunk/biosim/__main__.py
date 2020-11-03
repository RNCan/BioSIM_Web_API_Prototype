'''
Entry point of the biosim module to be run as main. 

@author: M. Fortin and R. Saint-Amant, Canadian Forest Service, August 2020
@copyright: Her Majesty the Queen in right of Canada
'''
from biosim.bsrequest import WeatherGeneratorRequest, NormalsRequest, ModelRequest , AbstractRequest, \
    WeatherGeneratorEpheremalRequest, BioSimRequestException, \
    SimpleModelRequest
from biosim.bsserver import Server
from biosim.bssettings import Settings
from biosim.bsutility import WgoutWrapper, BioSimUtility
from flask import Flask 
from flask.globals import request
from flask.helpers import make_response
from flask.json import jsonify
from waitress import serve
from paste.translogger import TransLogger 


FieldSeparator = ","

def create_app(test_config=None):
    app = Flask(__name__, instance_relative_config=True)
    
            
    @app.route('/BioSimMemoryLoad')
    def biosimMemoryLoad():
        try:
            nbWgouts = len(AbstractRequest.library)
            return str(nbWgouts)
        except Exception as error:
            return make_response(str(error), 500)

    
    @app.route('/BioSimMaxMemory')
    def biosimMaxMemory():
        try:
            return str(AbstractRequest.maxNumberWgoutInstances)
        except Exception as error:
            return make_response(str(error), 500)
    
    
    @app.route('/BioSimMemoryCleanUp')
    def biosimMemoryCleanUp():
        parms = request.args
        try:
            references = parms.get("ref").split()
            AbstractRequest.removeTeleIOObjects(references)
            return "Done"
        except Exception as error:
            return make_response(str(error), 500)
        ### TODO better error handling here

    
    @app.route('/BioSimModelEphemeral')
    def biosimModelEphemeral():
        parms = request.args
        try:
            bioSimRequest = WeatherGeneratorEpheremalRequest(parms)
            outputs = server.processRequest(bioSimRequest)
            if bioSimRequest.isForceClimateGenerationEnabled():
                lastDailyDate = -999                            # means climate is generated even for past dates
            else:
                lastDailyDate = server.lastDailyDate            # means we are using observation
            strOutput = ""
            for i in range(bioSimRequest.n):
                listForThisPlot = []
                for context in outputs.keys():
                    wgout = outputs.get(context)[i]
                    listForThisPlot.append(wgout)
                wgoutWrapper = WgoutWrapper(listForThisPlot, bioSimRequest.getInitialDateYr(), bioSimRequest.getFinalDateYr(), bioSimRequest.getNbRep(), lastDailyDate)
                bioSimRequest.storeWgoutWrapper(wgoutWrapper)
                
            bioSimRequest.weatherGenerated = True
            outputsList = server.doProcessModelRequest(bioSimRequest)
            if bioSimRequest.isJSONFormatRequested():
                mainDict = dict()
                for i in range(bioSimRequest.n):
                    modelOutputWrapper = outputsList[i] 
                    mainDict.__setitem__(i, modelOutputWrapper.parseOutputToDict())
                return jsonify(mainDict)
            else:
                strOutput = ""
                for modelOutputWrapper in outputsList: 
                    strOutput += modelOutputWrapper.parseOutputToString()
                return strOutput 
        except Exception as error:
            if isinstance(error, BioSimRequestException):
                return make_response(str(error), 400)
            return make_response(str(error), 500)
    
    
    @app.route('/BioSimWGEphemeralMode')
    def biosimWGEphemeralMode():
        return biosimModelEphemeral()

    
    @app.route('/BioSimWG')
    def biosimWG():
        parms = request.args
        try:
            bioSimRequest = WeatherGeneratorRequest(parms)
            outputs = server.processRequest(bioSimRequest)
            if bioSimRequest.isForceClimateGenerationEnabled():
                lastDailyDate = -999                            # means climate is generated even for past dates
            else:
                lastDailyDate = server.lastDailyDate            # means we are using observation
            strOutput = ""
            for i in range(bioSimRequest.n):
                listForThisPlot = []
                for context in outputs.keys():
                    wgout = outputs.get(context)[i]
                    listForThisPlot.append(wgout)
                
                strOutput += AbstractRequest.registerTeleIOObjects(listForThisPlot, bioSimRequest.getInitialDateYr(), bioSimRequest.getFinalDateYr(), bioSimRequest.getNbRep(), lastDailyDate) + " "
            return strOutput
        
        except Exception as error:
            if isinstance(error, BioSimRequestException):
                return make_response(str(error), 400)
            return make_response(str(error), 500)

    
    @app.route('/BioSimModelHelp')
    def biosimModelHelp():
        parms = request.args
        try:
            bioSimRequest = SimpleModelRequest(parms)
            modelType = bioSimRequest.mod
            return server.models.get(modelType).getHelp()
        except Exception as error:
            if isinstance(error, BioSimRequestException):
                return make_response(str(error), 400)
            return make_response(str(error), 500)

    
    @app.route('/BioSimModelDefaultParameters')
    def biosimModelDefaultParameters():
        parms = request.args
        try:
            bioSimRequest = SimpleModelRequest(parms)
            modelType = bioSimRequest.mod
            listObject = server.models.get(modelType).getDefaultParameters()
            outputString = ""
            for p in listObject:
                outputString += p + FieldSeparator
            outputString = outputString[0:(len(outputString) - 1)]
            return outputString
        except Exception as error:
            if isinstance(error, BioSimRequestException):
                return make_response(str(error), 400)
            return make_response(str(error), 500)

    
    @app.route('/BioSimMaxCoordinatesPerRequest')
    def MaxCoordinatesPerRequest():
        parms = request.args
        try:
            if parms.get("format", "CSV") == "JSON":
                return jsonify(maxWeatherGeneration = AbstractRequest.nbMaxCoordinatesWG, maxNormals = AbstractRequest.nbMaxCoordinatesNormals)
            else: 
                return str(AbstractRequest.nbMaxCoordinatesWG) + FieldSeparator + str(AbstractRequest.nbMaxCoordinatesNormals)
        except Exception as error:
            return make_response(str(error), 500)
    
    
    @app.route('/BioSimModel')
    def biosimModel():
        parms = request.args
        try:
            bioSimRequest = ModelRequest(parms)
            outputsList = server.processRequest(bioSimRequest)
            if bioSimRequest.isJSONFormatRequested():
                mainDict = dict()
                for i in range(bioSimRequest.n):
                    modelOutputWrapper = outputsList[i] 
                    mainDict.__setitem__(i, modelOutputWrapper.parseOutputToDict())
                return jsonify(mainDict)
            else:
                strOutput = ""
                for modelOutputWrapper in outputsList: 
                    strOutput += modelOutputWrapper.parseOutputToString()
                return strOutput 
        except Exception as error:
            if isinstance(error, BioSimRequestException):
                return make_response(str(error), 400)
            return make_response(str(error), 500)
    
    
    @app.route('/BioSimModelList')
    def biosimModelList():
        parms = request.args
        try:
            modelList = server.models.keys()
            outputList = list()
            for obj in modelList:
                outputList.append(obj.name)
            if parms.get("format", "CSV") == "JSON":
                return jsonify(outputList)
            else:
                outputStr = ""
                for name in outputList:
                    outputStr += name + "\n"
                return outputStr
        except Exception as error:
            return make_response(str(error), 500)

    
    @app.route('/BioSimNormals')
    def biosimNormals():
        parms = request.args
        try:
            bioSimRequest = NormalsRequest(parms)
            outputs = server.processRequest(bioSimRequest)
    
            if bioSimRequest.isJSONFormatRequested():
                mainDict = dict()
                for i in range(bioSimRequest.n):
                    output = outputs[i] 
                    if output.msg == "Success":
                        mainDict.__setitem__(i, BioSimUtility.convertTeleIOTextToList(output.text))
                    else:
                        return output.msg
                return jsonify(mainDict)
            else:        
                strOutput = ""
                for output in outputs:
                    if output.msg == "Success":
                        strOutput += output.text
                    else:
                        strOutput += output.msg
                return strOutput 
        except Exception as error:
            if isinstance(error, BioSimRequestException):
                return make_response(str(error), 400)
            return make_response(str(error), 500)
    return app


if __name__ == "__main__":
    Settings.SimpleMode = False   ### enabling multiprocessing
    print("Name set to " + str(__name__))
    print("Enabling multiprocessing")
    app = create_app()        
    server = Server()                               ### if running in simple mode then there is no multiprocessing
    serve(TransLogger(create_app(), setup_console_handler=True), listen='0.0.0.0:5000', ident="biosim")
elif __name__ == "__biosim__":
    Settings.SimpleMode = True
    print("Name set to " + str(__name__))
    print("Disabling multiprocessing")
    server = Server()        
