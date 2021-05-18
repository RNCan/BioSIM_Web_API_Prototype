'''
Provides different enums 
    to describe the context of a BioSim instance for weather generation
    to describe the different models

@author: M. Fortin and R. Saint-Amant, Canadian Forest Service, August 2020
@copyright: Her Majesty the Queen in right of Canada
'''
from enum import Enum
from math import floor
from nt import listdir, write
from os import path
import os


class Settings():
    
    Verbose = True
    ProductionMode = False 
    MultiprocessMode = False
    nbMaxCoordinatesNormals = 50
    nbMaxCoordinatesWG = 10
    UpdaterEnabled = False
    MinimalConfiguration = True
    ROOT_DIR = os.path.dirname(os.path.abspath(__file__)) + os.path.sep

    '''
    Set the settings of the API. 
    @param d: the app.config dictionary 
    '''
    @staticmethod
    def setSettings(d : dict):  
        if d.__contains__("VERBOSE"):
            Settings.Verbose = d["VERBOSE"]
        if d.__contains__("PRODUCTION_MODE"):
            Settings.ProductionMode = d["PRODUCTION_MODE"]
        if d.__contains__("MULTIPROCESS_MODE"):
            Settings.MultiprocessMode = d["MULTIPROCESS_MODE"]
        if d.__contains__("NB_MAX_COORDINATES_NORMALS"):
            Settings.nbMaxCoordinatesNormals = d["NB_MAX_COORDINATES_NORMALS"]
        if d.__contains__("NB_MAX_COORDINATES_WG"):
            Settings.nbMaxCoordinatesWG = d["NB_MAX_COORDINATES_WG"]
        if d.__contains__("UPDATER_ENABLED"):
            Settings.UpdaterEnabled = d["UPDATER_ENABLED"]
        if d.__contains__("MINIMAL_CONFIG"):
            Settings.MinimalConfiguration = d["MINIMAL_CONFIG"]

    @staticmethod
    def updateGribsRegistry():
        if Settings.Verbose:
            print("Updating Gribs registry...")
        gribsPath = Settings.ROOT_DIR + "data" + path.sep + "Weather" + path.sep + "Gribs";
        allTIFFiles = [f for f in listdir(gribsPath) if f.lower().endswith(".tif")]
        gribsRegistry = open(gribsPath + path.sep + "HRDPS daily.Gribs", "w")
        gribsRegistry.write("TRef,FilePath\n")
        for f in allTIFFiles:
            year = f[7:11]
            month = f[11:13]
            day = f[13:15]
            gribsRegistry.write(year + "-" + month + "-" + day + ",." + path.sep + f + "\n")
        gribsRegistry.close()
        if Settings.Verbose:
            print("Gribs registry successfully updated!")
        
        
        
class CurrentDaily(Enum):
    Simple = "DailyLatest"
    Alternative = "DailyLatestAlt"

class CurrentDailyHandler():
    currentDaily = CurrentDaily.Simple

    @staticmethod
    def toggleCurrentDaily():
        CurrentDailyHandler.currentDaily = CurrentDailyHandler.getAlternativeCurrentDaily()

    @staticmethod
    def getAlternativeCurrentDaily():
        if (CurrentDailyHandler.currentDaily == CurrentDaily.Simple):
            return CurrentDaily.Alternative
        else:
            return CurrentDaily.Simple


