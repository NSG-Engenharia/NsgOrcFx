from typing import Any
from OrcFxAPI import OrcaFlexObject

class __DataOrcFxObj(object):
    Name: str    
    """Object name"""
    __ofxObj: OrcaFlexObject

    def __init__(self, ofxObj: OrcaFlexObject) -> None:
        # super().__setattr__('__ofxObj', ofxObj)
        # object.__setattr__(self, '__ofxObj', ofxObj)
        self.__ofxObj = ofxObj

    def __getattr__(self, name: str) -> Any:
        if name != '_DataOrcFxObj__ofxObj':
            return self.__ofxObj.__getattr__(name)
        else:
            return self.__getattr__(name)

    def __setattr__(self, name: str, value: Any) -> None:
        if name == '_DataOrcFxObj__ofxObj':
            super().__setattr__(name, value)
        else:
            OrcaFlexObject.__setattr__(self.__ofxObj, name, value)

class _GeneralObject(__DataOrcFxObj):
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

class _DataLineObject(__DataOrcFxObj):
    EndAConnection: str 
    """End connections -> End A -> Connect to object"""
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

class _DataFatigueAnalysisObject(__DataOrcFxObj):
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