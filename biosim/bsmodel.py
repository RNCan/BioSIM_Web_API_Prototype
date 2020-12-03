'''
Handle the different model types and the instantiation of models in BioSIM.

@author: M. Fortin and R. Saint-Amant, Canadian Forest Service, August 2020
@copyright: Her Majesty the Queen in right of Canada
'''
from multiprocessing import Queue, Process, Lock

from biosim.bssettings import ModelType, Settings
from biosim.bsrequest import ModelRequest
from biosim.bsutility import TeleIODict, TeleIODictList
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
            inputTeleIODict = tasks_to_accomplish.get()
            parms = inputTeleIODict["parms"]
            lastDailyDate = inputTeleIODict["lastDailyDate"]
            inputTeleIO = inputTeleIODict.getTeleIO()
            outputTeleIO = innerModel.Execute(parms, inputTeleIO)
            outputTeleIODict = TeleIODict(outputTeleIO, lastDailyDate, False)
            outputTeleIODict["natOrd"] = inputTeleIODict["natOrd"]
            tasks_that_are_done.put(outputTeleIODict)
        except Exception as error:
            tasks_that_are_done(error)



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
        outputTeleIODictList = TeleIODictList()
        inputTeleIODictList = bioSimRequest.teleIODictList
        nbLocations = len(inputTeleIODictList)
        if self.modelType.isMultiProcessEnabled():
            mainDict = dict()
            self.lock.acquire()     ### To avoid concurrent feeding of the taskToDo queue
            for i in range(nbLocations):
                teleIODict = inputTeleIODictList[i].clone()
                teleIODict["natOrd"] = i
                teleIODict["parms"] = bioSimRequest.parseRequest(0, None)
                self.tasksToDo.put(teleIODict)
            for i in range(nbLocations):
                teleIODict = self.tasksDone.get()
                naturalOrder = teleIODict["natOrd"]
                del teleIODict["natOrd"]
                mainDict[naturalOrder] = teleIODict
            self.lock.release()      ### Release the lock for other threads
            for i in range(nbLocations):
                outputTeleIODictList.append(mainDict[i])
        else:
            for i in range(nbLocations):
                parms = bioSimRequest.parseRequest(0, None)
                inputTeleIODict = inputTeleIODictList[i]
                lastDailyDate = inputTeleIODict["lastDailyDate"]
                inputTeleIO = inputTeleIODict.getTeleIO()
                outputTeleIO = self.innerModel.Execute(parms, inputTeleIO)
                outputTeleIODict = TeleIODict(outputTeleIO, lastDailyDate, False)
                outputTeleIODictList.append(outputTeleIODict)
        return outputTeleIODictList

    def getRequiredVariables(self):
            return self.climateVariableNeeded