class ModelType(Enum):
    '''
    An enum variable that stands for a particular model in BioSIM
    '''
    ASCE_ETc_Daily = ["ASCE-ETc (Daily).mdl", 5]
    ASCE_ETcEx_Daily = ["ASCE-ETcEx (Daily).mdl", 5]
    ASCE_ETsz_Daily = ["ASCE-ETsz (Daily).mdl", 5]
    BlueStainIndex = ["BlueStainIndex.mdl", 3]
    BlueStainVariables = ["BlueStainVariables.mdl", 7]
    BudBurst = ["BudBurst.mdl", 4]
    CCBio_Annual = ["CCBio (Annual).mdl", 5]
    CCBio_Monthly = ["CCBio (Monthly).mdl", 5]
    Climate_Moisture_Index_Monthly = ["Climate Moisture Index (Monthly).mdl", 3]
    Climate_Mosture_Index_Annual = ["Climate Mosture Index (Annual).mdl", 3]
    Climatic_Annual = ["Climatic (Annual).mdl", 5]
    Climatic_Daily = ["Climatic (Daily).mdl", 5]
    Climatic_Monthly = ["Climatic (Monthly).mdl", 5]
    ClimaticEx_Daily = ["ClimaticEx (Daily).mdl", 5]
    ClimaticQc_Annual = ["ClimaticQc (Annual).mdl", 7]
    ClimaticWind_Annual = ["ClimaticWind (Annual).mdl", 3]
    ClimaticWind_Monthly = ["ClimaticWind (Monthly).mdl", 3]
#    Climdex_Annual = "Climdex (Annual).mdl"                              ### the base period is not inside the simulation period
#    Climdex_Monthly = "Climdex (Monthly).mdl"                            ### the base period is not inside the simulation period
    DegreeDay_Annual = ["DegreeDay (Annual).mdl", 9]
    DegreeDay_Daily = ["DegreeDay (Daily).mdl", 9]
    DegreeDay_Monthly = ["DegreeDay (Monthly).mdl", 9]
    EmeraldAshBorer = ["EmeraldAshBorer.mdl", 3]
    EmeraldAshBorerColdHardiness_Annual = ["EmeraldAshBorerColdHardiness (Annual).mdl", 1]
    EuropeanElmScale = ["EuropeanElmScale.mdl", 2]
    FallCankerworms = ["FallCankerworms.mdl", 3]
#    ForestTentCaterpillar = "ForestTentCaterpillar.mdl"                    ### Causes an exception from time to time
    FWI_Annual = ["FWI (Annual).mdl", 8]
    FWI_Daily = ["FWI (Daily).mdl", 8]
    FWI_Monthly = ["FWI (Monthly).mdl", 8]
    FWI_Drought_Code_Daily = ["FWI Drought Code (Daily).mdl", 8]
    FWI_Drought_Code_Monthly = ["FWI Drought Code (Monthly).mdl", 8]
    FWI_Drought_Code_Fixe_Daily = ["FWI Drought Code-Fixe (Daily).mdl", 8]
    FWI_Drought_Code_Fixe_Monthly = ["FWI Drought Code-Fixe (Monthly).mdl", 8]
    FWI_Fixed_Annual = ["FWI-Fixed (Annual).mdl", 8]
    FWI_Fixed_Daily = ["FWI-Fixed (Daily).mdl", 8]
    FWI_Fixed_Monthly = ["FWI-Fixed (Monthly).mdl", 8]
    GrowingSeason = ["GrowingSeason.mdl", 8]
    Gypsy_Moth_Seasonality = ["Gypsy Moth Seasonality.mdl", 9]
    Gypsy_Moth_Stability = ["Gypsy Moth Stability.mdl", 2]
    HemlockLooper = ["HemlockLooper.mdl", 9]
    HemlockLooperRemi = ["HemlockLooperRemi.mdl", 1]
    HemlockWoollyAdelgid_Annual = ["HemlockWoollyAdelgid (Annual).mdl", 5]
    HemlockWoollyAdelgid_Daily = ["HemlockWoollyAdelgid (Daily).mdl", 5]
#    HWA_Phenology = "HWA Phenology.mdl"                                       ### Causes an exception from time to time
#    Insect_Development_Database_II = "Insect Development Database II.mdl"     ### Always causes an exception 
#    Insect_Development_Database_III = "Insect Development Database III.mdl"   ### Always causes an exception
    Jackpine_Budworm = ["Jackpine Budworm.mdl", 9]
    LaricobiusNigrinus = ["LaricobiusNigrinus.mdl", 5]
    MPB_Cold_Tolerance_Annual = ["MPB Cold Tolerance (Annual).mdl", 5]       ### ArrayIndexOutOfBoundsException
    MPB_Cold_Tolerance_Daily = ["MPB Cold Tolerance (Daily).mdl", 5]
    MPB_SLR = ["MPB-SLR.mdl", 7]
    ObliqueBandedLeafroller = ["ObliqueBandedLeafroller.mdl", 5]
