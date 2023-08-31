"""
# Library of complementary tools for the OrcaFlex API (OrcFxAPI)
#
#
#
"""
from __future__ import annotations

__author__ = "NSG Engenharia"
__copyright__ = "Copyright 2023"
__credits__ = ["Gabriel Nascimento"]
__license__ = "GPL"
__version__ = "1.0.0"
__maintainer__ = "Gabriel Nascimento"
__email__ = "gabriel.nascimento@nsgeng.com"
__status__ = "Development"


from typing import Union
import ctypes
import OrcFxAPI as orc

from NsgOrcFx.classes import *
from NsgOrcFx.sortlines import *
from NsgOrcFx.objauxfuncs import *
import NsgOrcFx.environment as envtools


# ======= CONSTANTS ======== #
requiredOrcFxVer = '11.3a'

# ==== AUXILIARY METHODS ==== #
class AuxFuncs:
    def checkOrCreateFolder(self, path: str) -> bool:
        """
        Check if the folder exists and, case not, try to create
        Returns false if don't exists and can't create
        """
        return afCheckOrCreateFolder(path)

auxfuncs = AuxFuncs()

# ==== MODEL CLASS ==== #
class Model(orc.Model):
    general: OrcaFlexGeneralObject
    auxfuncs = auxfuncs
   
    def __checkOrcaFlexVersion(self) -> bool:
        """Return True if the installed version of OrcaFlex is equal or newer than the required"""
        if not checkOrcaFlexVersion(requiredOrcFxVer):
            raise Exception(f'The OrcaFlex version is older then {requiredOrcFxVer}.')    

    def getOrcaVersion() -> str:
        """Return the installed OrcaFlex version as string"""
        return getOrcaVersion()

    def __getitem__(self, name: str) -> OrcaFlexObject:
        return OrcaFlexObject(super().__getitem__(name)) 
    
    def findLineByName(self, name: str) -> OrcaFlexLineObject:
        """Find a line object by its name"""
        obj = self[name]
        return OrcaFlexLineObject(obj)
    
    def getAllLines(self) -> LineSelection:
        """Returns a list of all line objects"""
        lineList = LineSelection(self)
        for obj in self.objects:
            if obj.type == orc.ObjectType.Line:
                lineList.append(OrcaFlexLineObject(obj))
        return lineList

    def getLineList(
            self, 
            groupName: Union[str, None] = None, 
            includeSubgroups: bool = False
            ) -> LineSelection:
        """
        Returns all lines in the model which belongs to the defined group with or not its subgroups
        """            
        # if groupName:
        #     grouObj = self[groupName]
        #     selectedList = list(grouObj.GroupChildren(recurse=includeSubgroups))
        # else:
        #     selectedList = list(self.objects)

        # for obj in selectedList:
        #     if obj.type == orc.ObjectType.Line:
        #         result.append(OrcaFlexLineObject(obj))
        #     # elif groupName and includeSubgroups and obj.type == orc.ObjectType.BrowserGroup:
        #     #     result.extend(self.getLineList(obj.Name))
        result = LineSelection(self)
        getLinesToList(self, groupName, includeSubgroups, result)
        return result
    
    def sortPathInterconnectedLines(
            self,
            lineList: list[OrcaFlexLineObject]
            ) -> LineSelection:
        """
        Returns a sorted list of interconnected lines, based on its connections (e.g., path from first to last)
        The result is unpredictable if not all lines are connected or if there are connection between more than two lines
        """              
        newList = sortPathInterconnectedLines(lineList)
        returnList = LineSelection(self)
        for obj in newList: returnList.append(obj)
        return returnList
    

    def getUnconnectedConstraints(self) -> list[OrcaFlexObject]:
        """
        Returns the list of constraints to which there is not a line connected
        """
        constraintChildren = {}
        for obj in self.objects:
            if obj.type == orc.ObjectType.Constraint:
                constraintChildren[obj.name] = 0
        
        lines = self.getLineList()  
        for line in lines:
            for endObj in [line.EndAConnection, line.EndBConnection]:
                if endObj in constraintChildren:
                    constraintChildren[endObj] += 1

        resultList = []
        for constraint, n in constraintChildren.items():
            if n == 0:
                resultList.append(constraint)

        return resultList
    
    def deleteObjs(self, objects: list[str | OrcaFlexObject]):
        for obj in objects:
            self.DestroyObject(obj)



class LineSelection(list[OrcaFlexLineObject]):
    def __init__(self, model: Model):
        super().__init__()
        self.model = model

    def setGroup(self, groupName: str) -> None:
        group = self.model[groupName]
        for line in self:
            line.groupParent = group

    def setLog(self, logResults: bool) -> None:
        """Defines if the results of the line should be stored (logged) or not for all lines in this selection"""
        for line in self:
            line.setLog(logResults)

    def setMeshSize(
            self,
            nSegs: int = None,
            targetLength: float = None
            ):
        """Set the length/number of segments for all sections of all lines in this selection"""
        for line in self:
            line.setMeshSize(nSegs, targetLength)

    def selectByName(
            self, 
            name: Union[str, list[str]]
            ) -> LineSelection:
        if type(name) == str: nameList = [name]
        else: nameList = name
        resultList = LineSelection(self.model)
        for line in self:
            if line.Name in nameList:
                resultList.append(line)
        return resultList

    def selectByType(
            self, lineType: Union[list[str], str], 
            partialMatch: bool = False
            ) -> LineSelection:
        if type(lineType) == str: lineTypeGroup = [lineType]
        else: lineTypeGroup = lineType
        resultList = LineSelection(self.model)
        for line in self:
            for lt in line.LineType:
                if strInStrList(lt, lineTypeGroup, partialMatch):
                    resultList.append(line)
        return resultList

    def selectLinesByPosition(
            self,
            xLimits: tuple[Union[float,None], Union[float,None]] = (None, None),
            yLimits: tuple[Union[float,None], Union[float,None]] = (None, None),
            zLimits: tuple[Union[float,None], Union[float,None]] = (None, None)
            ) -> LineSelection:
        """
        Select lines in the model based on its ends position
        """
        if not len(self):
            raise Exception('Error! This selction is empty.')

        # cloneModel = orc.Model() # creates a 'dummy' model (only to set fixed connections and get global coords)
        resultList = LineSelection(self.model)
        for line in self:
            # clone = line.CreateClone(model=cloneModel) # copy object to 'dummy' model
            clone = line.CreateClone() # copy object to 'dummy' model
            clone.EndAConnection = 'Fixed' # ensures global coordinates
            clone.EndBConnection = 'Fixed' # ensures global coordinates
            minLimits = [xLimits[0], yLimits[0], zLimits[0]]            
            maxLimits = [xLimits[1], yLimits[1], zLimits[1]]
            xVls = [clone.EndAX, clone.EndBX]
            yVls = [clone.EndAY, clone.EndBY]
            zVls = [clone.EndAZ, clone.EndBZ]
            values = [xVls, yVls, zVls]
            include = True
            for vEnds, minLim, maxLim in zip(values, minLimits, maxLimits):
                for v in vEnds:
                    if minLim != None: # check min
                        if v < minLim: include = False
                    if maxLim != None: # check max
                        if v > maxLim: include = False
            if include: resultList.append(line)
            # cloneModel.DestroyObject(clone) # free memory
            self.model.DestroyObject(clone) # free memory

        return resultList


