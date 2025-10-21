import os
import OrcFxAPI as __ofx
from . import constants as __constants
import numpy as np
from scipy import interpolate

def dofNumber(dofString: str) -> int:
    """get the dof number. Start with 'Ux' = 1"""
    try:
        dofInt = __constants.dofStrs.index(dofString) + 1
        return dofInt
    except Exception as error:
        print(f'Invalid dof ({dofString}). {error}')


# def threeListsToOne(lists: list[list[float]]) -> list[list[float]]:
#     """ [[a1,b1,c1,...], [a2,b2,c2,...], [a3,b3,c3,...]] -> [[a1,a2,a3,...],[b1,b2,b3,...],[c1,c2,c3,...]]"""
#     newList = []
#     for x, y, z in zip(lists[0], lists[1], lists[2]):
#         newList.append([x, y, z])
#     return newList

def mergeLists(lists: list[list[float]]) -> list[list[float]]:
    """ [[a1,b1,c1,...], [a2,b2,c2,...], [a3,b3,c3,...], ...] -> [[a1,a2,a3,...],[b1,b2,b3,...],[c1,c2,c3,...], ...]"""
    n = len(lists[0])
    for list in lists:
        if len(list) != n:
            raise Exception(f'Error! The number of items in all lists must be the same {n} <> {len(list)}.')
    
    newList = []
    for i in range(n):
        newRow = []
        for list in lists:
            newRow.append(list[i])
        newList.append(newRow)

    return newList
    
    

def RadialPosFromStr(rPos: str) -> __ofx.RadialPos:
    """
    Return the RadialPos class correspondent to the string identifier
    * rPos: 'inner', 'mid', 'outer'
    """
    if rPos == 'inner': rp = __ofx.RadialPos.Inner
    elif rPos == 'mid': rp = __ofx.RadialPos.Mid
    elif rPos == 'outer': rp = __ofx.RadialPos.Outer
    else:
        raise Exception(f'Radial position {rPos} not allowed.')
    
    return rp


def creatEvenlySpacedData(
        xValues: list[float], 
        yValueLists: list[list[float]],
        kind: str='cubic'
        ) -> tuple[list[float], list[list[float]]]:
    """
    Interpolates the y values into a equally spaced x values
    * xValues: list of x values
    * yValueLists: lists of y values
    * kind: 'nearest', 'linear', 'quadratic' or 'cubic'
    * return: a tuple with a list of the new positions (x values) and a list of the interpolated y values for each y list provided in `yValueLists`
    """
    nPoints = len(xValues)
    if nPoints < 3: # this method (create evenly spaced data) is pointless if the lists have less than 3 values
        return xValues, yValueLists
    
    kind_nMin = ['nearest', 'linear', 'quadratic', 'cubic']
    try:
        nPointsMin = kind_nMin.index(kind) + 1
    except:
        raise Exception(f"Error! Interpolation kind '{kind}' not recognized. The supported options are 'nearest', 'linear', 'quadratic' or 'cubic'.")
    
    if nPoints < nPointsMin:
        kind = kind_nMin[nPoints-1]

    minDelta = xValues[1] - xValues[0]
    for i in range(2, len(xValues)):
        delta = xValues[i]-xValues[i-1]
        minDelta = min(minDelta, delta)
    
    xRange = xValues[-1] - xValues[0]
    n = int(xRange/minDelta) + 1    
    xNew = np.linspace(min(xValues), max(xValues), n)
    
    yNewLists = []
    for yValues in yValueLists:
        f = interpolate.interp1d(xValues, yValues, kind)
        yNew = f(xNew)
        yNewLists.append(yNew)

    return xNew, yNewLists

def getFileExtension(file: str) -> str:
    _, extension = os.path.splitext(file)
    return extension


def getAvailableFileName(
        baseName: str, 
        extension: str, 
        folder: str|None = None,
        randomNumberDigits: int = 10,
        forceRandom: bool = False
        ) -> str:
    """
    Returns an available file name adding a random number at the end if needed
    * baseName: file name without extension
    * extension: file extension with or without the dot ('.')
    * folder: if provided, the folder where to check if the file exists. If not provided, the current folder is used.
    * randomNumberDigits: number of digits of the random number to be added at the end of the file name if needed
    * forceRandom: if True, a random number is always added at the end of the file name
    * return: the available file name with extension (but without the folder path)
    """
    if not extension.startswith('.'):
        extension = '.' + extension

    if folder is None:
        folder = os.getcwd()
    
    fullPath = os.path.join(folder, baseName + extension)
    if not os.path.isfile(fullPath) and not forceRandom:
        return baseName + extension
    
    def getRandomNumber(nDigits: int) -> str:
        from random import randint
        rangeStart = 10**(nDigits-1)
        rangeEnd = (10**nDigits)-1
        return str(randint(rangeStart, rangeEnd))

    cont = getRandomNumber(randomNumberDigits)
    while True:
        newFileName = f'{baseName}_{cont}{extension}'
        fullPath = os.path.join(folder, newFileName)
        if not os.path.isfile(fullPath):
            return newFileName
        cont = getRandomNumber(randomNumberDigits)


def angleFromDirName(dirName: str) -> float:
    """
    Returns the angle in degrees from a direction name
    * dirName: direction name, e.g., 'N', 'NE', 'E', 'SE', 'S', 'SW', 'W', 'NW'
    * return: angle in degrees (0 = North, clockwise)
    """
    dirName = dirName.upper()
    dirAngles = {
        'N': 0.0,
        'NNE': 22.5,
        'NE': 45.0,
        'ENE': 67.5,
        'E': 90.0,
        'ESE': 112.5,
        'SE': 135.0,
        'SSE': 157.5,
        'S': 180.0,
        'SSW': 202.5,
        'SW': 225.0,
        'WSW': 247.5,
        'W': 270.0,
        'WNW': 292.5,
        'NW': 315.0,
        'NNW': 337.5
    }
    if dirName not in dirAngles:
        raise Exception(f'Error! Direction name {dirName} not recognized. Valid names are: {list(dirAngles.keys())}.')
    
    return dirAngles[dirName]