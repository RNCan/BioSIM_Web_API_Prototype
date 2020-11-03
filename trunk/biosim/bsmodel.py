'''
Handle the different model types and the instantiation of models in BioSIM.

@author: M. Fortin and R. Saint-Amant, Canadian Forest Service, August 2020
@copyright: Her Majesty the Queen in right of Canada
'''
from multiprocessing import Queue, Process, Lock

from biosim.bssettings import ModelType, Settings
from biosim.bsrequest import ModelRequest
from biosim.bsutility import WgoutWrapper, BioSimUtility
import biosim.biosimdll.BioSIM_API as BioSIM_API


def do_job(jobId, modelType : ModelType, tasks_to_accomplish : Queue, tasks_that_are_done : Queue):
    '''
        This function is passed to a Process instance.
        
        It first loads a weather generator associated with a context and then waits for requests to be sent through the
        tasks_to_accomplish Queue instance.
         
        The teleIO objects are converted into dict objects so that they can be sent back to the main process.
        Without conversion there would be a pickled exception. The dict are reconverted into teleIO object in the
        main process. 
        
        The code of this function was inspired by an example available on the JournalDev website at
        https://www.journaldev.com/15631/python-multiprocessing-example . We are thankful to the authors.
    '''
    innerModel = BioSIM_API.Model("Context name");
    initializationString = "Model=" + modelType.getPath();
    msg = innerModel.Initialize(initializationString)
    if jobId == 0:
        tasks_that_are_done.put(innerModel.GetWeatherVariablesNeeded())
        tasks_that_are_done.put(innerModel.GetDefaultParameters())
        tasks_that_are_done.put(innerModel.Help())
        if msg == "Success":
            if Settings.Verbose == True:
                print("Successfully loaded context: " + modelType.getName())
        else:
            raise Exception("Error: Failed to initialize model " + modelType.getName() + " - " + msg);
    
    while True:
        try:
            task = tasks_to_accomplish.get()
            parms = task["parms"]
            wgouts = task["wgouts"]
            outputForThisPlot = []
            for wgout in wgouts:
                teleIOInput = BioSimUtility.convertDictToTeleIO(wgout)
                teleIOOutput = innerModel.Execute(parms, teleIOInput)
                outputForThisPlot.append(BioSimUtility.convertTeleIOToDict(teleIOOutput)) 
            del task["wgouts"]
            del task["parms"]
            task["outputForThisPlot"] = outputForThisPlot
            tasks_that_are_done.put(task)
        except:
            break;
    return True



class Model():
    
    '''
    A wrapper for models in BioSIM.
    '''
    def __init__(self, modelType : ModelType):
        self.lock = Lock()
        self.modelType = modelType
         
        if modelType.isMultiProcessEnabled():
            self.processes = []
            self.tasksToDo = Queue()
            self.tasksDone = Queue()
            for i in range(modelType.getNbProcesses()):   
                p = Process(target=do_job, args = (i, modelType, self.tasksToDo, self.tasksDone))
                self.processes.append(p)
                p.start()
            self.climateVariableNeeded = self.tasksDone.get().split("+")
            self.defaultParameters = self.tasksDone.get().split("+")
            self.help = self.tasksDone.get()
        else:
            self.innerModel = BioSIM_API.Model("Context name");
            initializationString = "Model=" + modelType.getPath();
#            print(initializationString)
            msg = self.innerModel.Initialize(initializationString)
            self.climateVariableNeeded = self.innerModel.GetWeatherVariablesNeeded().split("+")
            self.defaultParameters = self.innerModel.GetDefaultParameters().split("+")
            self.help = self.innerModel.Help()
            if msg == "Success":
                if Settings.Verbose == True:
                    print("Successfully loaded context: " + modelType.getName())
            else:
                raise Exception("Error: Failed to initialize model " + modelType.getName() + " - " + msg);
                    
    def getHelp(self):
        return self.help
    
    def getDefaultParameters(self):
        return self.defaultParameters
    
    def doProcess(self, bioSimRequest : ModelRequest):
        outputs = []
        nbLocations = len(bioSimRequest.wgoutsList)
        if self.modelType.isMultiProcessEnabled():
            mainDict = dict()
            self.lock.acquire()     ### To avoid concurrent feeding of the taskToDo queue
            for i in range(nbLocations):
                wgoutWrapper = bioSimRequest.wgoutsList[i]
                task = wgoutWrapper.convertIntoDict()
                task["natOrd"] = i
                task["parms"] = bioSimRequest.parseRequest(0, None)
                self.tasksToDo.put(task)
            for i in range(nbLocations):
                modelOutput = self.tasksDone.get()
                naturalOrder = modelOutput["natOrd"]
                mainDict[naturalOrder] = modelOutput
            self.lock.release()      ### release the lock for other threads
            for i in range(nbLocations):
                modelOutput = mainDict[i]
                mow = ModelOutputWrapper()
                mow.__reconvertFromDict__(modelOutput)
                outputs.append(mow)
        else:
            for i in range(nbLocations):
                outputForThisPlot = []
                parms = bioSimRequest.parseRequest(0, None)
                wgoutWrapper = bioSimRequest.wgoutsList[i]
                for wgout in wgoutWrapper.getWgouts():
                    teleIOOutput = self.innerModel.Execute(parms, wgout)
                    outputForThisPlot.append(teleIOOutput) 
                mow = ModelOutputWrapper()
                mow.setModelOutput(outputForThisPlot, wgoutWrapper)
                outputs.append(mow)
        return outputs

    def getRequiredVariables(self):
            return self.climateVariableNeeded



