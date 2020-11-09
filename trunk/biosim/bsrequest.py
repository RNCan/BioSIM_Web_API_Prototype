'''
Different classes  of requests for normals, weather generation and model applications

@author: M. Fortin and R. Saint-Amant, Canadian Forest Service, August 2020
@copyright: Her Majesty the Queen in right of Canada
'''
from collections import OrderedDict
import math
from threading import Lock

from werkzeug.datastructures import ImmutableMultiDict

from biosim.bssettings import Context, ShortNormals, RCP, ClimateModel, ModelType
from biosim.bsutility import WgoutWrapper


typeGenList = ["des", # desaggregated
               "obs", # observed (default)
               "gribs"] # gribs source
typeOutputList = ["h", # hourly
                  "d"] # daily (default)

ticketNumber = int(0)

lock = Lock()

variableList = ["TN", # min air temperature
                "T",  # air temperature
                "TX", # max air temperature
                "P",  # precipitation
                "TD", # temperature dew point
                "H",  # humidity
                "WS", # wind speed
                "WD", # wind direction
                "R",  # solar radiation
                "Z",  # atmospheric pressure
                "S",  # snow precipitation
                "SD", # snow depth accumulation
                "SWE", # snow water equivalent
                "WS2"] # wind speed at 2 m

rcpDict = {"4_5" : RCP.RCP45,
               "8_5" : RCP.RCP85}
    
climModDict = {"Hadley" : ClimateModel.Hadley,
                   "RCM4" : ClimateModel.RCM4,
                   "GCM4" : ClimateModel.GCM4}

formats = ["CSV", "JSON"]

   
    
class AbstractRequest:
    '''
    This is the abstract class for derived requests
    '''
    nbMaxCoordinatesNormals = 50
    nbMaxCoordinatesWG = 10
   
    maxNumberWgoutInstances = 100000;
    
    library = OrderedDict()
    
    
    minLatDeg = float(-90)
    maxLatDeg = float(+90)
    minLongDeg = float(-180)
    maxLongDeg = float(+180)
    minElevM = float(-100)
    maxElevM = float(9000)

    def __init__(self, d : ImmutableMultiDict):
        '''
        Constructor
        '''
        self.areAllParametersThere(d)
        self.dict = self.formatParms(d)
        errorMessage = self.checkParmsValues(self.dict)
        if len(errorMessage) > 0:
            raise BioSimRequestException(errorMessage)



    def areAllParametersThere(self, d : ImmutableMultiDict):    
        """
        Checks if all the required parameters were provided in the request.
        Those are latitude, longitude, and variables of interest.
        @param d a ImmutableMultiDict instance provided by the request
        """
        if d.__contains__("lat"):
            if d.__contains__("long"):
