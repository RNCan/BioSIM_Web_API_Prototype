'''
A module that contains utility classes

@author: M. Fortin and R. Saint-Amant, Canadian Forest Service, August 2020
@copyright: Her Majesty the Queen in right of Canada
'''
import biosim.biosimdll.BioSIM_API as BioSIM_API
from threading import Lock
from collections import OrderedDict

lock = Lock()

class BioSimUtility():
    '''
    A class with static methods for utility
    '''

    maxNumberWgoutInstances = 100000;
    
    library = OrderedDict()



    @staticmethod
    def convertTeleIOToDict(obj : BioSIM_API.teleIO):
        '''
            Convert the teleIO instance into a dict instance so that it can be sent back and forth to the sub processes
        '''
        d = dict()   
        d["comment"] = obj.comment
        d["compress"] = obj.compress
        d["data"] = obj.data
        d["metadata"] = obj.metadata
        d["msg"] = obj.msg
        d["text"] = obj.text 
        return d

    @staticmethod
    def convertDictToTeleIO(d : dict):
        '''
            Reconvert a dict instance into a teleIO instance 
        '''
        teleIOobj = BioSIM_API.teleIO(d["compress"], d["msg"], d["comment"], d["metadata"], d["text"], d["data"])
        return teleIOobj


    @staticmethod
    def convertTeleIOTextToList(text : str):
        outputList = list()
        header = text[0:(text.index("\n") + 1)]
        headerFields = header[0:text.index("\n")].split(",")
        newText = text.replace(header, "")
        lines = newText.split("\n")
        if lines[len(lines)-1] == "":  ### remove last line if needed
            lines = lines[0:(len(lines) - 1)]
        for myLine in lines:
            fields = myLine.split(",")
            obsDict = dict(zip(headerFields, fields))
            outputList.append(obsDict)
        return outputList

class TeleIODictList(list):
    '''
    A List of TeleIODict instances. It handles the concatenation of instances from several contexts in order
    to have a single TeleIODict instance in the end. 
    '''
    
    ticketNumber = int(0)

    def add(self, l : list):
        '''
        Add a TeleIODictList instance to this one. If this instance is empty, the entries of the l argument
        are simply appended to this list. Otherwise, the TeleIODict instances in l are merged with those of
        this instance.
        '''
        if len(self) > 0 and len(l) != len(self):
            raise("WeatherGeneratorList.add: the list is not compatible!")
        elif isinstance(l, TeleIODictList) == False:
            raise("The l parameter should be of the WeatherGeneratorList class!")
        else:
            isEmpty = len(self) == 0
            for i in range(len(l)):
                if isEmpty:
                    self.append(l[i])
                else:
                    self[i].__merge__(l[i])
    
    def setLastDailyDate(self, date):
        for obj in self:
            obj.__setLastDailyDate__(date)

    def registerTeleIODictList(self):
        '''
        Register the TeleIODictList instance in the library for the non ephemeral mode
        '''
        lock.acquire()
        outputStr = ""
        for i in range(len(self)):
            key = str(TeleIODictList.ticketNumber)
            BioSimUtility.library.__setitem__(key, self[i]);
            if i == 0:
                outputStr += key
            else:
                outputStr += " " + key
            TeleIODictList.ticketNumber += 1
        while len(BioSimUtility.library) > BioSimUtility.maxNumberWgoutInstances:
            firstkey = next(iter(BioSimUtility.library.keys()))
            del BioSimUtility.library[firstkey]  ## we remove the oldest instances first these are the first instance in the ordered dict
        lock.release()
        return outputStr
    
    def getOutputText(self):
        '''
        Parse the text before it is sent to the client
        '''
        outputStr = ""
        for i in range(len(self)):
            outputStr += self[i].__getText__(True)
        return outputStr;
    
    def getTeleIO(self, i):
        '''
        Return a BioBIM_API.teleIO instance corresponding to the ith TeleIODict instance in this list
        '''
        return self[i].getTeleIO()

    @staticmethod
    def removeTeleIODictList(references):
        lock.acquire()
        for ref in references:
            if BioSimUtility.library.__contains__(ref):
                del BioSimUtility.library[ref]
        lock.release()
        
    @staticmethod
    def getTeleIODictList(l : list):
        teleIODictList = TeleIODictList()
        lock.acquire()
        for key in l:
            obj = BioSimUtility.library.get(key)
            if obj is not None:
                BioSimUtility.library.move_to_end(key, last = True) ### move the object to the end so that it shows it's been recently used
                teleIODictList.append(obj)
        lock.release()
        return teleIODictList;
    
    
    def parseToJSON(self):
        mainDict = dict()
        for i in range(len(self)):
            mainDict.__setitem__(i, self[i].__parseToJSON__()) 
        return mainDict

    
    
    
    
