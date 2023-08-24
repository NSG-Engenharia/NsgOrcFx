from typing import Union
import OrcFxAPI as orc
from NsgOrcFx.classes import *


def getLinesToList(
        model: orc.Model, 
        groupName: Union[str, None] = None, 
        includeSubgroups: bool = False,
        lineList: list[OrcaFlexLineObject] = None
        ) -> list[OrcaFlexLineObject]:
    """
    Returns all lines in the model which belongs to the defined group with or not its subgroups
    """            
    # result = LineSelection(self)
    if lineList == None: 
        lineList: list[OrcaFlexLineObject] = []

    if groupName:
        grouObj = model[groupName]
        selectedList = list(grouObj.GroupChildren(recurse=includeSubgroups))
    else:
        selectedList = list(model.objects)

    for obj in selectedList:
        if obj.type == orc.ObjectType.Line:
            lineList.append(OrcaFlexLineObject(obj))
    
    return lineList