#                if d.__contains__("var"):
                return True
        raise BioSimRequestException("A request must at least include either lat=, long=")
    
    
    def formatParms(self, d : ImmutableMultiDict):    
        """
        Parses the different variable to the proper format
        @param: d a ImmutableMultiDict instance provided by the request
        @return: a new dictionary with updated types 
        @raise BioSimRequestException: if the number of coordinates is inconsistent, if the maximum number of coordinates is exceeded or if some of the parameters could not be parsed
        """
        
        listDoubleParsed = ["lat", "long", "elev"]
        listIntParsed = ["from", "to", "compress", "rep", "nb_nearest_neighbor"]
        errMsg = ""
        newDict = {}
        self.n = None
        
        for key in d:
            try:
                if key in listDoubleParsed:
                    value = d.get(key)
                    args = value.split()
                    length = len(args)
                    if self.n is None:
                        self.n = length
                        self.checkIfNBustsMaxCapacity()
                    elif self.n != length:
                        raise BioSimRequestException("Error: the number of coordinates seems to be inconsistent. Typically more latitudes than longitudes.")  
                    for i in range(length):
                        if key == "elev":       ### special case for elev: a NAN can be passed and then BioSim will rely on the DEM
                            try:
                                args[i] = float(args[i])
                            except:
                                args[i] = float('NaN')
                        else:
                            v = float(args[i])
                            if math.isnan(v):
                                raise Exception("NaN is not accepted for parameter " + key)
                            else:
                                args[i] = v
                    newDict.__setitem__(key, args) 
                elif key in listIntParsed:
                    newDict.__setitem__(key, int(d.get(key))) 
                else:
                    newDict.__setitem__(key, d.get(key)) 
            except BioSimRequestException as err:  ### obvious exception that are immediately thrown
                raise err 
            except:  ### other exception of parsing
                errMsg = self.updateErrMsg(errMsg, "the " + key + " parameter cannot be parsed")
                    
        if errMsg.__len__() > 0:
            raise BioSimRequestException(errMsg)
        else:
            return newDict


    def updateErrMsg(self, errMsg, newMessage):
        if errMsg.__len__() == 0:
            errMsg += "Error: " + newMessage
        else:
            errMsg += ", " + newMessage
        return errMsg    


    def checkParmsValues(self, d : dict):
        errMsg = ""

        latValues = d.get("lat")
        for latValue in latValues:
            if latValue < self.minLatDeg or latValue > self.maxLatDeg:
                errMsg = self.updateErrMsg(errMsg, "the latitude must range between " + str(self.minLatDeg) + " and " + str(self.maxLatDeg))

        longValues = d.get("long")
        for longValue in longValues:
            if longValue < self.minLongDeg or longValue > self.maxLongDeg:
                errMsg = self.updateErrMsg(errMsg, "the longitude must range between " + str(self.minLongDeg) + " and " + str(self.maxLongDeg))
        if d.__contains__("elev"):
            elevValues = d.get("elev")
            for elevValue in elevValues:
                if math.isnan(elevValue):
                    if elevValue < self.minElevM or elevValue > self.maxElevM:
                        errMsg = self.updateErrMsg(errMsg, "the elevation must range between " + str(self.minElevM) + " and " + str(self.maxElevM))    

        if d.__contains__("rcp"):
            rcpString = d.get("rcp")
            if rcpDict.__contains__(rcpString) == False:
                errMsg = self.updateErrMsg(errMsg, "the rcp parameter must be one of the following: " + str(rcpDict.keys()))
            else:
                d.__setitem__("rcp", rcpDict.get(rcpString)) ### replace the rcp parameter by its appropriate enum
        else:
            d.__setitem__("rcp", RCP.RCP45)        ## default value
            
        if d.__contains__("climMod"):
            modString = d.get("climMod")    
            if climModDict.__contains__(modString) == False:
                errMsg = self.updateErrMsg(errMsg, "the climMod parameter must be one of the following: " + str(climModDict.keys()))
            else:
                d.__setitem__("climMod", climModDict.get(modString))
        else:
            d.__setitem__("climMod", ClimateModel.RCM4) ## default value

        if d.__contains__("format"):
            formatString = d.get("format")
            if formatString not in formats:
                errMsg = self.updateErrMsg(errMsg, "the format parameter must be one of the following: " + str(formats)) 
        else:
            d.__setitem__("format", "CSV")  ### default is CSV
            
        return errMsg


    def getRCP(self):
        return self.dict.get("rcp")

    def getClimateModel(self):
        return self.dict.get("climMod")

    def parseRequest(self, i, context : Context):
        requestString = "Latitude=" + str(self.dict.get("lat")[i]) + "&" + "Longitude=" + str(self.dict.get("long")[i]) 
        if (self.dict.__contains__("elev")):
            elevValue = self.dict.get("elev")[i]
            if math.isnan(elevValue) == False:
                requestString += "&Elevation=" + str(elevValue)
        requestString += "&compress=0"  # no compression 
        return requestString


    def isJSONFormatRequested(self):
        if (self.dict.__contains__("format")):
            if self.dict.get("format") == "JSON":
                return True 
        return False
    
    def doesThisContextMatch(self, context : Context):
        return True

    def checkIfNBustsMaxCapacity(self):
        if isinstance(self, NormalsRequest):
            if self.n > AbstractRequest.nbMaxCoordinatesNormals:
                raise BioSimRequestException("The maximum number of coordinates when requesting the normals is limited to " + str(AbstractRequest.nbMaxCoordinatesNormals))
        else: 
            if self.n > AbstractRequest.nbMaxCoordinatesWG:
                raise BioSimRequestException("The maximum number of coordinates in a climate generation request is limited to " + str(AbstractRequest.nbMaxCoordinatesWG))

        
        
        
    @staticmethod
    def registerTeleIOObjects(listForThisPlot, initialDateYr, finalDateYr, nbRep, lastDailyDate):
        lock.acquire()
        wgoutWrapper = WgoutWrapper(listForThisPlot, initialDateYr, finalDateYr, nbRep, lastDailyDate)
        key = hash(wgoutWrapper)
        AbstractRequest.library.__setitem__(str(key), wgoutWrapper);
        while len(AbstractRequest.library) > AbstractRequest.maxNumberWgoutInstances:
            firstkey = next(iter(AbstractRequest.library.keys()))
            del AbstractRequest.library[firstkey]  ## we remove the oldest instances first these are the first instance in the ordered dict
        lock.release()
        return str(key)

    @staticmethod
    def removeTeleIOObjects(references):
        lock.acquire()
        for ref in references:
            if AbstractRequest.library.__contains__(ref):
                del AbstractRequest.library[ref]
        lock.release()
        
    @staticmethod
    def getTeleIOObjects(wgoutHash):
        lock.acquire()
        obj = AbstractRequest.library.get(wgoutHash)
        if obj is not None:
            AbstractRequest.library.move_to_end(wgoutHash, last = True) ### move the object to the end so that it shows it's been recently used
        lock.release()
        return obj;
    
    @staticmethod
    def parseVariableRequestString(variables):
        variablesStr = ""
