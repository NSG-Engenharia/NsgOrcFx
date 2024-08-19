# === INPUTS === #
FigSize = [17, 24] # (cm) Figure size
SavePlots = True
ShowPlots = False
FigRes = 300 # Figure resolution in dpi
FigFormat = 'png' # file format to save the figures ('png', 'svg', 'pdf' or 'eps')
HorizGap = 0.3 # Horizontal space between plots in the same page (fraction of the avarege axis width)
OutputFolder = r'tests\tmptestfiles'

# === LIBS === #
#from traceback import format_list
import OrcFxAPI as orc
from OrcFxAPI import Model as ModelClass
from matplotlib import pyplot as plt
import matplotlib as mpl
import numpy as np
from tkinter import filedialog as fd
import os

# === GLOBAL VARIABLES === #
# list of RAOs for each wave heading
PeriodOrFreq = []
SurgeAmp, SwayAmp, HeaveAmp, RollAmp, PitchAmp, YawAmp = [],[],[],[],[],[]
SurgePhase, SwayPhase, HeavePhase, RollPhase, PitchPhase, YawPhase = [],[],[],[],[],[]
HeadingList = []

# === CONSTANTS === #
DOFsList = ['Surge', 'Sway', 'Heave', 'Roll', 'Pitch', 'Yaw']
ParamList = ['Amp', 'Phase']
FigSizeInInches = [1/2.54*FigSize[0], 1/2.54*FigSize[1]] # conversion to inches
LineFormatList = ['--b','-.g','--r',':r',':y','--y','--g',':b','--m',':m'] # list of colores to be used for each wave heading
LineWidthList = [1, 1, 1, 2, 2, 1, 1, 2, 1, 2] # list of line width to be used for each wave heading
FileTypes = [('OrcaFlex file','*.dat *.sim')]


# === PROCEDURES === #
# def SelectInFileDlg():
#     '''
#     Open a dialog to select the input PDF files
#     '''
#     global ModelFile
#     ModelFile = fd.askopenfilename(
#         title='Select OrcaFlex model with RAOs to plot',
#         filetypes=FileTypes
#     )
#     return ModelFile

# def SelectOutFolderDlg():
#     '''
#     Open a dialog to select the output folder
#     '''
#     global OutputFolder
#     OutputFolder = fd.askdirectory(
#         title='Choose the destination folder to save the figure files',
#         mustexist=True)
#     return OutputFolder


def GetConventions(vesseltype: orc.OrcaFlexObject):
    '''
    Get the conventions (e.g. units) in the vessel type
    '''
    global AngleUnity, WaveRefQty
    __AngleUnity__ = vesseltype.RAOResponseUnits
    AngleUnity = '('+__AngleUnity__[:3]+'/m)'
    __WaveRefQty__ = vesseltype.WavesReferredToBy 
    WaveRefQty = __WaveRefQty__[:1].upper()+__WaveRefQty__[1:]

def GetVesselTypeObjs(model: ModelClass):
    '''
    Generate the list of vessel objects in the model
    '''
    result = []
    for obj in model.objects:
        if obj.type == orc.otVesselType:
            result.append(obj)
    return result.copy()

def ResetGlobalVariables():
    for list in [SurgeAmp, SwayAmp, HeaveAmp, RollAmp, PitchAmp, YawAmp, \
         SurgePhase, SwayPhase, HeavePhase, RollPhase, PitchPhase, YawPhase, \
         PeriodOrFreq, HeadingList]:
        list.clear()

def GetValuesFromRAOtable(vesseltype: orc.OrcaFlexObject):
    '''
    Get the values from RAO table of OrcaFlex for the selected heading
    '''
    HeadingList.append(vesseltype.RAODirection)
    PeriodOrFreq.append(np.array(vesseltype.RAOPeriodOrFrequency))
    for DOF in DOFsList:
        for param in ParamList:
            tovar = globals()[DOF+param]
            exec(f'tv.append(np.array(vt.RAO{DOF}{param}))',{'vt':vesseltype, 'tv':tovar, 'np':np})
            print(tovar)