#    PlantHardiness = "PlantHardiness.mdl"                                      ### Bad number of parameters
    PlantHardinessCanada = ["PlantHardinessCanada.mdl", 5]
    PlantHardinessUSA = ["PlantHardinessUSA.mdl", 5]
    Potential_Evapotranspiration_Annual = ["Potential Evapotranspiration (Annual).mdl", 7]
    Potential_Evapotranspiration_Daily = ["Potential Evapotranspiration (Daily).mdl", 7]
    Potential_Evapotranspiration_Monthly = ["Potential Evapotranspiration (Monthly).mdl", 7]
    Potential_Evapotranspiration_Ex_Annual = ["Potential Evapotranspiration Ex (Annual).mdl", 7]
    Potential_Evapotranspiration_Ex_Daily = ["Potential Evapotranspiration Ex (Daily).mdl", 7]
    Potential_Evapotranspiration_Ex_Monthly = ["Potential Evapotranspiration Ex (Monthly).mdl", 7]
    ReverseDegreeDay_Annual = ["ReverseDegreeDay (Annual).mdl", 3]
    ReverseDegreeDay_Overall_years = ["ReverseDegreeDay (Overall years).mdl", 3]
    SiteIndexClimate = ["SiteIndexClimate.mdl", 3]
    SnowMelt_Monthly = ["SnowMelt (Monthly).mdl", 3]
    Soil_Moisture_Index_Annual = ["Soil Moisture Index (Annual).mdl", 3]
    Soil_Moisture_Index_Daily = ["Soil Moisture Index (Daily).mdl", 3]
    Soil_Moisture_Index_Monthly = ["Soil Moisture Index (Monthly).mdl", 3]
    Soil_Moisture_Index_QL_Annual = ["Soil Moisture Index QL(Annual).mdl", 3]
    Soil_Moisture_Index_QL_Daily = ["Soil Moisture Index QL(Daily).mdl", 3]
    Soil_Moisture_Index_QL_Monthly = ["Soil Moisture Index QL(Monthly).mdl", 3]
    SpringCankerworms = ["SpringCankerworms.mdl", 3]
    Spruce_Budworm_Biology_Annual = ["Spruce Budworm Biology (Annual).mdl", 9]
    Spruce_Budworm_Biology = ["Spruce Budworm Biology.mdl", 9]
#    Spruce_Budworm_Dispersal = "Spruce Budworm Dispersal.mdl"                ### encoding causes an exception between Python and C++
    Spruce_Budworm_Manitoba = ["Spruce Budworm Manitoba.mdl", 3]
    SpruceBeetle = ["SpruceBeetle.mdl", 3]                                ### ArrayIndexOutOfBoundsException
    Standardised_Precipitation_Evapotranspiration_Index = ["Standardised Precipitation Evapotranspiration Index.mdl", 7]
    TminTairTmax_Daily = ["TminTairTmax (Daily).mdl", 5]
    Tranosema_OBL_SBW_daily = ["Tranosema-OBL-SBW (daily).mdl", 5]
    VaporPressureDeficit_Annual = ["VaporPressureDeficit (Annual).mdl", 5]
    VaporPressureDeficit_Daily = ["VaporPressureDeficit (Daily).mdl", 5]
    VaporPressureDeficit_Monthly = ["VaporPressureDeficit (Monthly).mdl", 5]
    Western_Spruce_Budworm_annual = ["Western Spruce Budworm (annual).mdl", 5]
    Western_Spruce_Budworm = ["Western Spruce Budworm.mdl", 9]
    WhitemarkedTussockMoth = ["WhitemarkedTussockMoth.mdl", 5]
    WhitePineWeevil = ["WhitePineWeevil.mdl", 5]
    Yellowheaded_Spruce_Sawfly = ["Yellowheaded Spruce Sawfly.mdl", 9]

       
    def getPath(self):
        return Settings.ROOT_DIR + "models" + path.sep + self.value[0]

    def getNbProcesses(self):
        if Settings.MultiprocessMode:
            nb = floor(self.value[1] / 2) 
            if nb == 0:
                nb = 1
            if Settings.ProductionMode:  ### then use the maximum number of processes
                return nb
            else:       ### in development mode, then limit the maximum number of processes to 2
                if nb > 2:
                    return 2
                else:
                    return nb
        else:
            return 1
    
    def isMultiProcessEnabled(self):
        return self.getNbProcesses() > 1
    
    def getName(self):
        return self.value[0]

