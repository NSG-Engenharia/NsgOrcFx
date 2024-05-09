from __future__ import annotations
from typing import Optional, Union
import pandas as pd
import numpy as np
# import math
import OrcFxAPI as __ofx
from . import utils as _utils
from . import modal as _modal
from . import sncurves as SNCurves
from . import params

class OrcaFlexObject(__ofx.OrcaFlexObject):
    def __init__(self, obj: __ofx.OrcaFlexObject) -> None:
        super().__init__(obj.modelHandle, obj.handle, obj.type)
        object.__setattr__(self, 'params', params._DataLineObject(self))


class OrcaFlexGeneralObject(OrcaFlexObject):
    params: params._GeneralObject

class OrcaFlexConstraint(OrcaFlexObject):
    pass

class OrcaFlexLineObject(OrcaFlexObject, __ofx.OrcaFlexLineObject):
    params: params._DataLineObject

    def totalLength(self) -> float:
        self.__init__()
        """Total length of the line"""
        return self.CumulativeLength[-1]

    def CreateClone(
            self, 
            name: Optional[str] = None, 
            model: Optional[__ofx.Model] = None
            ) -> OrcaFlexLineObject:
        """Create an identical line, except for the name"""
        newObj = super().CreateClone(name, model)
        newLineObj = OrcaFlexLineObject(newObj)
        return newLineObj

    def setLog(self, logResults: bool) -> None:
        """Defines if the results of the line should be stored (logged) or not"""
        if logResults: self.LogResults = 'Yes'
        else: self.LogResults = 'No'

    def setMeshSize(
            self,
            nSegs: int = None,
            targetLength: float = None
            ):
        """Set the length/number of segments for all sections"""
        for i in range(self.NumberOfSections):
            if nSegs != None:
                self.TargetSegmentLength[i] = __ofx.OrcinaDefaultReal()
                self.NumberOfSegments[i] = nSegs
            elif targetLength != None:
                self.TargetSegmentLength[i] = targetLength
            else:
                raise Exception('Error! nSegs or targetLengh must be provided.')



    def getEndPositions(self) -> tuple[list[float], list[float]]:
        """
        Returns a tuple with the position [x, y, z] of the EndA and EndB
        * returns: [xA, yA, zA], [xB, yB, zB] 
        """
        clone = self.CreateClone() # copy object to 'dummy' object
        clone.EndAConnection = 'Fixed' # ensures global coordinates
        clone.EndBConnection = 'Fixed' # ensures global coordinates
        EndA = [clone.EndAX, clone.EndAY, clone.EndAZ]
        EndB = [clone.EndBX, clone.EndBY, clone.EndBZ]
        model = __ofx.Model(handle=self.modelHandle)        
        model.DestroyObject(clone) # free memory (delete the 'dummy' object)
        return EndA, EndB


class FatigueAnalysis(__ofx.FatigueAnalysis):
    params: params._DataFatigueAnalysisObject

    def __selectSNCurveByName(self, name: str, environment: str) -> SNCurves.SNCurve:
        """Name (e.g, 'F1') and environment ('air' or 'seawater')"""
        return SNCurves.selectSNCurveByName(name, environment)


    def setSNCurve(self, SNCurve: SNCurves.SNCurve) -> None:
        """
        Set the parameters of the selected S-N curve to the analysis
        """
        SNCurve.setToAnalysis(self)

    def setSNCurveByNameAndEnv(self, name: str, environment: str) -> None:
        """
        Set the parameters the S-N curve selected based on its name (e.g., 'F3')
        and environment ('air' or 'seawater')
        """
        SNCurve = self.__selectSNCurveByName(name, environment)
        self.setSNCurve(SNCurve)


    def totalExposureTime(self) -> float:
        """Sum of exposure time of each load case"""
        s = 0
        for e in self.LoadCaseExposureTime: s += e
        return s

    def nodeArcLengthList(self) -> list[float]:
        """
        Returns a list with the arc length of each node
        """
        arcLList: list[float] = []
        for pointDetails in self.outputPointDetails:
            arcLList.append(pointDetails[0])
        return arcLList

    def getArcLengthDamageLifeList(self) -> list[list[float]]:
        """
        Returns a list of three parameters (table columns): 
        * arc length: position (meters) of each node
        * damage: maximum damage arround the section circunference of each node
        * life: minimum life (years) arround the section cicrunference of each node 
        """
        arcLengthList = self.nodeArcLengthList()
        zdlList: list[list[float]] = []
        secsPerYear = 365.25*24*3600 # used to the conversion from seconds to years

        for nodeDamageRst, z in zip(self.overallDamage, arcLengthList):
            d_max = 0.0
            l_min = nodeDamageRst[0][1]
            for d, l in nodeDamageRst: # max around the circunference
                d_max = max(d_max, d) 
                l_min = min(l_min, l)
            zdlList.append([z, d_max, l_min/secsPerYear])

        return zdlList
    
    def getDamageList(self) -> list[float]:
        """
        Returns a list with the calculated damage in each node
        """
        zdlList =  self.getArcLengthDamageLifeList()
        damageList: list[float] = []
        for _, d, _ in zdlList: damageList.append(d)
        return damageList
    
    def totalExposureTime(self) -> float:
        """Return the sum of exposure time defined for each load case"""
        return sum(self.LoadCaseExposureTime)

    def getLifeList(self) -> list[float]:
        """
        Returns a list with the calculated life (years) in each node
        """
        zdlList =  self.getArcLengthDamageLifeList()
        lifeList: list[float] = []
        for _, _, l in zdlList: lifeList.append(l)
        return lifeList

    def getArcLengthDamageLifeListAsDF(self) -> pd.DataFrame:
        """
        Returns a DataFrame of three parameters (table columns): 
        * arc length: position (meters) of each node
        * damage: maximum damage arround the section circunference of each node
        * life: minimum life (years) arround the section cicrunference of each node 
        """        
        zdlList = self.getArcLengthDamageLifeList()
        cols = ['Arc length (m)', 'Damage', 'Life (years)']
        return pd.DataFrame(zdlList, columns=cols)