#        variables = ["TN", "TX", "P"]
        for var in variables:
            variablesStr += var + "+"       ### variables are now separated by a + MF20191107
        variablesStr = variablesStr[0:variablesStr.__len__() - 1]
        return "&Variables=" + variablesStr 

    
    
    
class NormalsRequest(AbstractRequest):
    '''
    A class that handles the request for normals
    '''
    
    periodList = dict()
    for shortNorm in ShortNormals:
        periodList.__setitem__(shortNorm.getBasicString(), shortNorm)


    def areAllParametersThere(self, d:ImmutableMultiDict):
        if AbstractRequest.areAllParametersThere(self, d):
            if d.__contains__("period"):
                return;
        raise BioSimRequestException("A request for normals must at least include either lat=, long=, and period=")


    def checkParmsValues(self, d : dict):
        errMsg = AbstractRequest.checkParmsValues(self, d)

        periodString = d.get("period")  
        if self.periodList.__contains__(periodString) == False:
            errMsg = self.updateErrMsg(errMsg, "the period must be one of the following: " + str(self.periodList.keys()))    
        else:
            d.__setitem__("period", self.periodList.get(periodString))
        return errMsg

    def parseRequest(self, i, context:Context):
        requestString = AbstractRequest.parseRequest(self, i, context)
        requestString += AbstractRequest.parseVariableRequestString(["TN", "TX", "P"])
        return requestString

    def doesThisContextMatch(self, context : Context):
        if context.normals == self.periodList.get(self.dict.get("period")):
            return True
        else:
            return False

    def getShortNormalsEnum(self):
        return self.dict.get("period")
    
    
class SimpleModelRequest(AbstractRequest):
    
    def areAllParametersThere(self, d:ImmutableMultiDict):
        if d.__contains__("model"):
                return;
        raise BioSimRequestException("An SimpleModelRequest must at least include model=")

    def checkParmsValues(self, d:dict):
        self.wgoutsList = [];
        errMsg = ""
        modelName = d.get("model")
        try:
            self.mod = ModelType[modelName]
        except:
            errMsg = self.updateErrMsg(errMsg, "Model " + modelName + " does not exist")
        return errMsg

    def parseRequest(self, i, context : Context):
        requestString = ""
        requestString += "compress=0"  # no compression 