class Shore(Enum):
    Shore1 = "Shore.ann"

    def getCommand(self):
        return "Shore=" + Settings.ROOT_DIR + "data" + path.sep + "Layers" + path.sep + self.value



class RCP(Enum):
    PastClimate = "PastClimate"
    RCP45 = "RCP45"
    RCP85 = "RCP85"

    def getCommandPart(self):
        if self == RCP.PastClimate:
            return ".NormalsDB"
        else:
            return self.value + ".NormalsDB"



class ClimateModel(Enum):
    Hadley = "Hadley GEM2-ES"
    GCM4 = "GCM4_ESM2_1850-2100"
    RCM4 = "RCM4_ESM2_22km"
    
class ShortNormals(Enum):
    CanUSA1941_1970 = ["1941_1970", True]
    CanUSA1951_1980 = ["1951_1980", True]
    CanUSA1961_1990 = ["1961_1990", True]
    CanUSA1971_2000 = ["1971_2000", True] 
    CanUSA1981_2010 = ["1981_2010", True]
    CanUSA1991_2020 = ["1991_2020", False]
    CanUSA2001_2030 = ["2001_2030", False]
    CanUSA2011_2040 = ["2011_2040", False]
    CanUSA2021_2050 = ["2021_2050", False]
    CanUSA2031_2060 = ["2031_2060", False]
    CanUSA2041_2070 = ["2041_2070", False]
    CanUSA2051_2080 = ["2051_2080", False]
    CanUSA2061_2090 = ["2061_2090", False]
    CanUSA2071_2100 = ["2071_2100", False]
   
    def isPastClimate(self):
        return self.value[1]
    
    def getBasicString(self):
        return self.value[0]
    
    
    