def GetRAOData(vesseltype: orc.OrcaFlexObject):
    '''
    Get RAO data from the model
    '''
    print(f'\nGetting data from vessel type \'{vesseltype.name}\'')
    GetConventions(vesseltype)
    vesseltype.SelectedRAOs = 'Displacement'
    ndraughts = vesseltype.NumberOfDraughts
    for draugthname in vesseltype.DraughtName:
        ResetGlobalVariables()
        vesseltype.SelectedDraught = draugthname
        ndir = vesseltype.NumberOfRAODirections
        for idir in range(ndir):
            vesseltype.SelectedRAODirectionIndex = idir
            GetValuesFromRAOtable(vesseltype)
        GenPlotGraphs(vesseltype)

def GetMaxT():
    '''
    Get the maximum period in all lists
    '''
    maxT = 0
    for list in PeriodOrFreq:
        maxT = max(maxT,max(list))
    return maxT

def GenPlotGraphs(vt: orc.OrcaFlexObject):
    '''
    Generate the Amp and Phase RAO plots for the specified vessel type and the selected draught
    '''
    for param in ParamList:
        GenPlotRAOs(vt, param)

def SaveFig(filename: str):
    '''
    Save the figure with the formats defined in 'FigFormats'
    '''
    path = fr'{OutputFolder}\\{filename}.{FigFormat}'
    print(f'Saving file {os.path.basename(path)} ...', end=' ')
    try: plt.savefig(path)
    except: print('Erro')
    else:   print('Done')

def GenPlotRAOs(vt: orc.OrcaFlexObject, param: str):
    '''
    Generate RAO plots for the specified param (Amp or Phase)
    '''
    if param != 'Phase': 
        paramTitle = 'Amplitude'
        colUnity = ['(m/m)', AngleUnity]
    else:                
        paramTitle = param
        colUnity = ['(deg)', '(deg)']
    fig, axs = plt.subplots(3, 2, figsize=FigSizeInInches, dpi=FigRes, layout='tight')    
    fig.subplots_adjust(wspace=HorizGap)
    for i, DOF in enumerate(DOFsList):
        yValues = globals()[DOF+param]
        row = i % 3
        col = i // 3
        ax = axs[row,col]
        mpl.rcParams['axes.titlesize'] = 'medium'
        #mpl.rcParams['ytick.labelsize'] = 'small'
        ax.tick_params(labelsize='small')
        maxT = GetMaxT()
        for j, (Heading, T, A) in enumerate(zip(HeadingList, PeriodOrFreq, yValues)):
            iStyle = j % len(LineFormatList)
            fmt = LineFormatList[iStyle]
            lw = LineWidthList[iStyle]
            ax.plot(T, A, fmt, label=str(Heading), linewidth=lw)
            ax.set_title(DOF) 
        if row == 2: 
            ax.set_xlabel(WaveRefQty)
            if col == 0: ax.legend()                
        else:        ax.set_xticklabels([])
        ax.set_ylabel(colUnity[col])
        ax.set_ylim([0,None])
        ax.set_xlim([0,maxT])
        ax.grid()

    if vt.NumberOfDraughts == 1: figtitle = f'{vt.name}\n{paramTitle}'
    else:                        figtitle = f'{vt.name} - {vt.SelectedDraught}\n{paramTitle}'
    fig.suptitle(figtitle)
    if SavePlots: SaveFig(f'{vt.name}_{paramTitle}')
    if ShowPlots: plt.show()    

# === MAIN === #
# if SelectInFileDlg():
#     if SelectOutFolderDlg():
#         model = orc.Model(ModelFile)
#         VesselTypeList = GetVesselTypeObjs(model)
#         for vt in VesselTypeList:
#             GetRAOData(vt)




