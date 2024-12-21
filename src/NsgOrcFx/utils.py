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
        ) -> tuple[list[float], list[float]]:
    """
    Interpolates the y values into a equally spaced x values
    * xValues: list of x values
    * yValueLists: lists of y values
    * kind: 'nearest', 'linear', 'quadratic' or 'cubic'
    * return: a list of the interpolated y value for each y list provided in `yValueLists`
    """
    kind_nMin = ['nearest', 'linear', 'quadratic', 'cubic']
    try:
        nPointsMin = kind_nMin.index(kind) + 1
    except:
        raise Exception(f"Error! Interpolation kind '{kind}' not recognized. The supported options are 'nearest', 'linear', 'quadratic' or 'cubic'.")
    
    nPoints = len(xValues)
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