class Normals(Enum):
    
    ### Hadley model + RCP 4.5
    CanUSA2071_2100Hadley45 = ["Canada-USA 2071-2100", 2081, 2100, ClimateModel.Hadley, RCP.RCP45, ShortNormals.CanUSA2071_2100]
    CanUSA2061_2090Hadley45 = ["Canada-USA 2061-2090", 2071, 2080, ClimateModel.Hadley, RCP.RCP45, ShortNormals.CanUSA2061_2090]
    CanUSA2051_2080Hadley45 = ["Canada-USA 2051-2080", 2061, 2070, ClimateModel.Hadley, RCP.RCP45, ShortNormals.CanUSA2051_2080]
    CanUSA2041_2070Hadley45 = ["Canada-USA 2041-2070", 2051, 2060, ClimateModel.Hadley, RCP.RCP45, ShortNormals.CanUSA2041_2070]
    CanUSA2031_2060Hadley45 = ["Canada-USA 2031-2060", 2041, 2050, ClimateModel.Hadley, RCP.RCP45, ShortNormals.CanUSA2031_2060]
    CanUSA2021_2050Hadley45 = ["Canada-USA 2021-2050", 2031, 2040, ClimateModel.Hadley, RCP.RCP45, ShortNormals.CanUSA2021_2050]
    CanUSA2011_2040Hadley45 = ["Canada-USA 2011-2040", 2021, 2030, ClimateModel.Hadley, RCP.RCP45, ShortNormals.CanUSA2011_2040]
    CanUSA2001_2030Hadley45 = ["Canada-USA 2001-2030", 2011, 2020, ClimateModel.Hadley, RCP.RCP45, ShortNormals.CanUSA2001_2030]
    CanUSA1991_2020Hadley45 = ["Canada-USA 1991-2020", 2001, 2010, ClimateModel.Hadley, RCP.RCP45, ShortNormals.CanUSA1991_2020]

    ### Hadley model + RCP 8.5
    CanUSA2071_2100Hadley85 = ["Canada-USA 2071-2100", 2081, 2100, ClimateModel.Hadley, RCP.RCP85, ShortNormals.CanUSA2071_2100]
    CanUSA2061_2090Hadley85 = ["Canada-USA 2061-2090", 2071, 2080, ClimateModel.Hadley, RCP.RCP85, ShortNormals.CanUSA2061_2090]
    CanUSA2051_2080Hadley85 = ["Canada-USA 2051-2080", 2061, 2070, ClimateModel.Hadley, RCP.RCP85, ShortNormals.CanUSA2051_2080]
    CanUSA2041_2070Hadley85 = ["Canada-USA 2041-2070", 2051, 2060, ClimateModel.Hadley, RCP.RCP85, ShortNormals.CanUSA2041_2070]
    CanUSA2031_2060Hadley85 = ["Canada-USA 2031-2060", 2041, 2050, ClimateModel.Hadley, RCP.RCP85, ShortNormals.CanUSA2031_2060]
    CanUSA2021_2050Hadley85 = ["Canada-USA 2021-2050", 2031, 2040, ClimateModel.Hadley, RCP.RCP85, ShortNormals.CanUSA2021_2050]
    CanUSA2011_2040Hadley85 = ["Canada-USA 2011-2040", 2021, 2030, ClimateModel.Hadley, RCP.RCP85, ShortNormals.CanUSA2011_2040]
    CanUSA2001_2030Hadley85 = ["Canada-USA 2001-2030", 2011, 2020, ClimateModel.Hadley, RCP.RCP85, ShortNormals.CanUSA2001_2030]
    CanUSA1991_2020Hadley85 = ["Canada-USA 1991-2020", 2001, 2010, ClimateModel.Hadley, RCP.RCP85, ShortNormals.CanUSA1991_2020]

    ### GCM4 model + RCP 4.5
    CanUSA2071_2100RCM445 = ["Canada-USA 2071-2100", 2081, 2100, ClimateModel.RCM4, RCP.RCP45, ShortNormals.CanUSA2071_2100]
    CanUSA2061_2090RCM445 = ["Canada-USA 2061-2090", 2071, 2080, ClimateModel.RCM4, RCP.RCP45, ShortNormals.CanUSA2061_2090]
    CanUSA2051_2080RCM445 = ["Canada-USA 2051-2080", 2061, 2070, ClimateModel.RCM4, RCP.RCP45, ShortNormals.CanUSA2051_2080]
    CanUSA2041_2070RCM445 = ["Canada-USA 2041-2070", 2051, 2060, ClimateModel.RCM4, RCP.RCP45, ShortNormals.CanUSA2041_2070]
    CanUSA2031_2060RCM445 = ["Canada-USA 2031-2060", 2041, 2050, ClimateModel.RCM4, RCP.RCP45, ShortNormals.CanUSA2031_2060]
    CanUSA2021_2050RCM445 = ["Canada-USA 2021-2050", 2031, 2040, ClimateModel.RCM4, RCP.RCP45, ShortNormals.CanUSA2021_2050]
    CanUSA2011_2040RCM445 = ["Canada-USA 2011-2040", 2021, 2030, ClimateModel.RCM4, RCP.RCP45, ShortNormals.CanUSA2011_2040]
    CanUSA2001_2030RCM445 = ["Canada-USA 2001-2030", 2011, 2020, ClimateModel.RCM4, RCP.RCP45, ShortNormals.CanUSA2001_2030]
    CanUSA1991_2020RCM445 = ["Canada-USA 1991-2020", 2001, 2010, ClimateModel.RCM4, RCP.RCP45, ShortNormals.CanUSA1991_2020]

    ### RCM4 model + RCP 8.5
    CanUSA2071_2100RCM485 = ["Canada-USA 2071-2100", 2081, 2100, ClimateModel.RCM4, RCP.RCP85, ShortNormals.CanUSA2071_2100]
    CanUSA2061_2090RCM485 = ["Canada-USA 2061-2090", 2071, 2080, ClimateModel.RCM4, RCP.RCP85, ShortNormals.CanUSA2061_2090]
    CanUSA2051_2080RCM485 = ["Canada-USA 2051-2080", 2061, 2070, ClimateModel.RCM4, RCP.RCP85, ShortNormals.CanUSA2051_2080]
    CanUSA2041_2070RCM485 = ["Canada-USA 2041-2070", 2051, 2060, ClimateModel.RCM4, RCP.RCP85, ShortNormals.CanUSA2041_2070]
    CanUSA2031_2060RCM485 = ["Canada-USA 2031-2060", 2041, 2050, ClimateModel.RCM4, RCP.RCP85, ShortNormals.CanUSA2031_2060]
    CanUSA2021_2050RCM485 = ["Canada-USA 2021-2050", 2031, 2040, ClimateModel.RCM4, RCP.RCP85, ShortNormals.CanUSA2021_2050]
    CanUSA2011_2040RCM485 = ["Canada-USA 2011-2040", 2021, 2030, ClimateModel.RCM4, RCP.RCP85, ShortNormals.CanUSA2011_2040]
    CanUSA2001_2030RCM485 = ["Canada-USA 2001-2030", 2011, 2020, ClimateModel.RCM4, RCP.RCP85, ShortNormals.CanUSA2001_2030]
    CanUSA1991_2020RCM485 = ["Canada-USA 1991-2020", 2001, 2010, ClimateModel.RCM4, RCP.RCP85, ShortNormals.CanUSA1991_2020]

    ### GCM4 model + RCP 4.5
    CanUSA2071_2100GCM445 = ["Canada-USA 2071-2100", 2081, 2100, ClimateModel.GCM4, RCP.RCP45, ShortNormals.CanUSA2071_2100]
    CanUSA2061_2090GCM445 = ["Canada-USA 2061-2090", 2071, 2080, ClimateModel.GCM4, RCP.RCP45, ShortNormals.CanUSA2061_2090]
    CanUSA2051_2080GCM445 = ["Canada-USA 2051-2080", 2061, 2070, ClimateModel.GCM4, RCP.RCP45, ShortNormals.CanUSA2051_2080]
    CanUSA2041_2070GCM445 = ["Canada-USA 2041-2070", 2051, 2060, ClimateModel.GCM4, RCP.RCP45, ShortNormals.CanUSA2041_2070]
    CanUSA2031_2060GCM445 = ["Canada-USA 2031-2060", 2041, 2050, ClimateModel.GCM4, RCP.RCP45, ShortNormals.CanUSA2031_2060]
    CanUSA2021_2050GCM445 = ["Canada-USA 2021-2050", 2031, 2040, ClimateModel.GCM4, RCP.RCP45, ShortNormals.CanUSA2021_2050]
    CanUSA2011_2040GCM445 = ["Canada-USA 2011-2040", 2021, 2030, ClimateModel.GCM4, RCP.RCP45, ShortNormals.CanUSA2011_2040]
    CanUSA2001_2030GCM445 = ["Canada-USA 2001-2030", 2011, 2020, ClimateModel.GCM4, RCP.RCP45, ShortNormals.CanUSA2001_2030]
    CanUSA1991_2020GCM445 = ["Canada-USA 1991-2020", 2001, 2010, ClimateModel.GCM4, RCP.RCP45, ShortNormals.CanUSA1991_2020]

    ### GCM4 model + RCP 8.5
    CanUSA2071_2100GCM485 = ["Canada-USA 2071-2100", 2081, 2100, ClimateModel.GCM4, RCP.RCP85, ShortNormals.CanUSA2071_2100]
    CanUSA2061_2090GCM485 = ["Canada-USA 2061-2090", 2071, 2080, ClimateModel.GCM4, RCP.RCP85, ShortNormals.CanUSA2061_2090]
    CanUSA2051_2080GCM485 = ["Canada-USA 2051-2080", 2061, 2070, ClimateModel.GCM4, RCP.RCP85, ShortNormals.CanUSA2051_2080]
    CanUSA2041_2070GCM485 = ["Canada-USA 2041-2070", 2051, 2060, ClimateModel.GCM4, RCP.RCP85, ShortNormals.CanUSA2041_2070]
    CanUSA2031_2060GCM485 = ["Canada-USA 2031-2060", 2041, 2050, ClimateModel.GCM4, RCP.RCP85, ShortNormals.CanUSA2031_2060]
    CanUSA2021_2050GCM485 = ["Canada-USA 2021-2050", 2031, 2040, ClimateModel.GCM4, RCP.RCP85, ShortNormals.CanUSA2021_2050]
    CanUSA2011_2040GCM485 = ["Canada-USA 2011-2040", 2021, 2030, ClimateModel.GCM4, RCP.RCP85, ShortNormals.CanUSA2011_2040]
    CanUSA2001_2030GCM485 = ["Canada-USA 2001-2030", 2011, 2020, ClimateModel.GCM4, RCP.RCP85, ShortNormals.CanUSA2001_2030]
    CanUSA1991_2020GCM485 = ["Canada-USA 1991-2020", 2001, 2010, ClimateModel.GCM4, RCP.RCP85, ShortNormals.CanUSA1991_2020]
    
    ### Past climate
    CanUSA1981_2010 = ["Canada-USA 1981-2010", 1991, 2000, ClimateModel.RCM4, RCP.PastClimate, ShortNormals.CanUSA1981_2010]
    CanUSA1971_2000 = ["Canada-USA 1971-2000", 1981, 1990, ClimateModel.RCM4, RCP.PastClimate, ShortNormals.CanUSA1971_2000]
    CanUSA1961_1990 = ["Canada-USA 1961-1990", 1971, 1980, ClimateModel.RCM4, RCP.PastClimate, ShortNormals.CanUSA1961_1990]
    CanUSA1951_1980 = ["Canada-USA 1951-1980", 1961, 1970, ClimateModel.RCM4, RCP.PastClimate, ShortNormals.CanUSA1951_1980]
    CanUSA1941_1970 = ["Canada-USA 1941-1970", 1951, 1960, ClimateModel.RCM4, RCP.PastClimate, ShortNormals.CanUSA1941_1970]

    def getPath(self):
        if self.value[4] == RCP.PastClimate:
            return Settings.ROOT_DIR + "data" + path.sep + "Weather" + path.sep + "Normals" + path.sep + self.value[0] + self.value[4].getCommandPart()
        else:
            return Settings.ROOT_DIR + "data" + path.sep + "Weather" + path.sep + "Normals" + path.sep + self.value[0] + " " + self.value[3].value + "_"  + self.value[4].getCommandPart()

    def getCommand(self):
        return "Normals=" + self.getPath()
    
    def getInitialDateYr(self): 
        return self.value[1]
    
    def getFinalDateYr(self):
        return self.value[2]
    
    def getShortNormals(self):
        return self.value[5]
    
    
