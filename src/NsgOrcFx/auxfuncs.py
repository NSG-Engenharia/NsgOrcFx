import os
import ctypes
import numpy as np
import OrcFxAPI as __ofx
from . import constants

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


# Searchs for the highest rise or fall for a given seastate (defined in the input OrcaFlex model)
# Save this file in the same folder of you code and include the following line in the library section: 
# 'from Orc_SearchWave import GetLargestRiseAndFall, SetReducedSimDuration'
def __TxtToFloat(txt: str):
    '''
    convert string to float, replacing ',' by '.', if necessary
    '''
    txt = txt.replace(',', '.')
    return float(txt)

def isRegularWave(waveType: str) -> bool:
    if waveType in constants.regularWaveTypes: return True
    elif waveType in constants.irregularWaveTypes: return False
    else:
        print(f'Warning! Wave type {waveType} not recognized. Considered as irregular.')
        return False

def SetReducedSimDuration(
        model: __ofx.Model, 
        reducedDuration: float = 200., 
        refstormduration = 10800.,
        fallOrRise: str ='rise', # 'rise' or 'fall'
        extremeWavePosition: list[float] = [0.,0.],
        iniWaveTimeOrigin: float | None = 0.0
        ) -> None:
    '''
    Reduces the simulation time for irreguar wave based on the highest fall/rise
        - model: OrcaFlex loaded model
        - reducedDuration: The simulation time after reducing. Used for the Stage 1. 
        - refstormduration: wave duration along which the highest rise/fall will be searched
        - fallOrRise: if time selection is based on the largest 'fall' or 'rise' event
        - waveTrainIndex: based on which wave train largest fall or rise must be selected
        - extremeWavePosition: position of wave origin for search
        - iniWaveTimeOrigin: initial wave time origin to search for the next extreme event. If `None`, keep the value in the model for each wave train.

        Obs.: the Tp value defined in the model will be used for the Stage 0.
    '''        
    env = model.environment
    # previousWaveTrainIndex = env.SelectedWaveTrainIndex
    # env.SelectedWaveTrainIndex = waveTrainIndex
    hasIrregularWave = False
    for i in range(env.NumberOfWaveTrains):
        env.SelectedWaveTrainIndex = i
        if iniWaveTimeOrigin != None:
            env.WaveTimeOrigin = iniWaveTimeOrigin
        if not isRegularWave(env.WaveType):
            hasIrregularWave = True

    if not hasIrregularWave:
        raise Exception(
            'Reduced simulation time approach is only '+\
            'valid when, at least, one have train has irregular waves.')
    
    # env.WaveTimeOrigin = 0 # uses the value defined by user
    # prevWavePreviewPosition = [env.WavePreviewPositionX, env.WavePreviewPositionY]
    env.WavePreviewPositionX = extremeWavePosition[0]
    env.WavePreviewPositionY = extremeWavePosition[1]
    
    tRise, tFall = GetLargestRiseAndFall(model, WaveSearchDuration=refstormduration)
    if fallOrRise == 'rise': tSel = tRise
    elif fallOrRise == 'fall': tSel = tFall
    else: raise Exception(f'Input {fallOrRise} not allowed to "fallOrRise".')

    largestTz = 0
    for i in range(env.NumberOfWaveTrains):
        env.SelectedWaveTrainIndex = i
        env.WaveTimeOrigin += -tSel + reducedDuration/2
        if not isRegularWave(env.WaveType):
            largestTz = max(largestTz, env.WaveTz)
    
    # Tz = env.WaveTz
    general = model.general
    general.StageDuration[0] = largestTz # Tz
    general.StageDuration[1] = reducedDuration

    # env.SelectedWaveTrainIndex = previousWaveTrainIndex
    # env.WavePreviewPositionX, env.WavePreviewPositionY = prevWavePreviewPosition[0], prevWavePreviewPosition[1]


def GetLargestRiseAndFall(
        model: __ofx.Model, 
        filename: str = 'SearchWave', 
        WaveSearchDuration: float = 10800
        ) -> tuple[float,float]:
    '''
    Inputs:
        - model: OrcaFlex model with the defined wave (type, Tp, Hs ...)
        - filename (optional): Temporary file that will be used in the search.
        - WaveSearchDuration (optional): Period, in seconds, to find the highest rise or fall. Default = 10080
        
    Outputs:
        - tuple (t1, t2) with two values: time of highest rise and fall
    '''        
    env = model.environment

    #assuming we want to look over the first 3hrs
    env.WaveSearchFrom = 0.0
    env.WaveSearchDuration = WaveSearchDuration
    #i'm using Largest Rise as the metric to judge which wave I want
    #so I don't actually need to report any of the individual waves 
    #so I set the search parameters to arbitrarily high values:
    env.WaveSearchMinHeight = 1e9
    if env.NumberOfWaveTrains == 1:
        env.WaveSearchMinSteepness = 1e9

    file = filename + '.txt'
    try:   
        model.SaveWaveSearchSpreadsheet(file)
    except:
        raise Exception(f'Error when saving temporary file {file}.')

    #parse the txt file to find the line with the largest rise and fall
    with open(file) as f:
        for row in f:
            if 'Largest rise' in row:
                timeOfLargestRise = __TxtToFloat(row.split()[3]) #get the global time of the largest rise
            elif 'Largest fall' in row:
                timeOfLargestFall = __TxtToFloat(row.split()[3]) #get the global time of the largest fall
    
    os.remove(file) # delete temp file

    t0 = env.WaveTimeOrigin

    return timeOfLargestRise-t0, timeOfLargestFall-t0