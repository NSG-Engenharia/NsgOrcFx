"""
Extract constraint loads from OrcaFlex simulation files
"""

import os
import OrcFxAPI as ofx
import numpy as np
import pandas as pd

class _Units:
    def __init__(self, file: str):
        model = ofx.Model(file)
        self.__force = model.general.ForceUnits
        self.__length = model.general.LengthUnits    
        self.__time = model.general.TimeUnits 
    @property
    def force(self) -> str: return self.__force    
    @property
    def length(self) -> str: return self.__length
    @property
    def moment(self) -> str: return self.force + '.' + self.length    
    @property
    def time(self) -> str: return self.__time
    def byStr(self, loadType: str) -> str:
        lt = loadType.upper()
        if lt == 'FORCE': return self.force
        elif lt == 'MOMENT': return self.moment
        elif lt == 'TIME': return self.time
        elif lt == 'LENGTH': return self.length
        else:
            raise Exception(f'Load type {loadType} not recognized.')

class CriticalLCs:
    def __init__(self, extremesByObj: dict):
        self.__criticalLCs: dict[list] = {}
        for objRsts in extremesByObj.values():
            for rstItem in objRsts:
                LC, time = rstItem[0], rstItem[1]
                if not LC in self.__criticalLCs.keys():
                    self.__criticalLCs[LC] = []
                if not time in self.__criticalLCs[LC]:
                    self.__criticalLCs[LC].append(time)
    def isIncluded(self, LC: str, time: None|float=None):
        if LC in self.__criticalLCs.keys():
            if time == None:
                return True
            else:
                if time in self.__criticalLCs[LC]:
                    return True
        return False

class ResultDefinitions:
    __loadTypes = ['force', 'moment']
    __directions = ['x','y','z','Total']
    def __init__(
            self, 
            units: _Units, 
            in_frame: bool=True, 
            local: bool=True
            ):
        if in_frame: self.frame = 'In-frame'
        else: self.frame = 'Out-frame'
        self.units = units

        if local: self.ref = 'L'
        else: self.ref = 'G'

    def __loadTypeFirstChar(self, loadType: str) -> str:
        return loadType[:1].upper()   

    def __loadTypeTitle(self, loadType: str) -> str:
        return f'{loadType.capitalize()} [{self.units.byStr(loadType)}]'

    def __isResultant(self, direction: str) -> bool:
        return direction == self.__directions[-1]

    def tag(self, loadType: str, direction: str) -> str:
        if self.__isResultant(direction): d = ''
        else: d = direction
        return self.__loadTypeFirstChar(loadType) + d

    @property
    def tags(self) -> list[str]:
        tagList = []
        for lt in self.__loadTypes:
            for d in self.__directions:
                tagList.append(self.tag(lt, d))
        return tagList

    @property
    def fullList(self) -> list[str]:
        result = []
        for loadType in self.__loadTypes:
            for direction in self.__directions:
                name = f'{self.frame} connection'
                if not self.__isResultant(direction):
                    name += ' ' + self.ref + direction
                name += ' ' + loadType
                tag = self.tag(loadType, direction)
                colTitle1 = self.__loadTypeTitle(loadType)
                colTitle2 = direction
                result.append([name, tag, colTitle1, colTitle2])        
        return result
    

    @property
    def count(self) -> int:
        return len(self.fullList)

    def tableColTitles(self, mainTitle: str | list[str]):
        if type(mainTitle) == str:
            mainTitleList = [mainTitle]
        elif type(mainTitle) == list:
            mainTitleList = mainTitle
        else:
            raise Exception(f'Invalid type for mainTitle ({type(mainTitle)})')    

        titleList = []
        for _, _, c1, c2 in self.fullList:
            newEntry = []
            for mt in mainTitleList: newEntry.append(mt)
            newEntry.extend([c1,c2])
            titleList.append(tuple(newEntry))
        return titleList


def __is_resultant_load(label: str) -> bool:
    """Verifies if the label correspond to the resultant, not one of the components"""
    return label == 'F' or label == 'M'
 
