from __future__ import annotations
from typing import Optional, Union
import pandas as pd
import numpy as np
# import math
import OrcFxAPI as _ofx
from . import utils as _utils
from . import modal as _modal
from . import params

class OrcaFlexObject(_ofx.OrcaFlexObject):
    def __init__(self, obj: _ofx.OrcaFlexObject) -> None:
        super().__init__(obj.modelHandle, obj.handle, obj.type)
        object.__setattr__(self, 'data', params._DataLineObject(self))


class OrcaFlexGeneralObject(OrcaFlexObject):
    data: params._DataGeneralObject

class OrcaFlexEnvironmentObject(OrcaFlexObject):
    data: params._DataEnvinronmentObject


class OrcaFlexConstraint(OrcaFlexObject):
    pass

class OrcaFlexLineObject(OrcaFlexObject, _ofx.OrcaFlexLineObject):
    data: params._DataLineObject

    def totalLength(self) -> float:
        self.__init__()
        """Total length of the line"""
        return self.CumulativeLength[-1]

    def CreateClone(
            self, 
            name: Optional[str] = None, 
            model: Optional[_ofx.Model] = None
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
                self.TargetSegmentLength[i] = _ofx.OrcinaDefaultReal()
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
        model = _ofx.Model(handle=self.modelHandle)        
        model.DestroyObject(clone) # free memory (delete the 'dummy' object)
        return EndA, EndB



# Modal analysis
class Modes(_ofx.Modes):
    model: _ofx.Model

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
    def model(self) -> _ofx.Model:
        """Returns the OrcaFlex Model"""
        # return _ofx.Model(handle=self.line.modelHandle)
        return _ofx.Model(handle=self.owner[0].modelHandle)

    def getLineByName(self, lineName: str) -> OrcaFlexLineObject:
        for obj in self.owner:
            if obj.name == lineName and obj.type == _ofx.ObjectType.Line:
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
        the displacements may be normalized to a maximum displacement of 1x outer diameter
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



            