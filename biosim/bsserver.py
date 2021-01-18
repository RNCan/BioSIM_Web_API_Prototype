'''
The server class which Loads the different instances, and models of BioSIM 
and handles the requests sent to them.

@author: M. Fortin and R. Saint-Amant, Canadian Forest Service, August 2020
@copyright: Her Majesty the Queen in right of Canada
'''
from multiprocessing import Queue, Process
import os
import shutil
import subprocess
import threading
import time
import zipfile

from biosim.bsmodel import Model
from biosim.bsrequest import AbstractRequest, ModelRequest, WeatherGeneratorRequest, NormalsRequest, \
    WeatherGeneratorEpheremalRequest, TeleIODictList
from biosim.bssettings import Context, Shore, Normals, Daily, DEM, Gribs, ClimateModel, RCP, ModelType, \
    CurrentDailyHandler, Settings
from biosim.bswrappers import BioSimNormalsAndWeatherGeneratorWrapper

PastClimateGeneration = "PastClimateForGeneration"

class Server:
    '''
    Handles the initialization of the different instances of BioSim, of the available models
    as well as the requests sent to them.
    '''

    lastDailyDate = 0       ### the variable is set dynamically when loading the context

    Instance = None         ### Singleton instance of the server

    @staticmethod
    def InstantiateServer():
        Server.Instance = Server()

    
    def __init__(self):
        '''
        Constructor
        '''
        if Settings.MultiprocessMode:
            if Settings.ProductionMode:
                self.nbProcessesForWrappers = 3
            else: # then multiprocess but development mode 
                self.nbProcessesForWrappers = 2
        else: 
            self.nbProcessesForWrappers = 1
            
        print("Loading contexts and models...")    
        pastClimateNormals = [Normals.CanUSA1941_1970, Normals.CanUSA1951_1980, Normals.CanUSA1961_1990, Normals.CanUSA1971_2000, Normals.CanUSA1981_2010]
        hadley45 = [Normals.CanUSA1991_2020Hadley45, Normals.CanUSA2001_2030Hadley45, Normals.CanUSA2011_2040Hadley45,
                    Normals.CanUSA2021_2050Hadley45, Normals.CanUSA2031_2060Hadley45, Normals.CanUSA2041_2070Hadley45,
                    Normals.CanUSA2051_2080Hadley45, Normals.CanUSA2061_2090Hadley45, Normals.CanUSA2071_2100Hadley45]
        hadley85 = [Normals.CanUSA1991_2020Hadley85, Normals.CanUSA2001_2030Hadley85, Normals.CanUSA2011_2040Hadley85,
                    Normals.CanUSA2021_2050Hadley85, Normals.CanUSA2031_2060Hadley85, Normals.CanUSA2041_2070Hadley85,
                    Normals.CanUSA2051_2080Hadley85, Normals.CanUSA2061_2090Hadley85, Normals.CanUSA2071_2100Hadley85]
        rcm445 = [Normals.CanUSA1991_2020RCM445, Normals.CanUSA2001_2030RCM445, Normals.CanUSA2011_2040RCM445,
                  Normals.CanUSA2021_2050RCM445, Normals.CanUSA2031_2060RCM445, Normals.CanUSA2041_2070RCM445,
                  Normals.CanUSA2051_2080RCM445, Normals.CanUSA2061_2090RCM445, Normals.CanUSA2071_2100RCM445]
        rcm485 = [Normals.CanUSA1991_2020RCM485, Normals.CanUSA2001_2030RCM485, Normals.CanUSA2011_2040RCM485,
                  Normals.CanUSA2021_2050RCM485, Normals.CanUSA2031_2060RCM485, Normals.CanUSA2041_2070RCM485,
                  Normals.CanUSA2051_2080RCM485, Normals.CanUSA2061_2090RCM485, Normals.CanUSA2071_2100RCM485]
        gcm445 = [Normals.CanUSA1991_2020GCM445, Normals.CanUSA2001_2030GCM445, Normals.CanUSA2011_2040GCM445,
                  Normals.CanUSA2021_2050GCM445, Normals.CanUSA2031_2060GCM445, Normals.CanUSA2041_2070GCM445,
                  Normals.CanUSA2051_2080GCM445, Normals.CanUSA2061_2090GCM445, Normals.CanUSA2071_2100GCM445]
        gcm485 = [Normals.CanUSA1991_2020GCM485, Normals.CanUSA2001_2030GCM485, Normals.CanUSA2011_2040GCM485,
                  Normals.CanUSA2021_2050GCM485, Normals.CanUSA2031_2060GCM485, Normals.CanUSA2041_2070GCM485,
                  Normals.CanUSA2051_2080GCM485, Normals.CanUSA2061_2090GCM485, Normals.CanUSA2071_2100GCM485]
                    

        self.normals = dict()
        self.normals.__setitem__(RCP.PastClimate, dict())
        self.normals.__setitem__(RCP.RCP45, self.setClimateModelsInDict(True)) ### true a dict and not a list
        self.normals.__setitem__(RCP.RCP85, self.setClimateModelsInDict(True)) ### true a dict and not a list
        
        for norm in pastClimateNormals:
            context = Context(Shore.Shore1, norm, None, DEM.WorldWide30sec, Gribs.HRDPS_daily_2019)
            wrapper = BioSimNormalsAndWeatherGeneratorWrapper(context)
            self.normals.get(RCP.PastClimate).__setitem__(context.normals.getShortNormals(), wrapper)
            
        for norm in hadley45:
            context = Context(Shore.Shore1, norm, None, DEM.WorldWide30sec, Gribs.HRDPS_daily_2019)
            wrapper = BioSimNormalsAndWeatherGeneratorWrapper(context)
            self.normals.get(RCP.RCP45).get(ClimateModel.Hadley).__setitem__(context.normals.getShortNormals(), wrapper)
        
        for norm in hadley85:
            context = Context(Shore.Shore1, norm, None, DEM.WorldWide30sec, Gribs.HRDPS_daily_2019)
            wrapper = BioSimNormalsAndWeatherGeneratorWrapper(context)
            self.normals.get(RCP.RCP85).get(ClimateModel.Hadley).__setitem__(context.normals.getShortNormals(), wrapper)

        for norm in rcm445:
            context = Context(Shore.Shore1, norm, None, DEM.WorldWide30sec, Gribs.HRDPS_daily_2019)
            wrapper = BioSimNormalsAndWeatherGeneratorWrapper(context)
            self.normals.get(RCP.RCP45).get(ClimateModel.RCM4).__setitem__(context.normals.getShortNormals(), wrapper)

        for norm in rcm485:
            context = Context(Shore.Shore1, norm, None, DEM.WorldWide30sec, Gribs.HRDPS_daily_2019)
            wrapper = BioSimNormalsAndWeatherGeneratorWrapper(context)
            self.normals.get(RCP.RCP85).get(ClimateModel.RCM4).__setitem__(context.normals.getShortNormals(), wrapper)

        for norm in gcm445:
            context = Context(Shore.Shore1, norm, None, DEM.WorldWide30sec, Gribs.HRDPS_daily_2019)
            wrapper = BioSimNormalsAndWeatherGeneratorWrapper(context)
            self.normals.get(RCP.RCP45).get(ClimateModel.GCM4).__setitem__(context.normals.getShortNormals(), wrapper)

        for norm in gcm485:
            context = Context(Shore.Shore1, norm, None, DEM.WorldWide30sec, Gribs.HRDPS_daily_2019)
            wrapper = BioSimNormalsAndWeatherGeneratorWrapper(context)
            self.normals.get(RCP.RCP85).get(ClimateModel.GCM4).__setitem__(context.normals.getShortNormals(), wrapper)
        
        
        self.weatherGen = dict()
        self.weatherGen.__setitem__(RCP.PastClimate, list())
        self.weatherGen.__setitem__(PastClimateGeneration, list())
        self.weatherGen.__setitem__(RCP.RCP45, self.setClimateModelsInDict(False)) ### false a list and not a dict
        self.weatherGen.__setitem__(RCP.RCP85, self.setClimateModelsInDict(False)) ### false a list and not a dict
 
        context1  = Context(Shore.Shore1, Normals.CanUSA1941_1970, Daily.CanUSA1900_1950, DEM.WorldWide30sec, Gribs.HRDPS_daily_2019, nbProcesses=self.nbProcessesForWrappers)
        context2  = Context(Shore.Shore1, Normals.CanUSA1951_1980, Daily.CanUSA1950_1980, DEM.WorldWide30sec, Gribs.HRDPS_daily_2019, nbProcesses=self.nbProcessesForWrappers)
        context3  = Context(Shore.Shore1, Normals.CanUSA1981_2010, Daily.CanUSA1980_2020, DEM.WorldWide30sec, Gribs.HRDPS_daily_2019, nbProcesses=self.nbProcessesForWrappers)
        context4  = Context(Shore.Shore1, Normals.CanUSA1981_2010, Daily.CanUSA2020_2021, DEM.WorldWide30sec, Gribs.HRDPS_daily_2019, nbProcesses=self.nbProcessesForWrappers) 

        for context in [context1, context2, context3, context4]:  ### contexts with daily values
            finalDate = context.daily.getFinalDateYr();
            if finalDate > self.lastDailyDate:
                self.lastDailyDate = finalDate;
            wrapper = BioSimNormalsAndWeatherGeneratorWrapper(context)
            self.weatherGen.get(RCP.PastClimate).append(wrapper)
        
        for norm in pastClimateNormals:         ### those serve for the climate generation. The wrapper for the normals dict cannot be used since the weather generation interferes with the normals
            context = Context(Shore.Shore1, norm, None, DEM.WorldWide30sec, Gribs.HRDPS_daily_2019)
            wrapper = BioSimNormalsAndWeatherGeneratorWrapper(context)
            self.weatherGen.get(PastClimateGeneration).append(wrapper)
            
        for norm in hadley45:
            context = Context(Shore.Shore1, norm, None, DEM.WorldWide30sec, Gribs.HRDPS_daily_2019)
            wrapper = BioSimNormalsAndWeatherGeneratorWrapper(context)
            self.weatherGen.get(RCP.RCP45).get(ClimateModel.Hadley).append(wrapper)
        
        for norm in hadley85:
            context = Context(Shore.Shore1, norm, None, DEM.WorldWide30sec, Gribs.HRDPS_daily_2019)
            wrapper = BioSimNormalsAndWeatherGeneratorWrapper(context)
            self.weatherGen.get(RCP.RCP85).get(ClimateModel.Hadley).append(wrapper)

        for norm in rcm445:
            context = Context(Shore.Shore1, norm, None, DEM.WorldWide30sec, Gribs.HRDPS_daily_2019, nbProcesses=self.nbProcessesForWrappers)
            wrapper = BioSimNormalsAndWeatherGeneratorWrapper(context)
            self.weatherGen.get(RCP.RCP45).get(ClimateModel.RCM4).append(wrapper)

        for norm in rcm485:
            context = Context(Shore.Shore1, norm, None, DEM.WorldWide30sec, Gribs.HRDPS_daily_2019, nbProcesses=self.nbProcessesForWrappers)
            wrapper = BioSimNormalsAndWeatherGeneratorWrapper(context)
            self.weatherGen.get(RCP.RCP85).get(ClimateModel.RCM4).append(wrapper)

        for norm in gcm445:
            context = Context(Shore.Shore1, norm, None, DEM.WorldWide30sec, Gribs.HRDPS_daily_2019)
            wrapper = BioSimNormalsAndWeatherGeneratorWrapper(context)
            self.weatherGen.get(RCP.RCP45).get(ClimateModel.GCM4).append(wrapper)

        for norm in gcm485:
            context = Context(Shore.Shore1, norm, None, DEM.WorldWide30sec, Gribs.HRDPS_daily_2019)
            wrapper = BioSimNormalsAndWeatherGeneratorWrapper(context)
            self.weatherGen.get(RCP.RCP85).get(ClimateModel.GCM4).append(wrapper)
        
        self.models = dict()
        
        for modType in ModelType:
            model = Model(modType)
            self.models.__setitem__(modType, model)
        
        if Settings.ProductionMode:    
            print("Initiating updater thread...")
            UpdaterThread(self)
        print("Server initialized!")
    
    def getWrapperForWeatherGeneration(self, request : WeatherGeneratorRequest):
        '''
        Generates the proper list of BioSimNormalsAndWeatherGeneratorWrapper instances given the RCP and climate model.
        '''
        outputList = list()
        if request.isForceClimateGenerationEnabled():
            outputList.extend(self.weatherGen.get(PastClimateGeneration))
        else:    
            outputList.extend(self.weatherGen.get(RCP.PastClimate))
        if request.getRCP() != RCP.PastClimate:
            values = self.weatherGen.get(request.getRCP()).get(request.getClimateModel())
            outputList.extend(values)
        return outputList
                

    def setClimateModelsInDict(self, mapWithDict : bool):
        d = dict()
        for model in ClimateModel:
            if mapWithDict:
                d.__setitem__(model, dict())     
            else:
                d.__setitem__(model, list())     
        return d
    
    def processRequest(self, bioSimRequest : AbstractRequest):
        if isinstance(bioSimRequest, WeatherGeneratorRequest):
            if isinstance(bioSimRequest, WeatherGeneratorEpheremalRequest):
                model = self.models.get(bioSimRequest.mod)
                bioSimRequest.setVariables(model.getRequiredVariables())
            teleIODictList = TeleIODictList()
            wrapperList = self.getWrapperForWeatherGeneration(bioSimRequest)
            for wrapper in wrapperList:
                context = wrapper.getContext()
                if (bioSimRequest.doesThisContextMatch(context)):
                    wgl = wrapper.doProcess(bioSimRequest)
                    teleIODictList.add(wgl)
            return teleIODictList
        elif isinstance(bioSimRequest, ModelRequest):
            outputs = self.doProcessModelRequest(bioSimRequest)
            return outputs
        elif isinstance(bioSimRequest, NormalsRequest):   ### normal request
            shortNorm = bioSimRequest.getShortNormalsEnum()
            if shortNorm.isPastClimate():
                wrapper = self.normals.get(RCP.PastClimate).get(shortNorm)
            else:
                wrapper = self.normals.get(bioSimRequest.getRCP()).get(bioSimRequest.getClimateModel()).get(shortNorm)
            return wrapper.doProcess(bioSimRequest)
        else:
            raise Exception("Unknown request type!")
    

    def doProcessModelRequest(self, bioSimRequest:ModelRequest):
        model = self.models.get(bioSimRequest.mod)
        outputs = model.doProcess(bioSimRequest)
        return outputs




