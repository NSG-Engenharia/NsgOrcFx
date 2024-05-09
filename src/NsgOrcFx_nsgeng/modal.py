import math
import numpy as np
import OrcFxAPI as orc
# from NsgOrcFx.classes import *
from . import constants as __constants
from . import classes as __classes
from . import utils as __utils

# def calculateModalAnalysis(
#         firstMode: int = -1,
#         lastMode: int = -1
#         ) -> __classes.Modes:
    
#     specs = orc.ModalAnalysisSpecification(True, firstMode, lastMode) # TODO: check other default inputs
#     return specs

# ========= CONSTANTS ========== #


# ========= METHODS ========== #
def GetModalArcLengths(
        line: orc.OrcaFlexLineObject,
        modes: orc.Modes,
        dof: str = 'Ux' # Degree of freedom: 'Ux', 'Uy', 'Uz', 'Rx', 'Ry', or 'Rz'
    ) -> list[float]:
    """
    Returns a list with the arc length of each modal result position
    Assumes that arc lengths are the same for all shapes
    """
    dofNumber = __utils.dofNumber(dof)
    
    # nodeList = [node for (dof, node) in zip(modes.dof, modes.nodeNumber) if dof == dofNumber]
    nodeList = [node for (owner, dof, node) in zip(modes.owner, modes.dof, modes.nodeNumber) if owner.name == line.name and dof == dofNumber]

    allNodesArcLengthList = line.NodeArclengths
    arcLengthList: list[float] = [l for i, l in enumerate(allNodesArcLengthList) if (i+1) in nodeList]

    return arcLengthList



def setDispsByMidLineConnections(
        line: orc.OrcaFlexLineObject,
        iniPos: list[list[float]],
        # iniAngles: list[list[float]],
        disps: list[list[float]],
        invertDisps: bool = False
        ):    
    # startNode = int(line.EndAConnection != 'Free')
    if line.LengthAndEndOrientations == 'Calculated from end positions':
        raise Exception(f"Error for line {line.name}. Cannot use mid line connections to enforce line positions for the 'Calculated from end positions'.")

    model = orc.Model(handle=line.modelHandle)
    arcLengths = line.NodeArclengths
    line.NumberOfMidLineConnections = len(arcLengths[1:-1])

    if invertDisps: sign = -1.
    else:           sign = +1.

    i = 0
    for l, [x, y, z, a, d, g], [u, v, w] in zip(arcLengths[1:-1], iniPos[1:-1], disps): #, iniAngles[1:-1], disps):
        # create new constraint to hold de line with the modal shape displacements
        newConstraint = model.CreateObject(orc.ObjectType.Constraint)
        # set the position of modal shape
        newConstraint.InitialX = x + sign*u
        newConstraint.InitialY = y + sign*v
        newConstraint.InitialZ = z + sign*w
        newConstraint.InitialAzimuth = a
        newConstraint.InitialDeclination = d
        newConstraint.InitialGamma = g            
        for j in range(3,6): newConstraint.DOFFree[j] = 'Yes' # free rotations
        # connect the line nodes to the constraints as midline connections
        line.MidLineConnectionArclength[i] = l
        line.MidLineConnection[i] = newConstraint.name
        line.MidLineConnectionX[i] = 0 
        line.MidLineConnectionY[i] = 0 
        line.MidLineConnectionZ[i] = 0 
        line.MidLineConnectionAzimuth[i] = 0
        line.MidLineConnectionDeclination[i] = 0
        line.MidLineConnectionGamma[i] = 0
        i += 1


def __getStressRange(
        line: orc.OrcaFlexLineObject, 
        modalShape: list[list[float]],
        nThetas: int=8, # number of cross section points (polar coords.) to calculate stress range
        rPos: str = 'mid' # 'inner', 'mid', 'outer'
        ) -> list[float]:
    """
    Get the stress range at the especified radius and theta (ploar coordinate in cross section)
    """    
    # static position
    staticDisps = __getStaticDisps(line)

    # new line
    model = orc.Model(handle=line.modelHandle)
    model.Reset()
    newLine = line.CreateClone()
    # modalArcLengthList = GetModalArcLengths(line, modes)

    rp = __utils.RadialPosFromStr(rPos)
    dTheta = 360./nThetas
    thetaList = [i*dTheta for i in range(nThetas)] #np.linspace(0, 360, nThetas)
    zzPlusMinusStressList = [[],[]]
    for plusMinus in zzPlusMinusStressList:
        for _ in range(nThetas): plusMinus.append([])

    # TODO: handle case with degree of freedon at end nodes (free end)
    # setDispsByMidLineConnections(newLine, staticDisps, staticAngles, modalShape)
    for invDisp, zzStressThetaList in zip([False, True], zzPlusMinusStressList):
        setDispsByMidLineConnections(newLine, staticDisps, modalShape, invDisp)
        model.CalculateStatics()
        # model.SaveData(f'test_{invDisp}.dat')

        for theta, zzStressList in zip(thetaList, zzStressThetaList):
            zzStresses = newLine.RangeGraph('ZZ stress', orc.pnStaticState, orc.oeLine(RadialPos=rp, Theta=theta))
            zzStressList.extend(zzStresses.Mean)

        # print(zzStressList)

    nNodes = len(zzStresses.Mean)
    maxStressRange = nNodes*[math.nan]

    for i in range(nNodes):
        for j in range(nThetas):
            diff = abs(zzPlusMinusStressList[0][j][i] - zzPlusMinusStressList[1][j][i])
            if math.isnan(maxStressRange[i]): maxStressRange[i] = diff
            else: maxStressRange[i] = max(maxStressRange[i], diff)


    # delete the temporary line
    model.DestroyObject(newLine)

    return zzStresses.X, np.array(maxStressRange)