class Daily(Enum):
    CanUSA2020_2021 = ["Canada-USA 2020-2021.DailyDB", 2020, 2021]
    CanUSA1980_2020 = ["Canada-USA 1980-2020.DailyDB", 1980, 2019]
    CanUSA1950_1980 = ["Canada-USA 1950-1980.DailyDB", 1950, 1979]
    CanUSA1900_1950 = ["Canada-USA 1900-1950.DailyDB", 1900, 1949]

    def getPath(self):
        if (self == Daily.CanUSA2020_2021):
            dailyFolderName = CurrentDailyHandler.currentDaily.value  ### this variable set the path to either the DailyLatest or the DailyLatestAlt directory
        else:
            dailyFolderName = "Daily" 
        return Settings.ROOT_DIR + "data" + path.sep + "Weather" + path.sep + dailyFolderName + path.sep + self.value[0]

    def getCommand(self):
        return "Daily=" + self.getPath()
    
    def getInitialDateYr(self): 
        return self.value[1]
    
    def getFinalDateYr(self):
        return self.value[2]
    
        
class DEM(Enum):
    WorldWide30sec = "Monde_30s(SRTM30).tif"
    
    def getCommand(self):
        return "DEM=" + Settings.ROOT_DIR + "data" + path.sep + "DEM" + path.sep + self.value


