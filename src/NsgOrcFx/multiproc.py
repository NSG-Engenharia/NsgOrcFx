"""
#  Run .sim files in multiprocessing
"""

import os
from dataclasses import dataclass
from multiprocessing import Process
import OrcFxAPI as orc

@dataclass
class ProcessResult:
    nAssignedLCs: int = 0
    nErrorLCs: int = 0
    ErrorLcList: list = None

@dataclass
class MultiProcConfig:
    fileList: list[str]
    procResults: ProcessResult
    nProcs: int
    pathModelFiles: str
    outputFolder: str
    delSuccessRunLCs: bool
    groupList: list|None = None

    @property
    def nFiles(self) -> int:
        return len(self.fileList)


def __getFileList(path: str) -> list[str]:
    return [f for f in os.listdir(path) if f[-4:] == '.dat']

def __distributeLCs(cfg: MultiProcConfig) -> list[list[str]]:
    nLCs = len(cfg.fileList)
    nLCsPerThread = nLCs // cfg.nProcs
    if nLCs % cfg.nProcs != 0:
        nLCsPerThread += 1

    print('\nORCAFLEX MULTIPROCESS SIMULATION')
    print('\n================================')
    print('Number of LCs: ', nLCs)
    print('Number of process: ', cfg.nProcs)
    print('Number LCs per process:', nLCsPerThread)
    print('--------------------------------')
    print('')
    groups = []

    if nLCs > cfg.nProcs:
        for i in range(cfg.nProcs-1):
            newGroup = cfg.fileList[i*nLCsPerThread:(i+1)*nLCsPerThread]
            groups.append(newGroup.copy())
        groups.append(cfg.fileList[(cfg.nProcs-1)*nLCsPerThread:])
    else:
        for file in cfg.fileList:
            groups.append([file])
        for i in range(cfg.nFiles-1, cfg.nProcs):
            groups.append([])

    return groups


def __runMultiThreading(cfg: MultiProcConfig):
    procs: list[Process] = []

    for i in range(cfg.nProcs):        
        group = cfg.groupList[i]
        if len(group) > 0:
            newProc = Process(target=__runLCs, args=(i, group, cfg))
            procs.append(newProc)

    for p in procs:
        p.start()

    for p in procs:
        p.join()
        if p.is_alive():
            p.terminate()

    __printSummary(cfg.procResults)
        
def __runAllLCs(cfg: MultiProcConfig):
    if cfg.nProcs == 1:
        __runLCs(-1, cfg.fileList, cfg)
    else:
        cfg.groupList = __distributeLCs(cfg)
        __runMultiThreading(cfg)
 
def __runLCs(iProc: int, group: list[str], cfg: MultiProcConfig):
    cfg.procResults[iProc].nAssignedLCs = len(group)
    cfg.procResults[iProc].nErrorLCs = len(group)

    for i, file in enumerate(group):
        __runLoadCase(iProc, i, len(group), file, cfg)

def __tTag(iProc: int, nProcs: int):
    return f'Proc {iProc+1}/{nProcs}'

def __runLoadCase(iProc: int, iFile: int, nProcFiles: int, file: str, cfg: MultiProcConfig):
    fullPath = os.path.join(cfg.pathModelFiles, file)
    model = orc.Model(fullPath, threadCount=cfg.nProcs)
    print(f'{__tTag(iProc, cfg.nProcs)}: running "{file}" ({iFile+1}/{nProcFiles}) ...', flush=True)
    try:
        model.RunSimulation()
        percent = float(iFile+1)/nProcFiles*100
        print(f'{__tTag(iProc, cfg.nProcs)}: simulation of file "{file}" ({iFile+1}/{nProcFiles}) completed ({percent:0.1f}%). Saving results...', flush=True)        
        if model.state == orc.ModelState.SimulationStopped:
            fullSimPath = os.path.join(cfg.pathModelFiles, cfg.outputFolder, file.replace('.dat', '.sim'))
            model.SaveSimulation(fullSimPath)            
            print(f'{__tTag(iProc, cfg.nProcs)}: result file saved.', flush=True)
            if cfg.delSuccessRunLCs:
                os.remove(fullPath)
                cfg.procResults[iProc].nErrorLCs -= 1
        else:
            cfg.procResults[iProc].ErrorLcList.append(file)

    except Exception as error:
        cfg.procResults[iProc].ErrorLcList.append(file)
        print(f'{__tTag(iProc, cfg.nProcs)}: error during simulation', error, flush=True)
    model.Clear()

def __printSummary(procResults: list[ProcessResult]):
    nTotalLCs = 0
    nErrorLCs = 0
    ErrorLCs = []
    for procRst in procResults:
        nTotalLCs += procRst.nAssignedLCs
        nErrorLCs += procRst.nErrorLCs
        ErrorLCs.extend(procRst.ErrorLcList)

    print(f'\nTOTAL NUMBER OF LCs: {nTotalLCs}')
    print(f'NUMBER OF LCs WITH ERROR: {nErrorLCs}')
    print('LIST OF LCs WITH ERROR: ', ErrorLCs)


def ProcMultiThread(
        dat_files_path: str,
        out_path: str,
        n_threads: None|int=None,
        del_success_dat: bool=True
        ):
    # global procResults, nProcs, pathModelFiles, outputFolder, delSuccessRunLCs

    
    if not n_threads:
        nProcs = os.cpu_count()-1
    else:
        nProcs = n_threads
    nProcs = max(1,nProcs)


    procResults: list[ProcessResult] = []
    for _ in range(nProcs):
        procResults.append(ProcessResult())
        procResults[-1].ErrorLcList = []

    fileList = __getFileList(dat_files_path)

    config = MultiProcConfig(
        fileList, procResults, nProcs, dat_files_path, out_path, del_success_dat)


    model = orc.Model()
    
    __runAllLCs(config)