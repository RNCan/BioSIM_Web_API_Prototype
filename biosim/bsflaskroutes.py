'''
Routing based on Flask. 

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
from flask.globals import request
from flask.helpers import make_response
from flask.json import jsonify


FieldSeparator = ","


class BsFlaskRoutes():
    
    @staticmethod
    def create_app(test_config=None):
        app = Flask(__name__, instance_relative_config=True)
        
                
        @app.route('/BioSimMemoryLoad')
        def biosimMemoryLoad():
            try:
                nbWgouts = len(BioSimUtility.library)
                return str(nbWgouts)
            except Exception as error:
                return make_response(str(error), 500)
    
        
        @app.route('/BioSimMaxMemory')
        def biosimMaxMemory():
            try:
                return str(BioSimUtility.maxNumberWgoutInstances)
            except Exception as error:
                return make_response(str(error), 500)
        
        
        @app.route('/BioSimMemoryCleanUp')
        def biosimMemoryCleanUp():
            parms = request.args
            try:
                if parms.__contains__("ref"):
                    references = parms.get("ref").split()
                    TeleIODictList.removeTeleIODictList(references)
                    return "Done"
                else:
                    raise BioSimRequestException("A request for a memory cleanup must contain a ref argument!")
            except Exception as error:
                if isinstance(error, BioSimRequestException):
                    return make_response(str(error), 400)
                return make_response(str(error), 500)
    
        
        @app.route('/BioSimModelEphemeral')
        def biosimModelEphemeral():
            parms = request.args
            try:
                bioSimRequest = WeatherGeneratorEpheremalRequest(parms)
                teleIODictList = doWeatherGeneration(bioSimRequest)
                bioSimRequest.storeTeleIODictList(teleIODictList)
                    
                bioSimRequest.weatherGenerated = True
                modelResultTeleIODictList = Server.Instance.doProcessModelRequest(bioSimRequest)
                if bioSimRequest.isJSONFormatRequested():
                    return jsonify(modelResultTeleIODictList.parseToJSON())
                else:
                    return modelResultTeleIODictList.getOutputText()
            except Exception as error:
                if isinstance(error, BioSimRequestException):
                    return make_response(str(error), 400)
                return make_response(str(error), 500)
        
        
        @app.route('/BioSimWGEphemeralMode')
        def biosimWGEphemeralMode():
            return biosimModelEphemeral()
    
        
        def doWeatherGeneration(bioSimRequest : WeatherGeneratorRequest):
            '''
            Perform the weather generation and returns a TeleIODictList instance
            '''
            outputs = Server.Instance.processRequest(bioSimRequest)
            if bioSimRequest.isForceClimateGenerationEnabled():
                outputs.setLastDailyDate(-999)      # means climate is generated even for past dates
            else:
                outputs.setLastDailyDate(Server.Instance.lastDailyDate)     # means we are using observation
            return outputs
        
        
        @app.route('/BioSimWG')
        def biosimWG():
            parms = request.args
            try:
                bioSimRequest = WeatherGeneratorRequest(parms)
                teleIODictList = doWeatherGeneration(bioSimRequest)
                keysToLibrary = teleIODictList.registerTeleIODictList()
                return keysToLibrary
            
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
                return Server.Instance.models.get(modelType).getHelp()
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
                listObject = Server.Instance.models.get(modelType).getDefaultParameters()
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
                    return jsonify(maxWeatherGeneration = Settings.nbMaxCoordinatesWG, maxNormals = Settings.nbMaxCoordinatesNormals)
                else: 
                    return str(Settings.nbMaxCoordinatesWG) + FieldSeparator + str(Settings.nbMaxCoordinatesNormals)
            except Exception as error:
                return make_response(str(error), 500)
        
        
        @app.route('/BioSimModel')
        def biosimModel():
            parms = request.args
            try:
                bioSimRequest = ModelRequest(parms)
                modelResultTeleIODictList = Server.Instance.processRequest(bioSimRequest)
                if bioSimRequest.isJSONFormatRequested():
                    return jsonify(modelResultTeleIODictList.parseToJSON())
                else:
                    return modelResultTeleIODictList.getOutputText()
            except Exception as error:
                if isinstance(error, BioSimRequestException):
                    return make_response(str(error), 400)
                return make_response(str(error), 500)
        
        
        @app.route('/BioSimModelList')
        def biosimModelList():
            parms = request.args
            try:
                modelList = Server.Instance.models.keys()
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
        def biosimNormals():            #### TODO the function needs to be refactored MF20201203
            parms = request.args
            try:
                bioSimRequest = NormalsRequest(parms)
                outputs = Server.Instance.processRequest(bioSimRequest)
        
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