def __getFileList(path: str) -> list[str]:
    return [f for f in os.listdir(path) if f[-4:] == '.sim']

def __copy(fromExtremes: list[list[float]]) -> list:
    newExtremes = []
    for row in fromExtremes:
        newExtremes.append(row.copy())
    return newExtremes

def __saveToFile(
        extremesByObj: dict, 
        completeRstList: dict,
        file: str,
        constraints: list[str],
        units: _Units,
        includeStatics: bool = True
        ):
    print('Saving file...', end=' ', flush=True)
    df1 = __genTableExtremeByObject(extremesByObj, file, constraints, units, includeStatics)
    df2 = __genTableCriticalLCs(constraints, extremesByObj, completeRstList, includeStatics)
    ext = os.path.splitext(file)[-1]

    if ext == '.xlsx' or ext == '.xls': 
        with pd.ExcelWriter(file) as writer:
            df1.to_excel(writer, sheet_name='Extreme loads')
            df2.to_excel(writer, sheet_name='LC list')
    elif ext == '.csv':
        df1.to_csv(file.replace('.csv','_Extreme-Loads.csv'), sheet_name='Extreme loads')
        df2.to_excel(file.replace('.csv','_LC-list.csv'), sheet_name='LC list')
    else:
        raise Exception(f'Extension "{ext}" not supported.')


    print('done.')

def __genTableExtremeByObject(
        extremesByObj: dict, 
        file: str,
        constraints: list[str],
        units: _Units,
        include_statics: bool = True
        ):
    data = []
    rowTitles = []
    for objName in constraints:
        extremes = extremesByObj[objName]
        for i, row in enumerate(extremes):
            if i < resultDefinitions.count: maxMinTag = 'Max'
            else: maxMinTag = 'Min'            
            loadTag = resultDefinitions.fullList[i % 8][1]
            rowTitles.append((objName, maxMinTag, loadTag))
            data.append(row)        

    indexes = pd.MultiIndex.from_tuples(
        rowTitles, names=['Constraint','Max/Min','Load'])
    columnTitles = [
        ('Load Case (LC)','File','(simulation)'), ('Load Case (LC)','Simulation',f'time [{units.time}]')]
    columnTitles.extend(resultDefinitions.tableColTitles('Total (dynamic)'))
    if include_statics:
        columnTitles.extend(resultDefinitions.tableColTitles('Static'))

    cols = pd.MultiIndex.from_tuples(columnTitles)
    df = pd.DataFrame(data, index=indexes, columns=cols)
    df.to_excel(file) 
    return df

def __genTableCriticalLCs(
        constraintList: list[str], 
        extremesByObj: dict,
        completeRstList: dict[dict], 
        includeStatics: bool = True
        ):
    criticalLCs = CriticalLCs(extremesByObj)
    indexesTitles = []
    columnTitles = []
    data = []

    # create the column titles
    for objName in constraintList:
        columnTitles.extend(resultDefinitions.tableColTitles(['Total (dynamic)', objName]))
    if includeStatics:
        for objName in constraintList:
            columnTitles.extend(resultDefinitions.tableColTitles(['Static', objName]))

    # iterate over the LCs
    for i, LC in enumerate(completeRstList.keys()):
        if criticalLCs.isIncluded(LC):            
            # create the row titles (indexes)
            for time in completeRstList[LC]['Time']:
                if criticalLCs.isIncluded(LC, time):
                    indexesTitles.append((LC, time))
            
            # set data into the required format
            for iTime, time in enumerate(completeRstList[LC]['Time']):
                if criticalLCs.isIncluded(LC, time):

                    newGeneralRow = []
                    # dynamic results
                    for objName in constraintList:
                        newObjRow = []
                        if objName in completeRstList[LC].keys(): 
                            for value in completeRstList[LC][objName]['Dynamic'].values():
                                newObjRow.append(value[iTime])
                            newGeneralRow.extend(newObjRow)    

                    # static results
                    if includeStatics:
                        for objName in constraintList:
                            newObjRow = []
                            if objName in completeRstList[LC].keys(): 
                                for value in completeRstList[LC][objName]['Static'].values():
                                    newObjRow.append(value)
                                newGeneralRow.extend(newObjRow)    
                            else:
                                raise Exception('Missing constraint in particular sim file not implemented yet.')

                    data.append(newGeneralRow)            

    indexes = pd.MultiIndex.from_tuples(indexesTitles, names=['File', 'Sim. time [s]'])
    columns = pd.MultiIndex.from_tuples(columnTitles)
    df = pd.DataFrame(data, index=indexes, columns=columns)
    return df