def do_job_thread(server : Server, tasks_to_accomplish : Queue, tasks_that_are_done : Queue):
    currentDay = time.gmtime().tm_yday
    while True:
        try:
            time.sleep(3600)
#            print("Checking time...")
            newCurrentDay = time.gmtime().tm_yday
            if (currentDay != newCurrentDay):
                print("Calling update...")
                tasks_to_accomplish.put(CurrentDailyHandler.getAlternativeCurrentDaily().value)  #### sends the destination folder to the process
                result = tasks_that_are_done.get()
                if result == "done":
                    CurrentDailyHandler.toggleCurrentDaily()
                    listWrapper = server.weatherGen.get(RCP.PastClimate)
                    listWrapper[len(listWrapper) - 1].respawn()
                    currentDay = newCurrentDay
        except:
            break;
    return True


def do_job_process(tasks_to_accomplish : Queue, tasks_that_are_done : Queue):
    while True:
        try:
            dailyFolder = tasks_to_accomplish.get()
            if dailyFolder[0:5] == "Daily":
                print("Downloading new database...")
                folder = UpdaterThread.updaterRootPath + "Weather" + os.path.sep + "DailyDump"
                UpdaterThread.deleteAllFilesInThisFolder(folder)
                command = UpdaterThread.updaterRootPath + "Mise_a_jour_meteo.bat" 
                subprocess.check_call(command, cwd=UpdaterThread.updaterRootPath)
    
                print("Extracting new database...")
                targetFolder = UpdaterThread.updaterRootPath + "Weather" + os.path.sep + dailyFolder
                UpdaterThread.deleteAllFilesInThisFolder(targetFolder)
                extension = ".zip"
                for item in os.listdir(folder): # loop through items in dir
                    if item.endswith(extension): # check for ".zip" extension
                        file_name = os.path.join(folder, item) # get full path of files
                        zip_ref = zipfile.ZipFile(file_name) # create zipfile object
                        zip_ref.extractall(targetFolder) # extract file to dir
                        zip_ref.close() # close file
            tasks_that_are_done.put("done")
        except Exception as ex:
            tasks_that_are_done.put("Error: " + str(ex))
    return True


class UpdaterThread():
    '''
    classdocs
    '''
    
    updaterRootPath = Settings.ROOT_DIR + "data" + os.path.sep 
    
    def __init__(self, server : Server):
        self.lastDay = time.gmtime()
        self.tasksToDo = Queue()
        self.tasksDone = Queue()
        self.p = Process(target=do_job_process, args = (self.tasksToDo, self.tasksDone))
        self.p.start()
        self.x = threading.Thread(target=do_job_thread, args = (server, self.tasksToDo, self.tasksDone))
        self.x.start()
        
    @staticmethod
    def deleteAllFilesInThisFolder(folder):
        for filename in os.listdir(folder):
            file_path = os.path.join(folder, filename)
            try:
                if os.path.isfile(file_path) or os.path.islink(file_path):
                    os.remove(file_path)
                elif os.path.isdir(file_path):
                    shutil.rmtree(file_path) 
            except Exception as e:
                print('Failed to delete %s. Reason: %s' % (file_path, e))
