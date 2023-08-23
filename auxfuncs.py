import os
import numpy as np
import OrcFxAPI as orc

def isConnectedToObj(connection: str) -> bool:
    """Returns true if the connection refers to other object"""
    if connection == 'Free' or connection == 'Fixed' or connection == 'Anchored':
        return False
    else:
        return True

def compareStrings(
        strA: str, 
        strB: str, 
        partialMatch: bool=False
        ) -> bool:
    if partialMatch:
        n = min(len(strA), len(strB))
        strA = strA[:n]
        strB = strB[:n]    
    # print(f'strA={strA} | strB={strB}')
    return strA == strB

def strInStrList(
        str: str,
        strList: list[str],
        partialMatch: bool=False
        ) -> bool:    
    for s in strList:
        if compareStrings(s, str, partialMatch): return True
    return False

def afCheckOrCreateFolder(path: str) -> bool:
    """
    Check if the folder exists and, case not, try to create
    Returns false if don't exists and can't create
    """
    if os.path.isdir(path):
        return True
    else:
        try:
            os.mkdir(path)
        except Exception as error:
            print(f'Error! Could not create the path {path}. {error}')
            return False
        else:
            return True

def getGlobalCoordinates(
        line: orc.OrcaFlexLineObject
        ) -> tuple[list[float], list[float]]:
    """
    Returns the global coordinates of a line end
    """
    EndAConnection = line.EndAConnection
    EndBConnection = line.EndBConnection
    line.EndAConnection = 'Fixed'
    line.EndBConnection = 'Fixed'
    endA = [line.EndAX, line.EndAY, line.EndAZ]
    endB = [line.EndBX, line.EndBY, line.EndBZ]
    line.EndAConnection = EndAConnection
    line.EndBConnection = EndBConnection
    return endA, endB

def getIntermadiatePos(
        endA: list[float], 
        endB: list[float], 
        positionRatio: float
        ) -> list[float]:
    """Returns an intermediate position based on two points and a position ratio"""
    p1, p2 = np.array(endA), np.array(endB)
    pos = (p2-p1)*positionRatio + p1
    return pos.tolist().copy()