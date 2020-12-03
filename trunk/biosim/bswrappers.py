'''
Provides a wrapper for the BioSim instance. This module is essentially used by the model module to
instantiate several BioSim applications with different contexts

@author: M. Fortin and R. Saint-Amant, Canadian Forest Service, August 2020
@copyright: Her Majesty the Queen in right of Canada
'''
from datetime import datetime
from multiprocessing import Process, Queue
from threading import Lock

from biosim.bssettings import Context, Settings
from biosim.bsrequest import NormalsRequest, AbstractRequest, WeatherGeneratorRequest 
from biosim.bsutility import BioSimUtility, TeleIODictList, TeleIODict
 
import biosim.biosimdll.BioSIM_API as BioSIM_API


def do_job(context : Context, tasks_to_accomplish : Queue, tasks_that_are_done : Queue):
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
    WG = BioSIM_API.WeatherGenerator(context.getContextName())
    initializationString = context.getInitializationString()
    msg = WG.Initialize(initializationString);
    tasks_that_are_done.put(msg)
    if msg != "Success":
        return ### we get out of the process, the msg has been sent to the main thread anyway
    else:
        if Settings.Verbose == True:
            print("Successfully loaded context: " + context.getContextName())
    
    while True:
        try:
            task = tasks_to_accomplish.get()
            naturalOrder = task["natOrd"]
            request = task["request"]
            outputTeleIOobj = WG.Generate(request)
            teleIOinDict = BioSimUtility.convertTeleIOToDict(outputTeleIOobj)   ### conversion in a dict instance to avoid pickled exception
            teleIOinDict["natOrd"] = naturalOrder   ### adding the natural order to sort the instances upon reception in the main process
            tasks_that_are_done.put(teleIOinDict)
        except:
            break;
    return True



class BioSimNormalsAndWeatherGeneratorWrapper:
    '''
    A wrapper for the BioSim normals or weather generator in C++
    '''
    
    def __init__(self, context : Context):
        '''
        Constructor
        @param context: a BioSimContext instance that defines how BioSim is initialized 
        @raise exception: if the BioSim instance in C++ cannot be initialized
        '''
        self.context = context
        self.lock = Lock()
        if context.isMultiProcessEnabled():
            self.tasksToDo = Queue()
            self.tasksDone = Queue()
            self.processes = self.initializeProcesses(context, self.tasksToDo, self.tasksDone)
#             for i in range(context.getNbProcesses()):  
#                 p = Process(target=do_job, args = (context, self.tasksToDo, self.tasksDone))
#                 self.processes.append(p)
#                 p.start()
        else:
            self.WG = BioSIM_API.WeatherGenerator(context.getContextName())
            initializationString = context.getInitializationString()
            msg = self.WG.Initialize(initializationString);
            if msg != "Success":
                raise Exception(msg)
            else:
                if Settings.Verbose == True:
                    print("Successfully loaded context: " + context.getContextName())

    def initializeProcesses(self, context : Context, tasksToDo : Queue, tasksDone : Queue):
        processes = []
        for i in range(context.getNbProcesses()):  
            p = Process(target=do_job, args = (context, tasksToDo, tasksDone))
            processes.append(p)
            p.start()
            msg = tasksDone.get()
            if msg != "Success":
                raise Exception(msg)
        return processes

    def getContext(self):
        return self.context

    def respawn(self):
        context = self.context
        print("Carrying out the respawning...")
        if context.isMultiProcessEnabled():
            tasksToDo = Queue()
            tasksDone = Queue()
            processes = self.initializeProcesses(context, tasksToDo, tasksDone)
#             for i in range(context.getNbProcesses()):  
#                 p = Process(target=do_job, args = (context, tasksToDo, tasksDone))
#                 processes.append(p)
#                 p.start()
            self.lock.acquire()
            formerProcesses = self.processes
            self.processes = processes
            self.tasksToDo = tasksToDo
            self.tasksDone = tasksDone
            self.lock.release()
            for p in formerProcesses:
                p.terminate()
                
            #### TODO should the weather generator instance be somehow finalized.....? MF20200928
        else:
            WG = BioSIM_API.WeatherGenerator(context.getContextName())
            initializationString = context.getInitializationString()
            msg = WG.Initialize(initializationString);
            if msg != "Success":
                raise Exception(msg)
            else:
                self.lock.acquire()
                self.WG = WG
                self.lock.release()
                print("Successfully loaded context: " + context.getContextName())
        currentTime = datetime.now().time()
        print("Respawn successfully terminated at", currentTime)

    def doProcess(self, bioSimRequest : AbstractRequest):
        '''
        Process the request whether it is a request for normals or weather generation. The
        class of the AbstractRequest instance allows distinguishing the type of request. 
        Return a list of teleIO objects.
        '''
        if isinstance(bioSimRequest, NormalsRequest):
            teleIODictList = [] #### TODO fix this as well
            for i in range(bioSimRequest.n):
                teleIODictList.append(self.WG.GetNormals(bioSimRequest.parseRequest(i, self.context))) 
        elif isinstance(bioSimRequest, WeatherGeneratorRequest):
            teleIODictList = TeleIODictList()
            if (self.context.isMultiProcessEnabled()):
                mainDict = dict()
                self.lock.acquire()     ### To avoid concurrent feeding of the taskToDo queue
                for i in range(bioSimRequest.n):
                    d = dict()
                    d["natOrd"] = i
                    d["request"] = bioSimRequest.parseRequest(i, self.context)
                    self.tasksToDo.put(d)
                for i in range(bioSimRequest.n):
                    teleIOinDict = self.tasksDone.get()
                    naturalOrder = teleIOinDict["natOrd"]
                    mainDict[naturalOrder] = BioSimUtility.convertDictToTeleIO(teleIOinDict)
                self.lock.release()      ### release the lock for other threads
                for i in range(bioSimRequest.n):
                    teleIODictList.append(mainDict[i])  ### TODO this does not work any mode
            else:
                for i in range(bioSimRequest.n):
                    WGout = self.WG.Generate(bioSimRequest.parseRequest(i, self.context))
                    datesYr = bioSimRequest.getDatesYr(self.context)
                    teleIODictList.append(TeleIODict(WGout, datesYr[1]))
        return teleIODictList

        