class TeleIODict(dict): 
    '''
    A representation of a BioSIM_API.teleIO instance that can be pickled and parsed. It handles the 
    concatenation of various BioSIM_API.teleIO instances by updating the value corresponding to the
    "text" key. This is done through the __merge__ function.
    '''
    def __init__(self, obj : BioSIM_API.teleIO, dateYr, isWeatherGenerationOutput = True):
        '''
            Convert the teleIO instance into a dict instance so that it can be sent back and forth to the sub processes
        '''
        dict.__init__(self)   
        self["comment"] = obj.comment
        self["compress"] = obj.compress
        self["data"] = obj.data
        self["metadata"] = obj.metadata
        self["msg"] = obj.msg
        if isWeatherGenerationOutput == False:
            self["lastDailyDate"] = dateYr
            self.__parseText__(obj.text, isWeatherGenerationOutput)
        else:
            self.__parseText__(obj.text, isWeatherGenerationOutput, dateYr) ## here dateYr is the finalDate of the context
       
    def __parseText__(self, text, isWeatherGenerationOutput, dateYr = None):
        replications = list()
        stringForThisRep = ""
        lines = text.split("\n")
        repId = 0
        for i in range(len(lines)):
            if i == 0:
                self["header"] = lines[i]
                headerFields = self["header"].split(",")
                indexYearField = headerFields.index("Year")
            elif lines[i] == self["header"]:
                replications.append(stringForThisRep)
                stringForThisRep = ""
                repId += 1
            elif len(lines[i]) > 0:
                myLine = lines[i]
                values = myLine.split(",")
                if isWeatherGenerationOutput == True:
                    thisYear = int(values[indexYearField])
                    if thisYear <= 0:
                        values[indexYearField] = dateYr + thisYear
                        myLine = self.__parseListToString__(values)
                else: ## then it is a model output
                    lastDailyDate = self["lastDailyDate"]
                    try:
                        thisYear = int(values[indexYearField])
                        if thisYear < lastDailyDate:
                            dataType = "Real_Data"
                        elif thisYear == lastDailyDate: 
                            dataType = "Real_Data/Simulated"
                        else:
                            dataType = "Simulated"
                    except Exception:
                        dataType = "No year provided"
                    myLine = str(repId) + "," + myLine + "," + dataType
                stringForThisRep += myLine + "\n"
        replications.append(stringForThisRep)
        if isWeatherGenerationOutput == False:
            currentHeader = self["header"]
            newHeader = "Rep," + currentHeader + ",DataType"
            self["header"] = newHeader
        self["replist"] = replications

    def __parseListToString__(self, myList:list):
        s = ""
        for i in range(len(myList)):
            s += str(myList[i])
            if i < (len(myList) - 1):
                s += ","
        return s

    def __getText__(self, isOutput = False):
        outputStr = ""
        rep = self["replist"]  
        if isOutput == True:        ### then only one header
            outputStr += self["header"] + "\n"
        for i in range(len(rep)):
            if isOutput == False:
                outputStr += self["header"] + "\n"
            outputStr += rep[i]
        return outputStr
    
    def __setLastDailyDate__(self, date):
        self["lastDailyDate"] = date
        
    def __parseToJSON__(self):
        if self["msg"] == "Success":
            headerFields = self["header"].split(",")
            mainDict = dict()
            for i in range(len(self["replist"])):
                mainDict.__setitem__(i, list())
                thisRep = self["replist"][i]
                lines = thisRep.split("\n")
                for line in lines:
                    values = line.split(",")
                    mainDict.get(i).append(dict(zip(headerFields, values)))
            return mainDict
        else:
            return self["msg"]
        
    def getTeleIO(self):
        '''
        Re-convert a TeleIODict instance into a BioSIM_API.teleIO instance
        '''
        teleIOobj = BioSIM_API.teleIO(self["compress"], self["msg"], self["comment"], self["metadata"], self.__getText__(), self["data"])
        return teleIOobj

    def __merge__(self, w):
        thisRepList = self["replist"]
        thatRepList = w["replist"]
        if isinstance(w, TeleIODict) == False or len(thisRepList) != len(thatRepList):
            raise("The w argument should be a WeatherGeneratorLocation instance with the same number of replications!")
        for i in range(len(thisRepList)):
            thisRepList[i] += thatRepList[i]    

    
class WgoutWrapper:
    
    def __init__(self, obj, initDateYr, finalDateYr, nbRep, lastDailyDate):
        '''
        Constructor
        '''
        self.obj = obj
        self.initDateYr = initDateYr
        self.finalDateYr = finalDateYr
        self.nbRep = nbRep
        self.lastDailyDate = lastDailyDate

    def getInitialDateYr(self):
        return self.initDateYr
    
    def getFinalDateYr(self):
        return self.finalDateYr
    
    def getWgouts(self):
        return self.obj

    def getNbRep(self):
        return self.nbRep
    
    def convertIntoDict(self):
        d = dict()
        wgouts = []
        for wgout in self.obj:
            wgouts.append(BioSimUtility.convertTeleIOToDict(wgout))
        d["wgouts"] = wgouts
        d["initDateYr"] = self.initDateYr
        d["finalDateYr"] = self.finalDateYr
        d["nbRep"] = self.nbRep      
        d["lastDailyDate"] = self.lastDailyDate
        return d