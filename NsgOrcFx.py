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

class OrcaFlexObject(orc.OrcaFlexObject):
    Name: str
    """Object name"""

class OrcaFlexGeneralObject(OrcaFlexObject):
    StageDuration: list[float]
    """Analysis -> Stages -> Duration (s)"""


class OrcaFlexLineObject(OrcaFlexObject, orc.OrcaFlexLineObject):
    pass

class FatigueAnalysis(orc.FatigueAnalysis):
    CriticalDamageFactor: float
    """Analysis Data -> Critical damage"""
    ThetaCount: int
    """Analysis Data -> Number of thetas"""
    ArclengthIntervalsCount: int
    """Analysis Data -> No. of arc length intervals"""
    AnalysisType: str
    """Analysis Type = 'Regular', 'Rainflow', 'Spectral (frequency domain)', or 'Spectral (response RAOs)'"""
    LoadCaseCount: int 
    """Load cases -> Number of load cases"""
    LoadCaseFileName: list[str]
    """Load cases -> Load case file name"""
    LoadCaseLineName: list[str]
    """Load cases -> Line name"""
    PeriodFrom: list[float]
    """Load cases -> Simulation periods (s) -> From"""
    PeriodTo: list[float]
    """Load cases -> Simulation periods (s) -> To"""
    LoadCaseExposureTime: list[float]
    """Load cases -> Exposure time (hours)"""

class Model(orc.Model):
    general: OrcaFlexGeneralObject
    
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
        Returns all lines in the model
        """            
        result: list[OrcaFlexObject] = []
        if groupName:
            selectedList = list(self[groupName].GroupChildren())
        else:
            selectedList = list(self.objects)

        for obj in selectedList:
            if obj.type == orc.ObjectType.Line:
                result.append(obj)
            elif groupName and includeSubgroups and obj.type == orc.ObjectType.BrowserGroup:
                result.extend(self.getLineList(obj.Name))
            
        return result