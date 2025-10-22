"""
# Library of complementary tools for the OrcaFlex API (OrcFxAPI)
#
#
#
"""
from __future__ import annotations

__author__ = "NSG Engenharia"
__copyright__ = "Copyright 2023"
__credits__ = ["Gabriel Nascimento"]
__license__ = "GPL"
__version__ = "1.0.0"
__maintainer__ = "Gabriel Nascimento"
__email__ = "gabriel.nascimento@nsgeng.com"
__status__ = "Development"


from typing import Union
from types import FunctionType

import OrcFxAPI
from OrcFxAPI import *

from .classes import *
from .sortlines import *
from .objauxfuncs import *
from .modal import *
from .loadcases import *
from .utils import *
from .raos import *
from .constraintloads import ExtremeLoadsFromConstraints
from .multiproc import ProcMultiThread

# ======= CONSTANTS ======== #
requiredOrcFxVer = '11.3a'

# ==== AUXILIARY METHODS ==== #
class AuxFuncs:
    def checkOrCreateFolder(self, path: str) -> bool:
        """
        Check if the folder exists and, case not, try to create
        Returns false if don't exists and can't create
        """
        return afCheckOrCreateFolder(path)

auxfuncs = AuxFuncs()

# ==== MODEL CLASS ==== #
class Model(orc.Model):
    general: OrcaFlexGeneralObject
    environment: OrcaFlexEnvironmentObject
    auxfuncs = auxfuncs

    def __wrapBasicObjets(self, name: str, obj: OrcaFlexObject) -> "OrcaFlexObject":
        if name == 'general':
            return OrcaFlexGeneralObject(obj)
        elif name == 'environment':
            return OrcaFlexEnvironmentObject(obj)
        else:
            return obj

    def __getattribute__(self, name: str) -> "OrcaFlexObject":
        obj = super().__getattribute__(name)
        if name != '_Model__wrapBasicObjets':
            return self.__wrapBasicObjets(name, obj)
        else:            
            return obj

    def __checkOrcaFlexVersion(self) -> bool:
        """Return True if the installed version of OrcaFlex is equal or newer than the required"""
        if not checkOrcaFlexVersion(requiredOrcFxVer):
            raise Exception(f'The OrcaFlex version is older then {requiredOrcFxVer}.')    

    def getOrcaVersion() -> str:
        """Return the installed OrcaFlex version as string"""
        return getOrcaVersion()

    def __getitem__(self, name: str) -> OrcaFlexObject:
        # return OrcaFlexObject(super().__getitem__(name))  # this generated error when calling methods with returned items
        return super().__getitem__(name)
    
    def Save(self, file: str) -> None:
        """
        Save data if file extension is '.dat' or '.yml' and simulation if '.sim'
        """
        extension = getFileExtension(file)
        if extension == '.dat' or extension == '.yml':
            self.SaveData(file)
        elif extension == '.sim':
            self.SaveSimulation(file)
        else:
            raise Exception(f'Extension "{extension}" not allowed.')

    def findLineByName(self, name: str) -> OrcaFlexLineObject:
        """Find a line object by its name"""
        obj = self[name]
        return OrcaFlexLineObject(obj)
    
    def getAllLines(self, includeStiffeners: bool = True) -> LineSelection:
        """Returns a list of all line objects"""
        lineList = LineSelection(self)
        for obj in self.objects:
            if obj.type == orc.ObjectType.Line:
                lineList.append(OrcaFlexLineObject(obj))
                
        if not includeStiffeners: # remove the stiffeners (line internally created by OrcaFlex due to attachements)
            stiffenerNames = []
            for line in lineList: stiffenerNames.extend(line.AttachmentName)                
            newList = []
            for line in lineList:
                if not line.name in stiffenerNames: newList.append(line)
            lineList = newList
            
        return lineList

    def getLineList(
            self, 
            groupName: Union[str, None] = None, 
            includeSubgroups: bool = False
            ) -> LineSelection:
        """
        Returns all lines in the model which belongs to the defined group with or not its subgroups
        """            
        # if groupName:
        #     grouObj = self[groupName]
        #     selectedList = list(grouObj.GroupChildren(recurse=includeSubgroups))
        # else:
        #     selectedList = list(self.objects)

        # for obj in selectedList:
        #     if obj.type == orc.ObjectType.Line:
        #         result.append(OrcaFlexLineObject(obj))
        #     # elif groupName and includeSubgroups and obj.type == orc.ObjectType.BrowserGroup:
        #     #     result.extend(self.getLineList(obj.Name))
        result = LineSelection(self)
        getLinesToList(self, groupName, includeSubgroups, result)
        return result
    
    def sortPathInterconnectedLines(
            self,
            lineList: list[OrcaFlexLineObject]
            ) -> LineSelection:
        """
        Returns a sorted list of interconnected lines, based on its connections (e.g., path from first to last)
        The result is unpredictable if not all lines are connected or if there are connection between more than two lines
        """              
        newList = sortPathInterconnectedLines(lineList)
        returnList = LineSelection(self)
        for obj in newList: returnList.append(obj)
        return returnList
    
    def getUnconnectedConstraints(self) -> list[OrcaFlexObject]:
        """
        Returns the list of constraints to which there is not a line connected
        """
        constraintChildren = {}
        for obj in self.objects:
            if obj.type == orc.ObjectType.Constraint:
                constraintChildren[obj.name] = 0
        
        lines = self.getLineList()  
        for line in lines:
            for endObj in [line.EndAConnection, line.EndBConnection]:
                if endObj in constraintChildren:
                    constraintChildren[endObj] += 1

        resultList = []
        for constraint, n in constraintChildren.items():
            if n == 0:
                resultList.append(constraint)

        return resultList
    
    def CreateLine(self, name: Optional[str] = None) -> OrcaFlexLineObject:
        newObj = self.CreateObject(ObjectType.Line, name)
        return OrcaFlexLineObject(newObj)    

    def deleteObjs(self, objects: list[str | OrcaFlexObject]):
        for obj in objects:
            self.DestroyObject(obj)

    def SetReducedSimulationDuration(self, 
            reducedDuration: float, 
            refstormduration = 10800.,
            fallOrRise: str ='rise', # 'rise' or 'fall'
            extremeWavePosition: list[float] = [0.,0.],
            iniWaveTimeOrigin: float | None = 0.0
            ) -> None:
        '''
        Reduces the simulation time for irreguar wave based on the highest fall/rise
            - reducedDuration: The simulation time after reducing. Used for the Stage 1. 
            - refstormduration: wave duration along which the highest rise/fall will be searched
            - fallOrRise: if time selection is based on the largest 'fall' or 'rise' event
            - waveTrainIndex: based on which wave train largest fall or rise must be selected
            - extremeWavePosition: position to search the largest 'fall' or 'rise'
            - iniWaveTimeOrigin: initial wave time origin to search for the next extreme event. If `None`, keep the value in the model for each wave train.

            Obs.: the Tp value defined in the model will be used for the Stage 0.
        ''' 
        SetReducedSimDuration(self, reducedDuration, refstormduration, fallOrRise, extremeWavePosition, iniWaveTimeOrigin)

    def GenerateLoadCases(
            self,
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
        
        * waveType: e.g., 'Dean stream' (regular) or 'JONSWAP' (irregular)
        * waveDirList: list of wave direction
        * waveHeightList: list of wave height (Hs for irregular wave)
        * wavePeriodList: list of wave period (Tp for erregular wave)
        * outFolder: folder to save the generated LC files
        * nTimesPeriodStage1: simulation duration as number of periods (regular wave)
        * stormDuration: simulation total duration (irregular wave)
        * calcGamma: if the gamma should be calculated base on formula gamma = 6.4 x Tp ^ -0.491
        * reducedIrregDuration: if not `None`, the simulation duration, reduced based on the largest 'fall' of 'rise' during the `simDuration`
        * largestFallOrRise: if `reducedIrregDuration != None`, if the extreme event is searched based on the largest 'fall' or 'rise'
        * waveTrainIndex: which Wave Train should be considered
        * extremeWavePosition: if `reducedIrregDuration != None`, position to search for the largest 'rise' or 'fall'
        """
        GenLoadCases(
            self, waveType, waveDirList, waveHeightList, wavePeriodList, outFolder,
            nTimesPeriodStage1, stormDuration, calcGamma, reducedIrregDuration,
            largestFallOrRise, waveTrainIndex, extremeWavePosition)


    def CalculateModal(
            self, 
            lineName: str | None = None,
            firstMode: int = -1,
            lastMode: int = -1            
            ) -> Modes:
        """
        Performs modal analysis and returns the result (Modes object)
        If no lineName is especified, includes all lines the analysis
        """

        # check if static calculation was performed
        if self.state == orc.ModelState.Reset: 
            self.CalculateStatics()

        if lineName == None: includeCouped = True
        else: includeCouped = False
        
        specs = orc.ModalAnalysisSpecification(True, firstMode, lastMode, includeCouped) # TODO: check other default inputs
        
        if lineName != None: obj = self[lineName]
        else: obj = self

        modes = Modes(obj, specs)

        return modes

    def SaveRAOplots(self, folder: str, vesseltype: OrcFxAPI.OrcaFlexObject = None, figtype: str = 'png') -> None:
        '''
        Generate the Amp and Phase RAO plots
        * folder: where to save the plot files
        * vesseltype: vessel type object containing the RAO to be plotted. All, if 'None'.
        * figtype: extension of the figure files ('png', 'svg', 'pdf' or 'eps')
        '''        
        # GenRAOplots(self, folder, figtype, vesseltype)
        raoPlots = RaoPlot()
        raoPlots.raoOutputFolder = folder
        if vesseltype == None:
            vesselTypeList = [obj for obj in self.objects if obj.type == OrcFxAPI.ObjectType.VesselType]
        else:
            vesselTypeList = [vesseltype]

        raoPlots.FigFormat = figtype

        for vt in vesselTypeList:
            raoPlots.GetRAOData(vt)


    def ProcessExtremeResponses(
            self,
            vesselName: str,
            position: list[float],
            waveDirsHsTp: dict[str, list[tuple[float, float]]],
            outFile: str,
            outFolderLCs: str|None = None,
            stormDuration: float = 3.0,
            northDir: float|None = None,
            waveTrainIndex: int|None = None,
            ):
        """
        Process extreme responses for the vessel.
        * model: OrcaFlex model object
        * position: list with the [x,y,z] coordinates of the response output point,
            relative to the vessel origin
        * vesselName: name of the vessel in the model
        * waveDirsHsTp: dictionary with the wave directions (coming from) as keys,
            and a list of (Hs,Tp) tuples as values
        * outFile: path to the output Excel file
        * outFolderLCs: folder to save the load case files. If None, load case files are not saved.
        * stormDuration: duration of the storm for extreme response calculations (hours)
        * northDir: North direction from the x-axis, as defined by the OrcaFlex convention.
            If None, use the model definition.
        * waveTrainIndex: index of the wave train to use. If None, use the model definition.
        """
        from .vessel import VesselResponseList
        response = VesselResponseList()
        response.ProcessExtremeResponses(
            model=self,
            vesselName=vesselName,
            position=position,
            waveDirsHsTp=waveDirsHsTp,
            outFile=outFile,
            outFolderLCs=outFolderLCs,
            stormDuration=stormDuration,
            northDir=northDir,
            waveTrainIndex=waveTrainIndex
        )


class LineSelection(list[OrcaFlexLineObject]):
    def __init__(self, model: Model):
        super().__init__()
        self.model = model

    def setGroup(self, groupName: str) -> None:
        group = self.model[groupName]
        for line in self:
            line.groupParent = group

    def setLog(self, logResults: bool) -> None:
        """Defines if the results of the line should be stored (logged) or not for all lines in this selection"""
        for line in self:
            line.setLog(logResults)

    def setMeshSize(
            self,
            nSegs: int = None,
            targetLength: float = None
            ):
        """Set the length/number of segments for all sections of all lines in this selection"""
        for line in self:
            line.setMeshSize(nSegs, targetLength)

    def selectByName(
            self, 
            name: Union[str, list[str]]
            ) -> LineSelection:
        if type(name) == str: nameList = [name]
        else: nameList = name
        resultList = LineSelection(self.model)
        for line in self:
            if line.Name in nameList:
                resultList.append(line)
        return resultList

    def selectByType(
            self, lineType: Union[list[str], str], 
            partialMatch: bool = False
            ) -> LineSelection:
        if type(lineType) == str: lineTypeGroup = [lineType]
        else: lineTypeGroup = lineType
        resultList = LineSelection(self.model)
        for line in self:
            for lt in line.LineType:
                if strInStrList(lt, lineTypeGroup, partialMatch):
                    resultList.append(line)
        return resultList

    def selectLinesByPosition(
            self,
            xLimits: tuple[Union[float,None], Union[float,None]] = (None, None),
            yLimits: tuple[Union[float,None], Union[float,None]] = (None, None),
            zLimits: tuple[Union[float,None], Union[float,None]] = (None, None)
            ) -> LineSelection:
        """
        Select lines in the model based on its ends position
        """
        if not len(self):
            raise Exception('Error! This selction is empty.')

        # cloneModel = orc.Model() # creates a 'dummy' model (only to set fixed connections and get global coords)
        resultList = LineSelection(self.model)
        for line in self:
            # clone = line.CreateClone(model=cloneModel) # copy object to 'dummy' model
            clone = line.CreateClone() # copy object to 'dummy' model
            clone.EndAConnection = 'Fixed' # ensures global coordinates
            clone.EndBConnection = 'Fixed' # ensures global coordinates
            minLimits = [xLimits[0], yLimits[0], zLimits[0]]            
            maxLimits = [xLimits[1], yLimits[1], zLimits[1]]
            xVls = [clone.EndAX, clone.EndBX]
            yVls = [clone.EndAY, clone.EndBY]
            zVls = [clone.EndAZ, clone.EndBZ]
            values = [xVls, yVls, zVls]
            include = True
            for vEnds, minLim, maxLim in zip(values, minLimits, maxLimits):
                for v in vEnds:
                    if minLim != None: # check min
                        if v < minLim: include = False
                    if maxLim != None: # check max
                        if v > maxLim: include = False
            if include: resultList.append(line)
            # cloneModel.DestroyObject(clone) # free memory
            self.model.DestroyObject(clone) # free memory

        return resultList


