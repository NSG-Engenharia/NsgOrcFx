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
        line2: OrcaFlexLineObject
        ) -> tuple[bool, str, str]:
    """If the lines are interconnected, directly or indirectly"""

    def whatEndOfLine(
            line: OrcaFlexLineObject, 
            end: str, z: float
            ) -> str:
        if end == 'EndA' and z < line.totalLength()/2. or \
           end == 'EndB' and z > line.totalLength()/2.:
            return 'EndA'
        else:
            return 'EndB'

    def isL1ConnectedToL2(
            l1: OrcaFlexLineObject, 
            l2: OrcaFlexLineObject
            ) -> tuple[bool, str, str]:
        if l1.EndAConnection == l2.Name:
            return True, 'EndA', whatEndOfLine(l2, l1.EndAConnectionzRelativeTo, l1.EndAZ)
        elif l1.EndBConnection == l2.Name:
            return True, 'EndB', whatEndOfLine(l2, l1.EndBConnectionzRelativeTo, l1.EndBZ)
        else:
            return False, '', ''
        
         
    def hasSameConnection(
            l1: OrcaFlexLineObject, 
            l2: OrcaFlexLineObject
            ) -> tuple[bool, str, str]:
        if isConnectedToObj(l1.EndAConnection):
            if l1.EndAConnection == l2.EndAConnection:
                return True, 'EndA', 'EndA'
            elif l1.EndAConnection == l2.EndBConnection:
                return True, 'EndA', 'EndB'
        if isConnectedToObj(l1.EndBConnection):
            if l1.EndBConnection == l2.EndAConnection:
                return True, 'EndB', 'EndA'
            elif l1.EndBConnection == l2.EndBConnection:
                return True, 'EndB', 'EndB'            
        return False, '', ''
    
    # line1 directly conneted to line2
    connected, end1, end2 = isL1ConnectedToL2(line1, line2)
    if connected: return True, end1, end2

    # line2 directly conneted to line1
    connected, end1, end2 = isL1ConnectedToL2(line2, line1)
    if connected: return True, end1, end2

    # indirectly
    return hasSameConnection(line1, line2)
   

def sortPathInterconnectedLines(
        lineList: list[OrcaFlexLineObject]
        ) -> list[OrcaFlexLineObject]:
    """
    Returns a sorted list of interconnected lines, based on its connections (e.g., path from first to last)
    The result is unpredictable if not all lines are connected or if there are connection between more than two lines
    """
    n = len(lineList)
    _lineList = lineList.copy()
    # _endAconnectedToList = [n*None]
    # _endBconnectedToList = [n*None]

    # find the end lines (connected to only one)
    _endLines: list[OrcaFlexLineObject] = []
    for i, lineI in enumerate(_lineList):
        nConnections = 0
        for j in range(n):
            if i != j:
                lineJ = _lineList[j]
                isConnected, end1, end2 = __isInterConnected(lineI, lineJ)
                if isConnected:
                    # print(f'Line {lineI.Name} connected with {lineJ.Name}')
                    nConnections += 1
        
        if nConnections == 1:
            _endLines.append([lineI, end1])

        elif nConnections > 2:
            raise Exception(f'The line {lineI.Name} has {nConnections} connections. Cannot define a path.')

    if len(_endLines) > 2:
        raise Exception(f'There are more than two lines with only one connection. Cannot define a path.')
   
    print(_endLines)

    # TODO: choose the top line
    topEndLine = _endLines[0]
    botEndLine = _endLines[1]


