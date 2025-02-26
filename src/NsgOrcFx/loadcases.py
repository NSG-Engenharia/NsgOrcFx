import OrcFxAPI as __ofx
from .auxfuncs import *
import pandas as pd
import math


def __setEnvironment(
        model: __ofx.Model,
        waveDirection: float,
        waveType: str,
        waveHeight: float,
        wavePeriod: float,
        nTimesPeriodStage1: float = 5,
        stormDuration: float = 10800,
        calcGamma: bool = True,
        reducedIrregDuration: float = None,
        largestFallOrRise: str = 'rise',
        waveTrainIndex: int = 0,
        extremeWavePosition: list[float] = [0.,0.]        
        ):
    """
    `waveTrainIndex` was keept for legacy compatibility
    """
    env = model.environment
    env.WaveDirection = waveDirection

    # regular wave
    if isRegularWave(waveType): 
        env.WaveHeight = waveHeight
        env.WavePeriod = wavePeriod
        model.general.StageDuration[0] = 1*wavePeriod
        model.general.StageDuration[1] = nTimesPeriodStage1*wavePeriod

    # irregular wave
    else: 
        if calcGamma: env.WaveGamma = 6.4*wavePeriod**(-.491)
        env.WaveTp = wavePeriod
        env.WaveHs = waveHeight

        #reset wave time origin for each case
        env.WaveTimeOrigin = 0.0

        if reducedIrregDuration == None:
            model.general.StageDuration[0] = 1*wavePeriod
            model.general.StageDuration[1] = stormDuration
        else:
            SetReducedSimDuration(
                model, reducedIrregDuration, stormDuration, 
                largestFallOrRise, extremeWavePosition)



def GenLoadCases(
        model: __ofx.Model,
        waveType: str, 
        waveDirList: list[float],
        waveHeightList: list[float],
        wavePeriodList: list[float],
        outFolder: str,
        nTimesPeriodStage1: float = 5,
        stormDuration: float = 10800,
        calcGamma: bool = True,
        reducedIrregDuration: float = None,
        largestFallOrRise: str = 'rise',
        waveTrainIndex: int = 0,
        extremeWavePosition: list[float] = [0.,0.]
        ) -> None:
    """
    Generates load cases from the current model for the list of wave direction, 
    height and period provided and saves the files at the specified folder
    
    * waveType: 'regular' (e.g., Dean stream) or 'JONSWAP'
    * waveDirList: list of wave direction
    * waveHeightList: list of wave height (Hs for irregular wave)
    * wavePeriodList: list of wave period (Tp for erregular wave)
    * outFolder: folder to save the generated LC files
    * nTimesPeriodStage1: simulation duration as number of periods (regular wave)
    * stormDuration: simulation total duration (irregular wave)
    * calcGamma: if the gamma should be calculated base on formula gamma = 6.4 x Tp ^ -0.491
    * reducedIrregDuration: if not `None`, the simulation duration, reduced based on the largest 'fall' of 'rise' during the `simDuration`
    * largestFallOrRise: if `reducedIrregDuration != None`, if the extreme event is searched based on the largest 'fall' or 'rise'
    * waveTrainIndex: keept for legacy compatibility. This input is ignored. The "Wave time origin" for all wave trains are changed when `reducedIrregDuration = True`.
    * extremeWavePosition: if `reducedIrregDuration != None`, position to search for the largest 'rise' or 'fall'
    """
    __caseListFile ='_CaseList.xlsx' # file to save the cases list
    env = model.environment
    env.WaveType = waveType
    if env.NumberOfWaveTrains > 1: env.SelectedWaveTrainIndex = waveTrainIndex

    nCases = len(waveHeightList) * len(waveDirList) * len(wavePeriodList)
    nDigits = math.floor(math.log10(nCases)) + 1
    def __fi(n: int, digits: int) -> float:
        s = str(n)
        while len(s) < digits:
            s = '0'+s
        return s

    CaseList = []
    cont=0

    for height in waveHeightList:
        for period in wavePeriodList:
            for direction in waveDirList:
                cont += 1

                if isRegularWave(waveType):
                    caseName = f'LC{__fi(cont, nDigits)}_H={height:0.2f}m_T={period:00.2f}s_dir={direction}'
                else:
                    caseName = f'LC{__fi(cont, nDigits)}_Hs={height:0.2f}m_Tp={period:00.2f}s_dir={direction}'
    
                __setEnvironment(
                    model, direction, waveType, height, period, 
                    nTimesPeriodStage1, stormDuration, calcGamma, 
                    reducedIrregDuration, largestFallOrRise, waveTrainIndex, extremeWavePosition)                

                fullPath = os.path.join(outFolder, caseName+'.dat')
                model.SaveData(fullPath)                    

                CaseList.append([caseName+'.dat', height, period, direction])

    df = pd.DataFrame(CaseList, columns=['File','Height(m)','Period(s)','Direction(deg)'])
    fullPath = os.path.join(outFolder, __caseListFile)
    df.to_excel(fullPath)