# Modal analysis
class Modes(__ofx.Modes):
    model: __ofx.Model

    # def __checkSingleLine(self):
    #     if self.isWholeSystem:
    #         raise Exception(f'NSG library  curently only supports single line modal analysis.')        
    

    def __checkModeIndex(self, modeIndex: int):
        if modeIndex >= self.modeCount:
            raise Exception(f'Requested mode index ({modeIndex}) greater than the maximum ({self.modeCount-1})')


    @property 
    def line(self) -> OrcaFlexLineObject:
        """Returns the line object, assuming single line modal analysis."""
        self.__checkSingleLine()
        return self.owner[0]
        
    @property
    def model(self) -> __ofx.Model:
        """Returns the OrcaFlex Model"""
        # return __ofx.Model(handle=self.line.modelHandle)
        return __ofx.Model(handle=self.owner[0].modelHandle)

    def getLineByName(self, lineName: str) -> OrcaFlexLineObject:
        for obj in self.owner:
            if obj.name == lineName and obj.type == __ofx.ObjectType.Line:
                return obj
        raise Exception(f'Line {lineName} not found in modal analysis.')

    def GetArcLengths(
            self,
            lineName: str | None,
            dof: str = 'Ux' # Degree of freedom: 'Ux', 'Uy', 'Uz', 'Rx', 'Ry', or 'Rz'
        ) -> list[float]:
        """
        Returns a list with the arc length of each modal result position
        Currently supports only modal analysis of single line
        """
        # self.__checkSingleLine()
        line = self.getLineByName(lineName)
        # return _modal.GetModalArcLengths(self.line, self, dof)    
        return _modal.GetModalArcLengths(line, self, dof)    


    def GlobalDispShape(
            self,
            lineName: str,
            modeIndex: int=0,
            normalize: bool=True, # apply a factor to the extreme value be +-1
            evenlySpaced: bool=False # interpolates the displacement values into equally spaced arclength positions
            ) -> tuple[list[float],list[float],list[float],list[float]]:
        """
        Returns the arclengths and shape displacements (x, y, z) for a given mode index (0 based)
        the displacements may be normalized to a maximum displaciment of 1 x outer diameter
        """
        self.__checkModeIndex(modeIndex)
        # line = self.getLineByName(lineName)
        # return _modal.GlobalDispShape(self.line, self, modeIndex)
        line = self.getLineByName(lineName)

        if normalize: extremeValue = 1.0
        else: extremeValue = None

        arcLengths = self.GetArcLengths(lineName)
        UX, UY, UZ = _modal.GlobalDispShape(line, self, modeIndex, extremeValue)

        if evenlySpaced:
            aList, [uxList, uyList, yzList] = _utils.creatEvenlySpacedData(arcLengths, [UX, UY, UZ])
        else:
            aList, uxList, uyList, yzList = arcLengths, UX, UY, UZ

        # return arcLengths, UX, UY, UZ
        return aList, uxList, uyList, yzList
    
    def getModeFrequency(self, modeIndex: int=0) -> float:
        """Returns the mode frequency"""
        mode = self.modeDetails(modeIndex)
        T = mode.period
        return 1./T


    def StressShape(
            self,
            lineName: str,
            modeIndex: int=0, # 0 based
            nThetas: int=8, # number of cross section points (polar coords.) to calculate stress range
            radiusPos: str='mid', # 'inner', 'mid', 'outer'
            normalizeByDiameter: bool=True, # set extreme value to + or - outer diameter (required by DNV FatFree)
            equalySpaced: bool=False # not implemented yet - if the result positions (arc lengths) should be interpolated into equaly sapced points
            ) -> tuple[list[float], list[float]]:
        """Returns the stress shape (stress range per diameter unit), in MPa"""
        line = self.getLineByName(lineName)
        return _modal.StressShape(line, self, modeIndex, nThetas, radiusPos, normalizeByDiameter, equalySpaced)



            