class Gribs(Enum):
    HRDPS_daily = "HRDPS daily.Gribs"

    def getCommand(self):
        return "Gribs=" + Settings.ROOT_DIR + "data" + path.sep + "Weather" + path.sep + "Gribs" + path.sep + self.value


class Context:
    '''
    classdocs
    '''

    def __init__(self, shore : Shore, normals : Normals, daily : Daily, dem : DEM, gribs : Gribs, nbProcesses = 1):
        '''
        Constructor
        '''
        self.shore = shore
        self.normals = normals
        self.daily = daily
        self.dem = dem
        self.gribs = gribs
        self.nbProcesses = nbProcesses
          
    def getContextName(self):
        if self.daily != None:
            return self.shore.name + "-" + self.normals.name + "-" + self.daily.name + "-" + self.dem.name + "-" + self.gribs.name
        else:
            return self.shore.name + "-" + self.normals.name + "-" + self.dem.name + "-" + self.gribs.name
    
    def getNbProcesses(self):
        return self.nbProcesses
    
    def isMultiProcessEnabled(self):
        return self.getNbProcesses() > 1
    
    def getInitializationString(self):
        initializationString = self.shore.getCommand() + "&" + self.normals.getCommand() + "&" + self.dem.getCommand() + "&" + self.gribs.getCommand()
        if self.daily != None:
            initializationString += "&" + self.daily.getCommand()
        return initializationString
     
    def getMatchInThisInterval(self, initDateYr, finalDateYr, isFromObservation): 
        if isFromObservation and self.daily != None:  ### then tries to retrieve the daily db   
            selectedEnum = self.daily
        else:
            selectedEnum = self.normals 
        return Context.getBounds(selectedEnum, initDateYr, finalDateYr)
    

    @staticmethod
    def getBounds(enumVar, initYr, finalYr):
        if initYr > enumVar.getFinalDateYr(): ### Both the initial and final dates lay beyond the upper bound
            return None
        elif initYr >= enumVar.getInitialDateYr():  ### the initial date is in
            if finalYr >= enumVar.getFinalDateYr(): ### only the initial date is in
                return [initYr, enumVar.getFinalDateYr()]
            elif finalYr >= enumVar.getInitialDateYr():  ### both the initial and the final dates are in 
                return [initYr, finalYr]
            else:
                return None ### Both the initial and the final dates are below the lower bound
        elif initYr < enumVar.getInitialDateYr():  ### the initial date is below the lower bound
            if finalYr >= enumVar.getFinalDateYr(): ### the interval is larger than the bounds
                return [enumVar.getInitialDateYr(), enumVar.getFinalDateYr()]
            elif finalYr >= enumVar.getInitialDateYr():  ### only the final date is within the bounds
                return [enumVar.getInitialDateYr(), finalYr]
            else:
                return None ### Both the initial and the final dates are below the lower bound