#         if self.dict.__contains__("rep"):
#             requestString += "&Replications=" + str(self.dict.get("rep"))
        if self.dict.__contains__("Parameters"):
            requestString += "&Parameters=" + str(self.dict.get("Parameters")).replace("*","+")  
                                                     
        return requestString
    

class ModelRequest(SimpleModelRequest):
    '''
    A class that handles the request to a particular model 
    '''
    
    def areAllParametersThere(self, d:ImmutableMultiDict):
        SimpleModelRequest.areAllParametersThere(self, d)
        if d.__contains__("wgout"):
            return;
        raise BioSimRequestException("A ModelRequest must at least include contain model= and wgout=")


    def checkParmsValues(self, d:dict):
        errMsg = SimpleModelRequest.checkParmsValues(self, d)
        wgouthash = d.get("wgout")
        wgouts = wgouthash.split()
        self.n = len(wgouts)
        self.checkIfNBustsMaxCapacity()
        for wgout in wgouts:
            teleIOObj = AbstractRequest.getTeleIOObjects(wgout)
            if teleIOObj is None:
                errMsg = self.updateErrMsg(errMsg, "The wgout object reference is not found in the library!");
            else: 
                self.wgoutsList.append(teleIOObj)
            
        return errMsg
    
    
    
    
class WeatherGeneratorRequest(AbstractRequest):
    '''
    A class that handles the request to the weather generator
    '''

    '''
    Constructor
    '''
    def __init__(self, d : ImmutableMultiDict):
        AbstractRequest.__init__(self, d)
        self.contextDict = OrderedDict()
        self.var = None
              
               
    def areAllParametersThere(self, d : ImmutableMultiDict):    
        """
        Checks if all the required parameters were provided in the request.
        Those are the latitude, longitude, variables of interest,
        the start date, and the end date.
        @param d a ImmutableMultiDict instance provided by the request
        """
        if AbstractRequest.areAllParametersThere(self, d):
            if d.__contains__("from"):
                if d.__contains__("to"):
                    return
        raise BioSimRequestException("A WeatherGeneratorRequest type must at least include lat=, long=, from=, and to=")

    
    def checkParmsValues(self, d : dict):
        errMsg = AbstractRequest.checkParmsValues(self, d)

        if d.__contains__("rep"):
            repValue = d.get("rep")
            if repValue < 1:
                errMsg = self.updateErrMsg(errMsg, "the rep parameter must be equal to or greater than 1")

#         if d.__contains__("nb_years"):
#             nbYearsValue = d.get("nb_years")
#             if nbYearsValue < 1:
#                 errMsg = self.updateErrMsg(errMsg, "the nb_years parameter must be equal to or greater than 1")

#         if d.__contains__("export"):
#             exportValue = d.get("export")
#             if exportValue < 0 or exportValue > 1:
#                 errMsg = self.updateErrMsg(errMsg, "the export parameter must be equal to 0 (kept in memory on the server) or 1 (exported to the client)")

        startDate = d.get("from")
        endDate = d.get("to")
        if startDate > endDate:
            errMsg = self.updateErrMsg(errMsg, "the start date must be the same than or earlier than the end date")    
        
        if d.__contains__("source"):
            sourceValue = d.get("source")
            if sourceValue not in ["FromNormals", "FromObservation"]:
                errMsg = self.updateErrMsg(errMsg, "the source parameter must be equal to FromNormals or FromObservation")
        else:
            d.__setitem__("source", "FromObservation") ### Default value 
            
        if d.__contains__("nb_nearest_neighbor"):
            nbStations = d.get("nb_nearest_neighbor")
            if isinstance(nbStations, int) == False:
                errMsg = self.updateErrMsg(errMsg, "the nb_nearest_neighbor must be an integer")
            elif nbStations < 1 or nbStations > 35:
                errMsg = self.updateErrMsg(errMsg, "the nb_nearest_neighbor must be an integer ranging from 1 to 35")
         
