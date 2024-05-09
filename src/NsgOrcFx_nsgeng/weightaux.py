import math
# import numpy as np
from .classes import *
from .auxfuncs import *


def getSubmergedVolume(line: OrcaFlexLineObject, inner: bool = True, segIndex: int=None) -> float:
    """Returns the submerged volume of a line, assuming straight shape"""
    endA, endB = getGlobalCoordinates(line)

    if endA[2] > endB[2]: endTop, endBot = endA, endB
    else:                 endTop, endBot = endB, endA

    model = orc.Model(handle=line.modelHandle)
    seaZ = model.environment.WaterSurfaceZ

    # ltotal = getLineLength(line)
    ltotal = line.totalLength()

    volume = 0.0

    if segIndex == None:
        segList = list(range(line.NumberOfSections))
    else: 
        segList = [segIndex]

    for iSeg in segList:
        lSeg = line.Length[iSeg]
        l2 = line.CumulativeLength[iSeg]
        l1 = l2 - lSeg

        end1 = getIntermadiatePos(endA, endB, l1/ltotal)
        end2 = getIntermadiatePos(endA, endB, l2/ltotal)

        ltName = line.LineType[iSeg]
        area = getCrossArea(ltName, model, inner)

        innerLines = getInnerLines(line)
        if innerLines:
            for inLine in innerLines: # TODO: improve to consider the segment which is inside (not necessarly the 1st)
                inArea = getCrossArea(inLine.LineType[0], model, False)
                area -= inArea      

        if end1[2] < seaZ and end2[2] < seaZ:            
            volume += lSeg * area

        elif end1[2] > seaZ and end2[2] > seaZ: # totally emerged
            volume += 0.0

        else: # if is partially submerged
            if end1[2] > end1[2]: endTop, endBot = end1, end2
            else:                 endTop, endBot = end2, end1            
            
            zTop, zBot = endTop[2], endBot[2]
            fracSub = (seaZ - zBot) / (zTop - zBot)
            lSub = lSeg * fracSub
            volume += lSub * area

    return volume

def getTotalInnerVolume(line: OrcaFlexLineObject) -> float:
    """Returns the total inner volume of a line"""
    model = orc.Model(handle=line.modelHandle)
    volume = 0.0
    for iSeg in range(line.NumberOfSections):
        ltName = line.LineType[iSeg]
        area = getCrossArea(ltName, model)
        innerLines = getInnerLines(line)
        if innerLines:
            for inLine in innerLines: # TODO: improve to consider the segment which is inside (not necessarly the 1st)
                inArea = getCrossArea(inLine.LineType[0], model, False)
                area -= inArea
        lSeg = line.Length[iSeg]
        volume += lSeg * area
    
    return volume


def getTotalInnerVolume(line: OrcaFlexLineObject) -> float:
    """Returns the total inner volume of a line"""
    model = orc.Model(handle=line.modelHandle)
    volume = 0.0
    for iSeg in range(line.NumberOfSections):
        ltName = line.LineType[iSeg]
        area = getCrossArea(ltName, model)
        innerLines = getInnerLines(line)
        if innerLines:
            for inLine in innerLines: # TODO: improve to consider the segment which is inside (not necessarly the 1st)
                inArea = getCrossArea(inLine.LineType[0], model, False)
                area -= inArea
        lSeg = line.Length[iSeg]
        volume += lSeg * area
    
    return volume


def getCrossArea(lineTypeName: str, model: orc.Model, inner: bool=True) -> float:
    """
    Calculates the ross section area of the Line Type
    If inner=True, returns the inner area, otherwise returns the external
    """
    lt = model[lineTypeName]
    if inner:
        d = lt.ID
    else:
        d = lt.OD
        if lt.Category == "Homogeneous pipe":
            d += 2*lt.CoatingThickness

    if type(d) == str:
        print(f'Warning! Variable diameter (line type {lineTypeName} not supported).')
        return 0.0
    else:
        return math.pi/4 * d**2



def getInnerLines(line: Union[OrcaFlexLineObject, str]) -> Union[list[OrcaFlexObject], None]:
    """Returns the lines inside the provided line"""
    innerLines = []
    if type(line) == OrcaFlexLineObject: lineName = line.Name
    elif type(line) == 'str': lineName = line
    else: raise Exception(f'Type {type(line)} not supported for the argument "line".')

    model = orc.Model(handle=line.modelHandle)
    contactData =  model['Line contact data']
    nRels = contactData.NumberOfRelationships
    for i in range(nRels):
        splinedLine = contactData.SplinedLine[i]
        if splinedLine == lineName:
            penIs = contactData.PenetratingLineIs[i]
            if penIs == 'Inside':
                penetratingLineName = contactData.PenetratingLine[i]
                penetratingLine = model[penetratingLineName]
                innerLines.append(penetratingLine)
    
    if len(innerLines): return innerLines
    else: return None


def getTotalInnerVolume(line: OrcaFlexLineObject) -> float:
    """Returns the total inner volume of a line"""
    model = orc.Model(handle=line.modelHandle)
    volume = 0.0
    for iSeg in range(line.NumberOfSections):
        ltName = line.LineType[iSeg]
        area = getCrossArea(ltName, model)
        innerLines = getInnerLines(line)
        if innerLines:
            for inLine in innerLines: # TODO: improve to consider the segment which is inside (not necessarly the 1st)
                inArea = getCrossArea(inLine.LineType[0], model, False)
                area -= inArea
        lSeg = line.Length[iSeg]
        volume += lSeg * area
    
    return volume
