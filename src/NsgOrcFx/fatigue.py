from typing import Optional
import os
import pandas as pd
import OrcFxAPI as _ofx
from .sncurves import *
from .objauxfuncs import *
from . import params

class FatigueAnalysis(_ofx.FatigueAnalysis):
    data: params._DataFatigueAnalysisObject

    def __init__(self, filename: Optional[str] = None, threadCount: Optional[int] = None) -> None:
        super().__init__(filename, threadCount)
        object.__setattr__(self, 'data', params._DataFatigueAnalysisObject(self))

    def __selectSNCurveByName(self, name: str, environment: str) -> SNCurve:
        """Name (e.g, 'F1') and environment ('air' or 'seawater')"""
        return selectSNCurveByName(name, environment)

    def addLoadCase(
            self, 
            simFile: str, 
            lineName: str = None, 
            simPeriod: list[float] = [0,0], 
            exposureTime: float = 365.25*24) -> None:
        """
        Add a new load case
        * simFile: path to the simulation file
        * lineName: if 'None', select the first line in the model
        * simPeriod: list with [start,end]. If end = 0, set to the total simulation duration
        * exposureTime: exposure time in hours
        """        
        # if the last load case is already defined, creates one more
        if self.LoadCaseFileName[-1] != '': self.LoadCaseCount += 1
        
        basePath = os.getcwd()
        self.LoadCaseFileName[-1] = os.path.join(basePath, simFile)
        model = _ofx.Model(simFile)

        if lineName == None:
            lines = getLinesToList(model)
            lineName = lines[0].name
        self.data.LoadCaseLineName[-1] = lineName

        if simPeriod[1] == 0: simPeriod[1] = model.general.StageEndTime[-1]
        self.PeriodFrom[-1] = simPeriod[0]
        self.PeriodTo[-1] = simPeriod[1]

        self.LoadCaseExposureTime[-1] = exposureTime

    def addAnalysisData(
            self, 
            arcLengthInterval: list[float] = [0,0], 
            radialPosition: str = 'Outer', 
            SCF: float = 1.0, 
            thicknessFactor: float = 1.0,
            SnCurveIndex: int = 0
            ):
        """
        Add a new analysis data
        * arcLengthInterval: list [from, to] with the from and to arc lengths. Will be set to the entire line length, if to = 0
        * radialPosition:
        * SCF: Stress Concentration Factor
        * thicknessFactor: thickness factor
        * snCurveIndex: index of the list in the S-N curve page
        """
        self.ArclengthIntervalsCount += 1
        # analysisIndex = self.ArclengthIntervalsCount - 1
        lineName = self.data.LoadCaseLineName[0]
        modelFile = self.data.LoadCaseFileName[0]
        model = _ofx.Model(modelFile)
        line = model[lineName]
        if arcLengthInterval[1] == 0: arcLengthInterval[1] = line.CumulativeLength[-1]
        self.FromArclength[-1] = arcLengthInterval[0]
        self.ToArclength[-1] = arcLengthInterval[1]
        self.RadialPosition[-1] = radialPosition
        self.SCF[-1] = SCF
        self.ThicknessCorrectionFactor[-1] = thicknessFactor
        snCurvaName = self.data.SNcurveName[SnCurveIndex]
        self.AnalysisDataSNcurve[-1] = snCurvaName



    def addSNCurve(self, SNCurve: SNCurve) -> int:
        """
        Set the parameters of the selected S-N curve to the analysis
        Return the index of the new S-N curve created
        """
        self.SNcurveCount += 1
        index = self.SNcurveCount - 1
        SNCurve.setToAnalysis(self, index)
        return index

    def addSNCurveByNameAndEnv(self, name: str, environment: str) -> int:
        """
        Set the parameters the S-N curve selected based on its name (e.g., 'F3')
        and environment ('air' or 'seawater')
        * name: S-N curve name (e.g., 'F3')
        * environment: S-N curve environment ('air' or 'seawater')
        \nReturns the index of the new S-N curve created
        """
        SNCurve = self.__selectSNCurveByName(name, environment)
        return self.addSNCurve(SNCurve)


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
    
    def totalExposureTime(self) -> float:
        """Return the sum of exposure time defined for each load case"""
        return sum(self.LoadCaseExposureTime)

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