def __storeGlobalResults(
        constraintName: str, LC: str, 
        sampleTimes: list[float],
        timeHistoryResults: dict[list[float]], 
        staticResults: dict[float]|None,
        complete_result_list: dict
        ):
    
    if not LC in complete_result_list.keys(): 
        complete_result_list[LC] = {}
        complete_result_list[LC]['Time'] = sampleTimes

    if not constraintName in complete_result_list[LC].keys(): 
        complete_result_list[LC][constraintName] = {}        
        complete_result_list[LC][constraintName]['Dynamic'] = {}        
        complete_result_list[LC][constraintName]['Static'] = {}        

    for tag, value in timeHistoryResults.items():
        complete_result_list[LC][constraintName]['Dynamic'][tag] = value
        if staticResults != None:
            complete_result_list[LC][constraintName]['Static'][tag] = staticResults[tag]

def __getConstraintList(model: ofx.Model, constraints: list[str]) -> list[str]:
    for obj in model.objects:
        if obj.type == ofx.ObjectType.Constraint:
            constraints.append(obj.name)
    if len(constraints) == 0:
        raise Exception('None constraint object was found in the model.')
            
def __procFiles(
        files: list[str], 
        simFilesFolder: str, 
        constraints: list[str],
        latestWave: bool = True,
        includeStatics: bool = True,
        invert_signs: bool = False
        ):
    extremesByObj = {}
    completeResultList = {}

    n = len(files)
    for i, f in enumerate(files):
        print(f'Processing file ({i+1}/{n}): "{f}" ...', end=' ', flush=True)
        LC = f # the Load Case title is assumed to be the file name

        path = os.path.join(simFilesFolder, f)
        model = ofx.Model(path)
        if len(constraints) == 0 and i == 0:
            __getConstraintList(model, constraints)

        for objName in constraints:
            constraint = model[objName]            
            newExtremeResults, thResults, sampleTimes, staticRsts = __getConstraintExtremes(
                constraint, LC, latestWave, includeStatics, invert_signs)

            # stores the extreme results for the evaluated constraint
            if i == 0: 
                extremesByObj[objName] = __copy(newExtremeResults)
            else:
                __compareExtremeLCs(
                    extremesByObj[objName], newExtremeResults)

            # stores in the complete result list
            __storeGlobalResults(
                objName, LC, sampleTimes, thResults, staticRsts, completeResultList)

        print('done.')

    return extremesByObj, completeResultList

def __compareExtremeLCs(extremesA: list[list[float]], extremesB: list[list[float]]):
    for maxMinOffset in [0,resultDefinitions.count]:
        # compare only the first block of results , which corresponds to the total (dynamic) extremes
        for i in range(resultDefinitions.count): 
            row = i + maxMinOffset            
            if (maxMinOffset == 0 and extremesA[row][i+2] < extremesB[row][i+2]) \
                or (maxMinOffset == resultDefinitions.count and extremesA[row][i+2] > extremesB[row][i+2]):
                # copy all values, including the second block, which corresponds to the static values
                for j in range(len(extremesB[row])): 
                    extremesA[row][j] = extremesB[row][j]

def __getPeriod(latestWave: bool=True) -> ofx.PeriodArg:
    if latestWave: pn = ofx.pnLatestWave
    else: pn = ofx.pnWholeSimulation
    return pn

