from __future__ import annotations
import OrcFxAPI as orc
from typing import Optional, Union

class OrcaFlexObject(orc.OrcaFlexObject):
    Name: str
    """Object name"""
    def __init__(self, object: orc.OrcaFlexObject) -> None:
        super().__init__(object.modelHandle, object.handle, object.type)

class OrcaFlexGeneralObject(OrcaFlexObject):
    StageDuration: list[float]
    """Analysis -> Stages -> Duration (s)"""


class OrcaFlexLineObject(OrcaFlexObject, orc.OrcaFlexLineObject):
    EndAConnection: str 
    """End connections -> End A -> Connect to object"""
    EndBConnection: str    
    """End connections -> End B -> Connect to object"""
    EndAX: float
    """End connections -> End A -> Position (m) -> x"""
    EndBX: float
    """End connections -> End B -> Position (m) -> x"""
    EndAY: float
    """End connections -> End A -> Position (m) -> y"""
    EndBY: float
    """End connections -> End B -> Position (m) -> y"""
    EndAZ: float
    """End connections -> End A -> Position (m) -> z"""
    EndBZ: float
    """End connections -> End B -> Position (m) -> z"""
    EndAConnectionzRelativeTo: str
    """End connections -> End A -> z relative to: 'End A' or 'End B'"""
    EndBConnectionzRelativeTo: str
    """End connections -> End B -> z relative to: 'End A' or 'End B'"""
    EndAHeightAboveSeabed: float
    """End connections -> End A -> Height above seabed"""
    EndBHeightAboveSeabed: float
    """End connections -> End B -> Height above seabed"""
    EndAAzimuth: float
    """End connections -> End A -> Orientation (deg) -> Azimuth"""
    EndBAzimuth: float
    """End connections -> End B -> Orientation (deg) -> Azimuth"""
    EndADeclination: float
    """End connections -> End A -> Orientation (deg) -> Declination"""
    EndBDeclination: float
    """End connections -> End B -> Orientation (deg) -> Declination"""
    EndAGamma: float
    """End connections -> End A -> Orientation (deg) -> Gamma"""
    EndBGamma: float
    """End connections -> End B -> Orientation (deg) -> Gamma"""
    EndAReleaseStage: int
    """End connections -> End A -> Release at start of stage"""
    EndBReleaseStage: int
    """End connections -> End B -> Release at start of stage"""
    
    CumulativeLength: list[float]
    """Structure -> Cumulative values -> Length (m)"""

    def totalLength(self) -> float:
        """Total length of the line"""
        return self.CumulativeLength[-1]

    def CreateClone(
            self, 
            name: Optional[str] = None, 
            model: Optional[orc.Model] = None
            ) -> OrcaFlexLineObject:
        newObj = super().CreateClone(name, model)
        newLineObj = OrcaFlexLineObject(newObj)
        return newLineObj

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

    FromArclength: list[float]
    """Analysis data -> Arc length intervals (m) -> From"""
    ToArclength: list[float]
    """Analysis data -> Arc length intervals (m) -> To"""
    RadialPosition: list[str]
    """Analysis data -> Radial position: 'Inner', 'Outer', or 'Mid'"""
    SCF: list[float]
    """Analysis data -> Stress correction factors -> Stress concentration factor (SCF)"""
    ThicknessCorrectionFactor: list[float]
    """Analysis data -> Stress correction factors -> Thickness factor"""
    AnalysisDataSNcurve: list[str]
    """Analysis data -> Stress correction factors -> S-N curve"""