#         if d.__contains__("out"):  ### maybe obsolete
#             outputPreference = d.get("out")
#             if outputPreference not in typeOutputList:
#                 errMsg = self.updateErrMsg(errMsg, "the out parameter must be either h (hourly) or d (daily)")    
# 
#         if d.__contains__("gen"):   ### maybe obsolete
#             generatorPreference = d.get("gen")
#             if generatorPreference not in typeGenList:
#                 errMsg = self.updateErrMsg(errMsg, "the gen parameter must be either des (desaggregated), obs (observed) or gribs (mapped data)")    
        return errMsg
    
    
    def parseRequest(self, i, context : Context):
        requestString = AbstractRequest.parseRequest(self, i, context);
        
        if self.var != None:
            requestString += AbstractRequest.parseVariableRequestString(self.var)
        else:
            requestString += AbstractRequest.parseVariableRequestString(variableList)

        source = self.dict.get("source")
        if (source == "FromObservation" and context.daily == None): ### override the FromObservation when the daily values are unavailable
            source = "FromNormals"             
        requestString += "&Source=" + source            
        
        initDateYr = self.contextDict.get(context)[0]
        finalDateYr = self.contextDict.get(context)[1]

        if source == "FromObservation":
            requestString += "&First_year=" + str(initDateYr) + "&Last_year=" + str(finalDateYr)
           
        if self.dict.__contains__("rep"):
            requestString += "&Replications=" + str(self.dict.get("rep"))
            
        requestString += "&nb_years=" + str(finalDateYr - initDateYr + 1)
        
#         if self.dict.__contains__("export"):
#             self.export = self.dict.get("export") == "1"
#         else:
#             self.export = False ### default value
            
        if self.dict.__contains__("nb_nearest_neighbor"):
            requestString += "&nb_nearest_neighbor=" + str(self.dict.get("nb_nearest_neighbor"))
                                                           
        return requestString


    def doesThisContextMatch(self, context : Context):
        if len(self.contextDict) > 0:       ### some contexts already match
            values = list(self.contextDict.values())
            lastValue = values[-1]
            initDateYr = lastValue[1] + 1   ### the initial date is then set to the last date that matches + 1
        else:
            initDateYr = self.dict.get("from")
        finalDateYr = self.dict.get("to")
        if initDateYr > finalDateYr: ### all the time interval is now included in the self.contextDict dictionary 
            return False
        isFromObservation = self.dict.get("source") == "FromObservation"
        bounds = context.getMatchInThisInterval(initDateYr, finalDateYr, isFromObservation)
        if bounds != None:
            self.contextDict.__setitem__(context, bounds)
            return True
        else:
            return False

    def getInitialDateYr(self):
        return self.dict.get("from")

    def getFinalDateYr(self):
        return self.dict.get("to")

    def isForExport(self):
        return self.export
    
    def getNbRep(self):
        if self.dict.__contains__("rep"):
            return self.dict.get("rep")
        else:
            return 1
    
    def isForceClimateGenerationEnabled(self):
        return self.dict.get("source") == "FromNormals"
        
        
class WeatherGeneratorEpheremalRequest(WeatherGeneratorRequest, SimpleModelRequest):
    
    
    def __init__(self, d : ImmutableMultiDict):
        WeatherGeneratorRequest.__init__(self, d)
        self.weatherGenerated = False

    def areAllParametersThere(self, d:ImmutableMultiDict):
        WeatherGeneratorRequest.areAllParametersThere(self, d)
        return SimpleModelRequest.areAllParametersThere(self, d)
        
    def checkParmsValues(self, d:dict):
        errMsg = WeatherGeneratorRequest.checkParmsValues(self, d)
        errMsg += SimpleModelRequest.checkParmsValues(self, d)
        return errMsg
    
    def parseRequest(self, i, context:Context):
        if self.weatherGenerated:
            return SimpleModelRequest.parseRequest(self, i, context)
        else:
            return WeatherGeneratorRequest.parseRequest(self, i, context)
    
    def setVariables(self, variables):
        self.var = variables
        
    def storeWgoutWrapper(self, wgoutwrapper : WgoutWrapper): 
        self.wgoutsList.append(wgoutwrapper)   
    
        
class BioSimRequestException(Exception):
    
    def __init__(self, message : str):
        Exception.__init__(self, message)
    
    