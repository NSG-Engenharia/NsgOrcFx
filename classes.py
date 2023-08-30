from __future__ import annotations
import pandas as pd
from typing import Optional, Union
import OrcFxAPI as orc
import NsgOrcFx.sncurves as SNCurves


class OrcaFlexObject(orc.OrcaFlexObject):
    Name: str
    """Object name"""
    def __init__(self, object: orc.OrcaFlexObject) -> None:
        super().__init__(object.modelHandle, object.handle, object.type)

class OrcaFlexGeneralObject(OrcaFlexObject):
    StageCount: int
    """Analysis -> Stages -> Number of stages"""
    StageDuration: list[float]
    """Analysis -> Stages -> Duration (s)"""
    ImplicitConstantTimeStep: float
    """Dynamics -> Parameters -> Time step (s)"""
    ImplicitConstantMaxNumOfIterations: int
    """Dynamics -> Parameters -> Maximum number of iterations"""
    ImplicitTolerance: float
    """Dynamics -> Parameters -> Tolerance"""

class OrcaFlexConstraint(OrcaFlexObject):
    pass

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
    NumberOfSections: int
    """Structure -> Sections -> Number of sections"""
    LineType: list[str]
    """Structure -> Line type"""
    Weighting: list[float]
    """Structure -> Weighting (when LengthAndEndOrientations = 'Calculated from end positions')"""
    Length: list[float]
    """Structure -> Length"""
    ExpansionFactor: list[float]
    """Structure -> Expansion Factor"""
    TargetSegmentLength: list[float]
    """Structure -> Target segment length"""
    NumberOfSegments: list[int]
    """Structure -> Number of segments"""
    ClashCheck: list[str]
    """Structure -> Clash check"""
    CumulativeLength: list[float]
    """Structure -> Cumulative values -> Length (m)"""
    CumulativeNumberOfSegments: list[float]
    """Structure -> Cumulative values -> Number of segments"""
    LogResults: str
    """Results -> Log results = 'Yes' (default) or 'No'"""


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

    def setLog(self, logResults: bool) -> None:
        """Defines if the results of the line should be stored (logged) or not"""
        if logResults: self.LogResults = 'Yes'
        else: self.LogResults = 'No'

    def setMeshSize(
            self,
            nSegs: int = None,
            targetLength: float = None
            ):
        """Set the length/number of segments for all sections"""
        for i in range(self.NumberOfSections):
            if nSegs != None:
                self.TargetSegmentLength[i] = orc.OrcinaDefaultReal()
                self.NumberOfSegments[i] = nSegs
            elif targetLength != None:
                self.TargetSegmentLength[i] = targetLength
            else:
                raise Exception('Error! nSegs or targetLengh must be provided.')


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

    SNcurveCount: int
    """S-N curves -> S-N curves -> Count"""
    SNcurveName: list[str]
    """S-N curves -> S-N curves -> Names"""
    SNcurveSpecificationMethod: str
    """S-N curves -> Data for S-N curve -> Specified by ('Parameters' or 'Table')"""
    SNcurvem1: float
    """S-N curves -> Data for S-N curve -> S-N curve parameters -> Low cycle region < N cycles -> m1"""
    SNcurveloga1: float
    """S-N curves -> Data for S-N curve -> S-N curve parameters -> Low cycle region < N cycles -> log(a1)"""
    SNcurveRegionBoundary: float
    """S-N curves -> Data for S-N curve -> S-N curve parameters -> Region boundary, N (cycles)"""   
    SNcurvem2: float
    """S-N curves -> Data for S-N curve -> S-N curve parameters -> Low cycle region < N cycles -> m2"""
    SNcurveloga2: float
    """S-N curves -> Data for S-N curve -> S-N curve parameters -> Low cycle region < N cycles -> log(a2)"""
    SNcurveEnduranceLimit: float
    """S-N curves -> Data for S-N curve -> S-N curve parameters -> Endurance limit"""
    SNcurveMeanStressModel: str 
    """S-N curves -> Data for S-N curve -> Mean stress model: 'None'; 'Goodman'; 'Soderberg'; 'Gerber'; 'Smith-Watson-Topper'"""

    def __selectSNCurveByName(self, name: str, environment: str) -> SNCurves.SNCurve:
        """Name (e.g, 'F1') and environment ('air' or 'seawater')"""
        return SNCurves.selectSNCurveByName(name, environment)


    def setSNCurve(self, SNCurve: SNCurves.SNCurve) -> None:
        """
        Set the parameters of the selected S-N curve to the analysis
        """
        SNCurve.setToAnalysis(self)

    def setSNCurveByNameAndEnv(self, name: str, environment: str) -> None:
        """
        Set the parameters the S-N curve selected based on its name (e.g., 'F3')
        and environment ('air' or 'seawater')
        """
        SNCurve = self.__selectSNCurveByName(name, environment)
        self.setSNCurve(SNCurve)


    def totalExposureTime(self) -> float:
        """Sum of exposure time of each load case"""
        s = 0
        for e in self.LoadCaseExposureTime: s += e
        return s

    def nodeArcLengthList(self) -> list[float]:
        """
        Returns a list with the arc length of each node
        """
        arcLList: list[float] = []
        for pointDetails in self.outputPointDetails:
            arcLList.append(pointDetails[0])
        return arcLList

    def getArcLengthDamageLifeList(self) -> list[list[float]]:
        """
        Returns a list of three parameters (table columns): 
        * arc length: position (meters) of each node
        * damage: maximum damage arround the section circunference of each node
        * life: minimum life (years) arround the section cicrunference of each node 
        """
        arcLengthList = self.nodeArcLengthList()
        zdlList: list[list[float]] = []
        secsPerYear = 365.25*24*3600 # used to the conversion from seconds to years

        for nodeDamageRst, z in zip(self.overallDamage, arcLengthList):
            d_max = 0.0
            l_min = nodeDamageRst[0][1]
            for d, l in nodeDamageRst: # max around the circunference
                d_max = max(d_max, d) 
                l_min = min(l_min, l)
            zdlList.append([z, d_max, l_min/secsPerYear])

        return zdlList
    
    def getDamageList(self) -> list[float]:
        """
        Returns a list with the calculated damage in each node
        """
        zdlList =  self.getArcLengthDamageLifeList()
        damageList: list[float] = []
        for _, d, _ in zdlList: damageList.append(d)
        return damageList

    def getLifeList(self) -> list[float]:
        """
        Returns a list with the calculated life (years) in each node
        """
        zdlList =  self.getArcLengthDamageLifeList()
        lifeList: list[float] = []
        for _, _, l in zdlList: lifeList.append(l)
        return lifeList

    def getArcLengthDamageLifeListAsDF(self) -> pd.DataFrame:
        """
        Returns a DataFrame of three parameters (table columns): 
        * arc length: position (meters) of each node
        * damage: maximum damage arround the section circunference of each node
        * life: minimum life (years) arround the section cicrunference of each node 
        """        
        zdlList = self.getArcLengthDamageLifeList()
        cols = ['Arc length (m)', 'Damage', 'Life (years)']
        return pd.DataFrame(zdlList, columns=cols)