def __calcNormalFactor(
        line: orc.OrcaFlexLineObject,
        ux: np.ndarray,
        uy: np.ndarray,
        uz: np.ndarray,
        extremeValue: float=1.0,
        ) -> float:
    """Returns the normalization factor"""
    u: list[float] = []
    for x, y, z in zip(ux, uy, uz):
        u.append(math.sqrt(x**2+y**2+z**2))
    maxU = max(abs(max(u)), abs(min(u)))
    f = extremeValue/maxU
    return f

def __getGlobalDispValues(
        line: orc.OrcaFlexLineObject,
        # lineName: str,
        modes: orc.Modes,
        dof: str, # Degree of freedom: 'Ux', 'Uy', 'Uz', 'Rx', 'Ry', or 'Rz'
        modeIndex: int=0
        ) -> list[float]:
    """without normalization"""
    # modes = orc.Modes(line)

    mode = modes.modeDetails(modeIndex)
    dofNumber = __utils.dofNumber(dof) 
        
    # nDofTypes = len(__constants.dofStrs)
    # dispList: list[float] = [
    #     disp for (i, disp) in enumerate(mode.shapeWrtGlobal) if i % nDofTypes == dofNumber-1 \
    #         and modes.owner[i].name == line.name
    # ]

    dispList: list[float] = [
        disp for (i, disp) in enumerate(mode.shapeWrtGlobal) if \
            modes.owner[i].name == line.name and modes.dof[i] == dofNumber
    ]


    # TODO: handle lines with intermediate node dof fixed (no result)
    # if line.EndAConnection != 'Free': dispList.insert(0, 0)
    # if line.EndBConnection != 'Free': dispList.append(0)

    return dispList



def GlobalDispShape(
        line: orc.OrcaFlexLineObject,
        modes: orc.Modes,
        modeIndex: int=0,
        normalizeMaxValue: float | None = None # apply a factor to the extreme value be the especified value
        ) -> tuple[list[float],list[float],list[float]]:
    """
    Returns the shape displacements (x, y, z) for a given mode index (0 based)
    the displacements are normalized to a maximum displaciment of 1 x outer diameter
    """
    ux = np.array(__getGlobalDispValues(line, modes, 'Ux', modeIndex))
    uy = np.array(__getGlobalDispValues(line, modes, 'Uy', modeIndex))
    uz = np.array(__getGlobalDispValues(line, modes, 'Uz', modeIndex))

    if normalizeMaxValue != None: f = __calcNormalFactor(line, ux, uy, uz, normalizeMaxValue)
    else: f = 1.0

    return f*ux, f*uy, f*uz

def __getStaticDisps(line: orc.OrcaFlexLineObject) -> list[list[float]]:
    """Returns the static displacements (translational and angular)"""
    staticDisps = []
    for var in ['X', 'Y', 'Z', 'Node azimuth', 'Node declination', 'Node gamma']: 
        staticDisps.append(line.RangeGraph(var, orc.pnStaticState).Mean.copy())

    return __utils.mergeLists(staticDisps)

def __getExternalDiameter(line: orc.OrcaFlexLineObject) -> float:
    """Returns the external diameter, including coating"""
    ltName = line.LineType[0] # assuming all sections with same line type
    model = orc.Model(handle=line.modelHandle)
    lt = model[ltName]
    OD = lt.OD
    tCoating = lt.CoatingThickness
    if tCoating: OD += 2*tCoating
    return OD

def StressShape(
        line: orc.OrcaFlexLineObject,
        modes: orc.Modes,
        modeIndex: int=0, # 0 based
        nThetas: int=8, # number of cross section points (polar coords.) to calculate stress range
        radiusPos: str='mid', # 'inner', 'mid', 'outer'
        normalizeByDiameter: bool=True, # set extreme value to + or - outer diameter
        equalySpaced: bool=False # if the result positions (arc lengths) should be interpolated into equaly sapced points
        ):
    """Returns the stress shape (stress range per diameter unit), in MPa"""

    # modal disps
    if normalizeByDiameter: extremeValue = __getExternalDiameter(line)
    extremeValue = None
    ux, uy, uz = GlobalDispShape(line, modes, modeIndex, extremeValue)
    modalDisps = __utils.mergeLists([ux, uy, uz])
    
    # calculate statics and get axial stress
    # zzStressRange = __getStressRange(line, modalDisps, nThetas, radiusPos)
    arcLengthList, maxStressRangeList = __getStressRange(line, modalDisps, nThetas, radiusPos)    

    if equalySpaced:
        xList, [yList] = __utils.creatEvenlySpacedData(arcLengthList, [maxStressRangeList])
    else:
        xList, yList = arcLengthList, maxStressRangeList
            
    # return zzStressRange.X, zzStressRange.Mean/1e3 # MPa
    # return arcLengthList, maxStressRangeList/1e3 # MPa
    return xList, yList/1e3 # MPa