class ModelOutputWrapper:
    '''
    A class that wraps the model output and parse them before sending the result back to the client.
    '''
    def __init__(self):
        self.outputForThisPlot = []

    def setModelOutput(self, outputForThisPlot, ww: WgoutWrapper):
        self.outputForThisPlot = outputForThisPlot
        self.initialDateYr = ww.getInitialDateYr()
        self.finalDateYr = ww.getFinalDateYr()
        self.nbRep = ww.getNbRep()
        self.lastDailyDate = ww.lastDailyDate
       
    def __reconvertFromDict__(self, d : dict):
        for wgout in d["outputForThisPlot"]:
            self.outputForThisPlot.append(BioSimUtility.convertDictToTeleIO(wgout))
        self.initialDateYr = d["initDateYr"]
        self.finalDateYr = d["finalDateYr"]
        self.nbRep = d["nbRep"]
        self.lastDailyDate = d["lastDailyDate"]
       
#     def processRequest(self, ww : WgoutWrapper, model : Model, bioSimRequest : ModelRequest):    
#         for wgout in ww.getWgouts():
#             self.outputForThisPlot.append(model.doProcess(bioSimRequest.parseRequest(0, None), wgout))    ## the index i and the context are useless for the ModelRequest class
#         self.initialDateYr = ww.getInitialDateYr()
#         self.finalDateYr = ww.getFinalDateYr()
#         self.nbRep = ww.getNbRep()
    
    def __parseListToString__(self, myList:list):
        s = ""
        for i in range(len(myList)):
            s += str(myList[i])
            if i < (len(myList) - 1):
                s += ","
        return s
    
    def parseOutputToString(self):
        strOutput = ""
        header = None
        initialDateYr = self.initialDateYr
        finalDateYr = self.finalDateYr
        nbRep = self.nbRep
        substrings = []
        for zz in range(nbRep):
            substrings.append("")
        ### a particular output is an interval within a wrapper for a given location.
        currentDateYr = initialDateYr
        for output in self.outputForThisPlot:   
            if output.msg == "Success":
                if (header == None):
                    header = output.text[0:(output.text.index("\n") + 1)]
                    headerFields = header.split(",")
                    strOutput += "Rep," + header[0:output.text.index("\n")] + ",DataType\n"
                newText = output.text.replace(header, "")
                lines = newText.split("\n")
                if lines[len(lines)-1] == "":  ### remove last line if needed
                    lines = lines[0:(len(lines) - 1)]
                nbObsPerRep = len(lines)/nbRep 
                if abs(nbObsPerRep - round(nbObsPerRep, 0)) > 1E-8:     ### check if the number of observations is an integer
                    raise("The number of lines is incompatible with the number of replicates!")  
                else:
                    nbObsPerRep = int(nbObsPerRep)
                i = 0
                try: 
                    indexYearField = headerFields.index("Year")
                except ValueError:
                    indexYearField = -1
                    
                for rep in range(nbRep):
                    innerDate = currentDateYr - 1
                    lastKnownDate = None
                    for obs in range(nbObsPerRep):
                        myLine = lines[i]
                        if indexYearField != -1:
                            fields = myLine.split(",")
                            if innerDate > finalDateYr:
                                raise("The currentDateYr is inconsistent with the finalDateYr value!")
                            yearFieldValue = fields[indexYearField]
                            if yearFieldValue != lastKnownDate:
                                innerDate += 1
                                lastKnownDate = yearFieldValue
                            fields[indexYearField] = innerDate
                            myLine = self.__parseListToString__(fields)
                        if innerDate < self.lastDailyDate:
                            dataType = "Real_Data"
                        elif innerDate == self.lastDailyDate: 
                            dataType = "Real_Data/Simulated"
                        else:
                            dataType = "Simulated"
                        myLine = str(rep) + "," + myLine + "," + dataType + "\n"
                        i += 1
