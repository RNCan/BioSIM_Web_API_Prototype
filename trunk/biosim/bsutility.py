'''
A module that contains utility classes

@author: M. Fortin and R. Saint-Amant, Canadian Forest Service, August 2020
@copyright: Her Majesty the Queen in right of Canada
'''
import biosim.biosimdll.BioSIM_API as BioSIM_API

class BioSimUtility():
    '''
    A class with static methods for utility
    '''

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