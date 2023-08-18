"""
# Library of complementary tools for the OrcaFlex API (OrcFxAPI)
#
#
#
"""

__author__ = "NSG Engenharia"
__copyright__ = "Copyright 2023"
__credits__ = ["Gabriel Nascimento"]
__license__ = "GPL"
__version__ = "1.0.0"
__maintainer__ = "Gabriel Nascimento"
__email__ = "gabriel.nascimento@nsgeng.com"
__status__ = "Development"


import OrcFxAPI as orc
from typing import Union

from OrcFxAPI import Handle, ObjectType, OrcaFlexObject

from NsgOrcFx.classes import *
from NsgOrcFx.sortlines import *



class Model(orc.Model):
    general: OrcaFlexGeneralObject
   
    def __getitem__(self, name: str) -> OrcaFlexObject:
        return OrcaFlexObject(super().__getitem__(name)) 
    
    def findLineByName(self, name: str) -> OrcaFlexLineObject:
        """Find a line object by its name"""
        obj = self[name]
        return OrcaFlexLineObject(obj)
    
    def getAllLines(self) -> list[OrcaFlexLineObject]:
        """Returns a list of all line objects"""
        lineList = []
        for obj in self.objects:
            if obj.type == orc.ObjectType.Line:
                lineList.append(obj)
        return lineList

    def getLineList(
            self, 
            groupName: Union[str, None] = None, 
            includeSubgroups: bool = False
            ) -> list[OrcaFlexLineObject]:
        """
        Returns all lines in the model which belongs to the defined group with or not its subgroups
        """            
        result: list[OrcaFlexObject] = []
        if groupName:
            selectedList = list(self[groupName].GroupChildren(recurse=includeSubgroups))
        else:
            selectedList = list(self.objects)

        for obj in selectedList:
            if obj.type == orc.ObjectType.Line:
                result.append(OrcaFlexLineObject(obj))
            elif groupName and includeSubgroups and obj.type == orc.ObjectType.BrowserGroup:
                result.extend(self.getLineList(obj.Name))
            
        return result
    
    def sortPathInterconnectedLines(
            self,
            lineList: list[OrcaFlexLineObject]
            ) -> list[OrcaFlexLineObject]:
        """
        Returns a sorted list of interconnected lines, based on its connections (e.g., path from first to last)
        The result is unpredictable if not all lines are connected or if there are connection between more than two lines
        """        
        return sortPathInterconnectedLines(lineList)