#                        strOutput += myLine
                        substrings[rep] += myLine
                currentDateYr = innerDate + 1
            else:
                strOutput += output.msg
                return strOutput        ### in case of error we do not iterate on the data
        for substring in substrings:
            strOutput += substring
        return strOutput
  


    def parseOutputToDict(self):
        header = None
        initialDateYr = self.initialDateYr
        finalDateYr = self.finalDateYr
        nbRep = self.nbRep
        ### a particular output is an interval within a wrapper for a given location.
        currentDateYr = initialDateYr
        mainDict = dict()
        for output in self.outputForThisPlot:   
            if output.msg == "Success":
                if (header == None):
                    header = output.text[0:(output.text.index("\n") + 1)]
                    headerFields = header[0:output.text.index("\n")].split(",")
                    headerFields.append("DataType")
                newText = output.text.replace(header, "")
                lines = newText.split("\n")
                if lines[len(lines)-1] == "":  ### remove last line if needed
                    lines = lines[0:(len(lines) - 1)]
                nbObsPerRep = len(lines)/nbRep 
                if abs(nbObsPerRep - round(nbObsPerRep, 0)) > 1E-8:     ### check if the number of observations is an integer
                    raise("The number of lines is incompatible with the number of replicates!")  
                else:
                    nbObsPerRep = int(nbObsPerRep)
                i = 0
                try: 
                    indexYearField = headerFields.index("Year")
                except ValueError:
                    indexYearField = -1
                    
                for rep in range(nbRep):
                    if mainDict.__contains__(rep) == False:
                        mainDict.__setitem__(rep, list())
                    innerDate = currentDateYr - 1
                    lastKnownDate = None
                    for obs in range(nbObsPerRep):
                        myLine = lines[i]
                        fields = myLine.split(",")
                        if indexYearField != -1:
                            if innerDate > finalDateYr:
                                raise("The currentDateYr is inconsistent with the finalDateYr value!")
                            yearFieldValue = fields[indexYearField]
                            if yearFieldValue != lastKnownDate:
                                innerDate += 1
                                lastKnownDate = yearFieldValue
                            fields[indexYearField] = innerDate
                            myLine = self.__parseListToString__(fields)
                        if innerDate < self.lastDailyDate:
                            fields.append("Real_Data")
                        elif innerDate == self.lastDailyDate: 
                            fields.append("Real_Data/Simulated")
                        else:
                            fields.append("Simulated")
                        i += 1
                        obsDict = dict(zip(headerFields, fields))
                        mainDict.get(rep).append(obsDict)
                currentDateYr = innerDate + 1
            else:
                return output.msg
        return mainDict
  
    def parseOutputToDictAlt(self):
        header = None
        initialDateYr = self.initialDateYr
        finalDateYr = self.finalDateYr
        nbRep = self.nbRep
        ### a particular output is an interval within a wrapper for a given location.
        currentDateYr = initialDateYr
        mainDict = []
        for output in self.outputForThisPlot:   
            if output.msg == "Success":
                if (header == None):
                    header = output.text[0:(output.text.index("\n") + 1)]
                    headerFields = ["rep"]
                    headerFields.extend(header[0:output.text.index("\n")].split(","))
                    headerFields.append("DataType")
                newText = output.text.replace(header, "")
                lines = newText.split("\n")
                if lines[len(lines)-1] == "":  ### remove last line if needed
                    lines = lines[0:(len(lines) - 1)]
                nbObsPerRep = len(lines)/nbRep 
                if abs(nbObsPerRep - round(nbObsPerRep, 0)) > 1E-8:     ### check if the number of observations is an integer
                    raise("The number of lines is incompatible with the number of replicates!")  
                else:
                    nbObsPerRep = int(nbObsPerRep)
                i = 0
                try: 
                    indexYearField = headerFields.index("Year")
                except ValueError:
                    indexYearField = -1
                    
                for rep in range(nbRep):
                    innerDate = currentDateYr - 1
                    lastKnownDate = None
                    for obs in range(nbObsPerRep):
                        fields = [rep]
                        myLine = lines[i]
                        fields.extend(myLine.split(","))
                        if indexYearField != -1:
                            if innerDate > finalDateYr:
                                raise("The currentDateYr is inconsistent with the finalDateYr value!")
                            yearFieldValue = fields[indexYearField]
                            if yearFieldValue != lastKnownDate:
                                innerDate += 1
                                lastKnownDate = yearFieldValue
                            fields[indexYearField] = innerDate
                            myLine = self.__parseListToString__(fields)
                        if innerDate < self.lastDailyDate:
                            fields.append("Real_Data")
                        elif innerDate == self.lastDailyDate: 
                            fields.append("Real_Data/Simulated")
                        else:
                            fields.append("Simulated")
                        i += 1
                        obsDict = dict(zip(headerFields, fields))
                        mainDict.append(obsDict)
                currentDateYr = innerDate + 1
            else:
                return output.msg
        return mainDict
