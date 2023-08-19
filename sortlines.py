from NsgOrcFx.classes import *
from NsgOrcFx.auxfuncs import *


# def __haveAcommonConnection(
#         lineA: OrcaFlexLineObject, 
#         lineB: OrcaFlexLineObject
#         ) -> bool:
#     """If the lines have a common connection (end A or B)"""
#     if lineA.EndAConnection in [lineB.EndAConnection, lineB.EndBConnection] or \
#        lineA.EndBConnection in [lineB.EndAConnection, lineB.EndBConnection]: 
#         return True
#     else: 
#         return False

def __isInterConnected(
        line1: OrcaFlexLineObject,
        line2: OrcaFlexLineObject,
        searchL1EndA: bool = True,
        searchL1EndB: bool = True        
        ) -> tuple[bool, str, str]:
    """If the lines are interconnected, directly or indirectly"""

    def whatEndOfLine(
            line: OrcaFlexLineObject, 
            end: str, z: float
            ) -> str:
        L = line.totalLength()
        if end == 'End A' and z < L/2. or \
           end == 'End B' and z > L/2.:
            return 'End A'
        else:
            return 'End B'

    def isL1ConnectedToL2(
            l1: OrcaFlexLineObject, 
            l2: OrcaFlexLineObject,
            ) -> tuple[bool, str, str]:
        if l1.EndAConnection == l2.Name:
            return True, 'End A', whatEndOfLine(l2, l1.EndAConnectionzRelativeTo, l1.EndAZ)
        elif l1.EndBConnection == l2.Name:
            return True, 'End B', whatEndOfLine(l2, l1.EndBConnectionzRelativeTo, l1.EndBZ)
        else:
            return False, '', ''
        
         
    def hasSameConnection(
            l1: OrcaFlexLineObject, 
            l2: OrcaFlexLineObject,
            searchL1EndA: bool = True,
            searchL1EndB: bool = True            
            ) -> tuple[bool, str, str]:
        if searchL1EndA:
            if isConnectedToObj(l1.EndAConnection):
                if l1.EndAConnection == l2.EndAConnection:
                    return True, 'End A', 'End A'
                elif l1.EndAConnection == l2.EndBConnection:
                    return True, 'End A', 'End B'
        if searchL1EndB:
            if isConnectedToObj(l1.EndBConnection):
                if l1.EndBConnection == l2.EndAConnection:
                    return True, 'End B', 'End A'
                elif l1.EndBConnection == l2.EndBConnection:
                    return True, 'End B', 'End B'            
        return False, '', ''
    
    # line1 directly conneted to line2
    connected, end1, end2 = isL1ConnectedToL2(line1, line2)
    if connected:
        if searchL1EndA and end1 == 'End A' or searchL1EndB and end1 == 'End B':
            return True, end1, end2

    # line2 directly conneted to line1
    connected, end2, end1 = isL1ConnectedToL2(line2, line1)
    if connected: 
        if searchL1EndA and end1 == 'End A' or searchL1EndB and end1 == 'End B':
            return True, end1, end2

    # indirectly
    return hasSameConnection(line1, line2, searchL1EndA, searchL1EndB)
   

def sortPathInterconnectedLines(
        lineList: list[OrcaFlexLineObject]
        ) -> list[OrcaFlexLineObject]:
    """
    Returns a sorted list of interconnected lines, based on its connections (e.g., path from first to last)
    The result is unpredictable if not all lines are connected or if there are connection between more than two lines
    """
    n = len(lineList)
    _lineList = lineList.copy()

    # find the end lines (connected to only one)
    _endLines: list[list[OrcaFlexLineObject, str]] = []
    for i, lineI in enumerate(_lineList):
        nConnections = 0
        for j in range(n):
            if i != j:
                lineJ = _lineList[j]
                isConnected, end1, end2 = __isInterConnected(lineI, lineJ)
                if isConnected:
                    # print(f'Line {lineI.Name} connected with {lineJ.Name}')
                    nConnections += 1
                    end = end1
        
        if nConnections == 1:
            _endLines.append([lineI, end])

        elif nConnections > 2:
            raise Exception(f'The line {lineI.Name} has {nConnections} connections. Cannot define a path.')

    if len(_endLines) > 2:
        txt = ''
        for line, _ in _endLines:
            txt += f'Line {line.Name}. '
        raise Exception(f'There are more than two lines with only one connection. Cannot define a path.\n {txt}')
  

    # TODO: choose the top line
    line1, end = _endLines[0][0], _endLines[0][1]
    # botEndLine = _endLines[1]

    def getOtherEnd(end: str) -> str:
        if end == 'End A': return 'End B'
        else: return 'End A'

    path: list[OrcaFlexLineObject] = []
    path.append(line1)
    isConnected = True
    while isConnected:
        isConnected = False
        for line2 in _lineList:
            if line1.Name != line2.Name:
                isConnected, end1, end2 = __isInterConnected(line1, line2, end=='End A', end=='End B')
                if isConnected:
                    path.append(line2)
                    line1, end = line2, getOtherEnd(end2)
                    break
    
    return path
