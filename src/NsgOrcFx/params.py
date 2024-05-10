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

class _DataGeneralObject(__DataOrcFxObj):
    # Analysis page
    StageCount: int
    """Analysis -> Stages -> Number of stages"""
    StageDuration: list[float]
    """Analysis -> Stages -> Duration (Time)"""

    # Dynamics page
    ImplicitConstantTimeStep: float
    """Dynamics -> Parameters -> Time step (Time)"""
    ImplicitConstantMaxNumOfIterations: int
    """Dynamics -> Parameters -> Maximum number of iterations"""
    ImplicitTolerance: float
    """Dynamics -> Parameters -> Tolerance"""    
    TargetLogSampleInterval: float
    """Dynamics -> Logging -> Target sample interval (Time)"""

class _DataEnvinronmentObject(__DataOrcFxObj):
    # Sea page
    WaterSurfaceZ: float
    """Sea -> Surface Z (m)"""
    KinematicViscosity: float
    """Sea -> Kinematic viscosity (m^2/s)"""
    SeaTemperature: float
    """Sea -> Temperature (°C)"""
    ReynoldsNumberCalculation: str
    """
    Sea -> Reynolds number calculation\n
      * possible values: Nominal; Cross flow; Flow direction
    """
    HorizontalWaterDensityFactor: float
    """Sea -> Horizontal density variation -> Horizontal water density factor"""
    VerticalDensityVariation: str

    # Sea density page
    """
    Sea density -> Vertical density variation -> Vertical density variation\n
      * possible values: 'Constant'; 'Bulk modulus'; 'Interpolated'
    """
    Density: float
    """
    Sea density -> Vertical density variation -> Water density -> Density (M/L^3)\n
    Applicable when `VerticalDensityVariation = 'Constant'`
    """
    SurfaceDensity: float
    """
    Sea density -> Vertical density variation -> Water density -> Surface density (Mass/Length^3)\n
    Applicable when `VerticalDensityVariation = 'Bulk modulus'`
    """
    BulkModulus: float
    """
    Sea density -> Vertical density variation -> Water density -> Bulk modulus (Pressure)\n
    Applicable when `VerticalDensityVariation = 'Bulk modulus'`
    """
    NumberOfDensityLevels: int    
    """
    Sea density -> Vertical density variation -> Water density -> Profile table -> Number of rows\n
    Applicable when `VerticalDensityVariation = 'Interpolated'`
    """
    DensityDepth: list[float]
    """
    Sea density -> Vertical density variation -> Water density -> Profile table -> Depth (Length)\n
    Applicable when `VerticalDensityVariation = 'Interpolated'`
    """
    DensityValue: list[float]
    """
    Sea density -> Vertical density variation -> Water density -> Profile table -> Density (Mass/Length^3)\n
    Applicable when `VerticalDensityVariation = 'Interpolated'`
    """

    # Seabed page
    SeabedType: str
    """
    Seabed -> Shape -> Type
    possible values: 'Flat'; 'Profile'; '3D'
    """
    SeabedOriginX: float
    """
    Seabed -> Shape -> Seabed origin (Length) -> X
    """
    SeabedOriginY: float
    """
    Seabed -> Shape -> Seabed origin (Length) -> Y
    """
    SeabedOriginZ: float
    """
    Seabed -> Shape -> Seabed origin (Length) -> Z
    """
    WaterDepth: float
    """
    Seabed -> Shape -> Seabed origin (Length) -> Depth
    """
    SeabedSlopeDirection: float
    """
    Seabed -> Shape -> Direction (angle)
    """
    SeabedSlope: float
    """
    Seabed -> Shape -> Slope (angle)
    """
    SeabedModel: str
    """
    Seabed -> Seabed model
      * possible values: 'Elastic'; 'Nonlinear soil model'
    """
    SeabedNormalStiffness: float
    """
    Seabed -> Stiffness & damping -> Stiffeness (Force/Length/Length^2) -> Normal\n
    Applicable when `SeabedModel = 'Elastic'`
    """
    SeabedShearStiffness: float
    """
    Seabed -> Stiffness & damping -> Stiffeness (Force/Length/Length^2) -> Shear\n
    Applicable when `SeabedModel = 'Elastic'`
    """
    SeabedDamping: float
    """
    Seabed -> Stiffness & damping -> Damping (% of critical)\n
    Applicable when `SeabedModel = 'Elastic'`
    """

    # Wave page
    SelectedWaveTrainIndex: int
    """Wave -> Wave trains -> Wave train selected (index)"""
    SelectedWaveTrain: str
    """Wave -> Wave trains -> Wave train selected (name)"""
    NumberOfWaveTrains: int
    """Wave -> Wave trains -> Number of wave trains"""
    WaveName: list[str]
    """Wave -> Wave trains -> Name of all wave trains"""
    WaveDirection: float
    """Wave -> Data for the selected wave train -> Wave data -> Direction (Angle)"""
    WaveHeight: float
    """
    Wave -> Data for the selected wave train -> Wave data -> Height (Length)\n
    applicable when `WaveType` is a regular wave
    """
    WavePeriod: float
    """
    Wave -> Data for the selected wave train -> Wave data -> Period (Time)\n
    applicable when `WaveType` is a regular wave
    """
    WaveOriginX: float
    """
    Wave -> Data for the selected wave train -> Wave data -> Wave Origin -> X (Length)
    """
    WaveOriginY: float
    """
    Wave -> Data for the selected wave train -> Wave data -> Wave Origin -> Y (Length)
    """
    WaveTimeOrigin: float
    """
    Wave -> Data for the selected wave train -> Wave data -> Wave time origin (Time)
    """
    WaveType: str 
    """
    Wave -> Data for the selected wave train -> Wave data -> Wave type
    * possible values: 'Airy'; 'Dean stream'; "Stokes' 5th"; 'Cnoidal'; 'JONSWAP'; 'ISSC'; 'Ochi-Hubble'; 'Torsethaugen'; 'Gaussian swell'; 'User defined spectrum'; 'User specified components'; 'Time history'; 'Response calculation'
    """
    WaveCurrentSpeedInWaveDirectionAtMeanWaterLevel: float
    """
    Wave -> Data for the selected wave train -> Wave data -> Current speed in wave direction (Length/Time)
    """
    WaveStreamFunctionOrder: int
    """
    Wave -> Data for the selected wave train -> Wave data -> Stream function order\n
    applicable when `WaveType = 'Dean stream'`
    """
    WaveHs: float
    """
    Wave -> Data for the selected wave train -> Wave data -> Hs (Length)\n
    applicable when `WaveType` is irregular
    """
    WaveTz: float
    """
    Wave -> Data for the selected wave train -> Wave data -> Tz (Time)\n
    applicable when `WaveType` is irregular
    """
    WaveJONSWAPParameters: str
    """
    Wave -> Data for the selected wave train -> Spectral parameters specification
    * possible values: 'Automatic'; 'Partially specified'; 'Fully specified'
    """
    WaveGamma: float
    """
    Wave -> Data for the selected wave train -> Spectral parameters -> Gamma (JONSWAP spectrum shape)\n
    applicable when:
        * `WaveType = 'JONSWAP'`
        * `WaveJONSWAPParameters = 'Partially specified'` or  `WaveJONSWAPParameters = 'Fully specified'`
    """
    WaveAlpha: float
    """
    Wave -> Data for the selected wave train -> Spectral parameters -> Alpha (JONSWAP spectrum factor)\n
    applicable when:
        * `WaveType = 'JONSWAP'`
        * `WaveJONSWAPParameters = 'Fully specified'`
    """
    WaveSigma1: float
    """
    Wave -> Data for the selected wave train -> Spectral parameters -> Sigma 1 (JONSWAP spectrum factor)\n
    applicable when:
        * `WaveType = 'JONSWAP'`
        * `WaveJONSWAPParameters = 'Fully specified'`
    """
    WaveSigma2: float
    """
    Wave -> Data for the selected wave train -> Spectral parameters -> Sigma 2 (JONSWAP spectrum factor)\n
    applicable when:
        * `WaveType = 'JONSWAP'`
        * `WaveJONSWAPParameters = 'Fully specified'`
    """
    Wavefm: float
    """
    Wave -> Data for the selected wave train -> Spectral parameters -> fm (Frequency) \n
    applicable when:
        * `WaveType = 'JONSWAP'`
        * `WaveJONSWAPParameters = 'Partially specified'` or  `WaveJONSWAPParameters = 'Fully specified'`
    """
    WaveTp: float
    """
    Wave -> Data for the selected wave train -> Spectral parameters -> Tp (Time)\n
    applicable when:
        * `WaveType = 'JONSWAP'`
        * `WaveJONSWAPParameters = 'Partially specified'` or  `WaveJONSWAPParameters = 'Fully specified'`
    """

    UserSpecifiedRandomWaveSeeds: str
    """
    Wave -> Data for the selected wave train -> User specified seeds
    – possible values: No; Yes
    \nApplicable when `WaveType` is irregular
    """
    WaveSeed: int
    """
    Wave -> Data for the selected wave train -> Components -> Seed
    \nApplicable when `WaveType` is irregular
    """
    WaveNumberOfComponents: int
    """
    Wave -> Data for the selected wave train -> Components -> Number
    \nApplicable when `WaveType` is irregular
    """
    WaveSpectrumMinRelFrequency: float
    """
    Wave -> Data for the selected wave train -> Components -> Relative frequency range -> Minimum
    – possible values: No; Yes
    \nApplicable when `WaveType` is irregular
    """
    WaveSpectrumMaxRelFrequency: float
    """
    Wave -> Data for the selected wave train -> Components -> Relative frequency range -> Maximum
    – possible values: No; Yes
    \nApplicable when `WaveType` is irregular
    """
    WaveSpectrumMaxComponentFrequencyRange: float
    """
    Wave -> Data for the selected wave train -> Components -> Maximum component frequency range (Hz)
    – possible values: No; Yes
    \nApplicable when `WaveType` is irregular
    """

    KinematicStretchingMethod: str
    """
    Wave -> Kinematic streching method
    – possible values: Vertical stretching; Wheeler stretching; Extrapolation stretching
    """
    WaveFrequencySpectrumDiscretisationMethod: str
    """
    Wave -> Frequency spectrum discretisation method
    – possible values: Arithmetic progression; Geometric progression; Equal energy; Equal energy, 9.3a, deprecated; Equal energy, legacy, deprecated
    \nApplicable when `WaveType` is irregular
    """







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