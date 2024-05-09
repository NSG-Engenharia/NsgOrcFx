import os
import ctypes
import numpy as np
import OrcFxAPI as __ofx

__char = ctypes.c_wchar
__letters = 'abcdefghijklimnoprstuvwxyz'

def getOrcaVersion() -> str:
    """Return the installed OrcaFlex version as string"""
    global __char, DLLVersion
    _charArray16 = (__char * 16)()
    OK = ctypes.c_long()
    Status = ctypes.c_long()
    __ofx._GetDLLVersion(None, 
                        _charArray16,
                        ctypes.byref(OK), 
                        ctypes.byref(Status))
    DLLVersion = str()
    for i in range(16): 
        c = _charArray16[i]
        if c != '\x00': DLLVersion += c
    return DLLVersion

def __versionStrToNum(version: str):
    vernum = str()
    verletter = str()        
    for c in version:
        if __letters.find(c) < 0:
            vernum += c
    else:
        verletter += c
        letterpos = __letters.find(c)

    return float(vernum + str(letterpos))

def getOrcaVersionAsFloat() -> float:
    """Return the installed OrcaFlex version as float"""
    versionTxt = getOrcaVersion()
    __versionStrToNum(versionTxt)

def checkOrcaFlexVersion(requiredVersion: str) -> bool:
    """Return True if the installed version of OrcaFlex is equal or newer than the required"""
    return __isNewerOrEqualTo(requiredVersion)

def __isNewerOrEqualTo(version: str) -> bool:
    """
    Verifies if the current version of OrcFxAPI.dll is equal or newer then the required version
    * version: minimum required version of OrcFxAPI.dll
    """
    actualver = getOrcaVersion()
    if __versionStrToNum(actualver) >= __versionStrToNum(version):
        return True
    else:
        return False    


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
        line: __ofx.OrcaFlexLineObject
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