def __getTimeHistories(
        obj: ofx.OrcaFlexObject, 
        latestWave: bool = True,
        invert_signs: bool = False
        ):    
    pn = __getPeriod(latestWave)
    th_results = {}
    for varName, tag, _, _ in resultDefinitions.fullList: 
        th = obj.TimeHistory(varName, pn)
        if invert_signs: 
            if not __is_resultant_load(tag): 
                th = -1 * th
        th_results[tag] = th
    return th_results

def __getStaticResults(        
        obj: ofx.OrcaFlexObject,
        invert_signs: bool = False
        ):
    results = {}
    for varName, tag, _, _ in resultDefinitions.fullList:
        r = obj.StaticResult(varName)
        if invert_signs:
            # invert only the components (x, y, z); not the resultant
            if not __is_resultant_load(tag): 
                r *= -1
        results[tag] = r
    return results


def __getExtremeValuesFromTH(
        sampleTimes: np.ndarray,
        th_results: dict, 
        LC: str
        ):
    extremeResults = []
    for iExtreme in [np.argmax, np.argmin]:
        for tag1 in resultDefinitions.tags: 
            rstList: list[float] = th_results[tag1]
            i = iExtreme(rstList)
            time = sampleTimes[i]
            rstNewRow = [LC,time]
            for tag2 in resultDefinitions.tags: 
                rstNewRow.append(th_results[tag2][i])
            extremeResults.append(rstNewRow)
      
    return extremeResults

def __getConstraintExtremes(
        obj: ofx.OrcaFlexObject, 
        LC: str,
        latestWave: bool = True,
        includeStatics: bool = True,
        invert_signs: bool = False
        ):
    th_results = __getTimeHistories(obj, latestWave, invert_signs)
    pn = __getPeriod(latestWave)
    sampleTimes = obj.SampleTimes(pn)
    extremeResults = __getExtremeValuesFromTH(sampleTimes, th_results, LC)

    if includeStatics:
        staticResults = __getStaticResults(obj, invert_signs)
        for extreme in extremeResults:
            extreme.extend(staticResults.values())
    else:
        staticResults = None

    return extremeResults, th_results, sampleTimes, staticResults




def ExtremeLoadsFromConstraints(
        sim_files_folder: str, 
        out_file: str, 
        constraints: None|list[str] = None, 
        latest_wave: bool=True,
        in_frame: bool=True, 
        local: bool=True,
        include_statics: bool = True,
        invert_signs: bool = False
        ):
    """
    Extract Constraint extreme (max. and min.) loads (force and moment) from OrcaFLex simulation files
    * sim_files_folder: path to the .sim files
    * out_file: file to write the results (.xlsx or .csv)
    * constraints: list of constraint object names (OrcaFlex) to gather the result from; 
    if `None`, results will be extracted for all constraint in the first .sim file
    * latest_wave: if only the latest wave should be considered (period)
    * in_frame: if true, the results will be obtained for the in-frame reference; 
    otherwise, the out-frame will be considered
    * local: if true, the results will be obtained for the local (constraint) reference; 
    otherwise, the global will be considered
    * include_statics: if statics results should be included in the list to be generated
    * invert_signs: the in-frame load results refer to the force and moment applied by 
    the objects to which the constraint is connected, while the out-frame are the loads 
    applied by the in-frame to the out-frame; set this input as `False` if the 
    opposite is required, i.e. load applied to the object to which the constraint is 
    connected (`in_frame=True`) or by the out-frame to the out-frame (`in_frame=False`)

    Obs.: Assumes all .sim files have the same Constraint objects and unit definitions 
    """
    files = __getFileList(sim_files_folder)

    units = _Units(os.path.join(sim_files_folder,files[0]))

    global resultDefinitions
    resultDefinitions = ResultDefinitions(units, in_frame, local)

    if constraints == None: constraints = []

    extremeByObj, completeRstList = __procFiles(
        files, sim_files_folder, constraints, latest_wave, 
        include_statics, invert_signs)
    
    __saveToFile(extremeByObj, completeRstList, out_file, constraints, units, include_statics)