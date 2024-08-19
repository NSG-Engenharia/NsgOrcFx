
# Code to get RAO data from OrcaFlex model and generate plots
# Created by Gabriel Nascimento in 22/05/2022
# Last update in 23/05/2022

# === INPUTS === #
FigSize = [17, 24] # (cm) Figure size
SavePlots = True
ShowPlots = False
FigRes = 300 # Figure resolution in dpi
FigFormat = 'png' # file format to save the figures ('png', 'svg', 'pdf' or 'eps')
HorizGap = 0.3 # Horizontal space between plots in the same page (fraction of the avarege axis width)


# === LIBS === #
import OrcFxAPI as ofx
import matplotlib as mpl
import matplotlib.pyplot as plt
import os
import numpy as np



# === CONSTANTS === #
__FigTypes = ['png', 'svg', 'pdf', 'eps']
__DOFsList = ['Surge', 'Sway', 'Heave', 'Roll', 'Pitch', 'Yaw']
__ParamList = ['Amp', 'Phase']
__FigSizeInInches = [1/2.54*FigSize[0], 1/2.54*FigSize[1]] # conversion to inches
__LineFormatList = ['--b','-.g','--r',':r',':y','--y','--g',':b','--m',':m'] # list of colores to be used for each wave heading
__LineWidthList = [1, 1, 1, 2, 2, 1, 1, 2, 1, 2] # list of line width to be used for each wave heading
# __FileTypes = [('OrcaFlex file','*.dat *.sim')]

# === GLOBAL VARIABLES === #
# list of RAOs for each wave heading
__PeriodOrFreq = []
__SurgeAmp, __SwayAmp, __HeaveAmp, __RollAmp, __PitchAmp, __YawAmp = [],[],[],[],[],[]
__SurgePhase, __SwayPhase, __HeavePhase, __RollPhase, __PitchPhase, __YawPhase = [],[],[],[],[],[]
__HeadingList = []

# === METHODS === #
def __GetConventions(vesseltype: ofx.OrcaFlexObject):
    '''
    Get the conventions (e.g. units) in the vessel type
    '''
    global AngleUnity, WaveRefQty
    __AngleUnity__ = vesseltype.RAOResponseUnits
    AngleUnity = '('+__AngleUnity__[:3]+'/m)'
    __WaveRefQty__ = vesseltype.WavesReferredToBy 
    WaveRefQty = __WaveRefQty__[:1].upper()+__WaveRefQty__[1:]

def __GetVesselTypeObjs(model: ofx.Model):
    '''
    Generate the list of vessel objects in the model
    '''
    result = []
    for obj in model.objects:
        if obj.type == ofx.otVesselType:
            result.append(obj)
    return result.copy()

def __ResetGlobalVariables():
    for list in [__SurgeAmp, __SwayAmp, __HeaveAmp, __RollAmp, __PitchAmp, __YawAmp, \
         __SurgePhase, __SwayPhase, __HeavePhase, __RollPhase, __PitchPhase, __YawPhase, \
         __PeriodOrFreq, __HeadingList]:
        list.clear()

def __GetValuesFromRAOtable(vesseltype: ofx.OrcaFlexObject):
    '''
    Get the values from RAO table of OrcaFlex for the selected heading
    '''
    __HeadingList.append(vesseltype.RAODirection)
    __PeriodOrFreq.append(np.array(vesseltype.RAOPeriodOrFrequency))
    for DOF in __DOFsList:
        for param in __ParamList:
            tovar = globals()['__'+DOF+param]
            exec(f'tv.append(np.array(vt.RAO{DOF}{param}))',{'vt':vesseltype, 'tv':tovar, 'np':np})

# def GenRAOplotsForAllDraughts(
#         model: ofx.Model, 
#         folder: str, 
#         figtype: str = 'png', 
#         vesseltype: ofx.OrcaFlexObject = None        
#         ):
#     '''
#     Get RAO data from the model
#     '''

#     print(f'\nGetting data from vessel type \'{vesseltype.name}\'')
#     __GetConventions(vesseltype)
#     vesseltype.SelectedRAOs = 'Displacement'
#     # ndraughts = vesseltype.NumberOfDraughts

#     for draugthname in vesseltype.DraughtName:
#         __ResetGlobalVariables()
#         vesseltype.SelectedDraught = draugthname
#         ndir = vesseltype.NumberOfRAODirections
#         for idir in range(ndir):
#             vesseltype.SelectedRAODirectionIndex = idir
#             __GetValuesFromRAOtable(vesseltype)
#         __GenPlotGraphs(vesseltype)

def __GetMaxT():
    '''
    Get the maximum period in all lists
    '''
    maxT = 0
    for list in __PeriodOrFreq:
        maxT = max(maxT,max(list))
    return maxT

def GenRAOplots(
        model: ofx.Model, 
        folder: str, 
        figtype: str = 'png', 
        vesseltype: ofx.OrcaFlexObject = None
        ):
    '''
    Generate the Amp and Phase RAO plots
    * folder: where to save the plot files
    * figtype: extension of the figure files ('png', 'svg', 'pdf' or 'eps')
    * vesseltype: vessel type object containing the RAO to be plotted. All, if 'None'.
    '''
    __checkFigType(figtype)

    if vesseltype != None: vesseltypes = [vesseltype]
    else: vesseltypes = __GetVesselTypeObjs(model)

    for vt in vesseltypes:
        __GetConventions(vt)
        vt.SelectedRAOs = 'Displacement'

        for draugthname in vt.DraughtName:
            __ResetGlobalVariables()
            vt.SelectedDraught = draugthname
            ndir = vt.NumberOfRAODirections
            for idir in range(ndir):
                vt.SelectedRAODirectionIndex = idir
                __GetValuesFromRAOtable(vt)

            for param in __ParamList:
                __GenPlotRAOs(folder, figtype, vt, param)

def __SaveFig(basePath: str, basename: str, figtype: str):
    '''
    Save the figure with the formats defined in 'FigFormats'
    '''
    # path = fr'{OutputFolder}\\{filename}.{FigFormat}'
    filename = f'{basename}.{figtype}'
    path = os.path.join(basePath, filename)
    
    # print(f'Saving file {os.path.basename(path)} ...', end=' ')
    try: plt.savefig(path)
    except: print(f'Erro when save the file {path}')
    # else:   print('Done')

def __checkFigType(figtype: str) -> None:
    if not figtype in __FigTypes:
        raise Exception(f'Figure extension {figtype} not supported.')

def __GenPlotRAOs(
        folder: str, 
        figtype: str,
        vt: ofx.OrcaFlexObject, 
        param: str):
    '''
    Generate RAO plots for the specified param (Amp or Phase)
    '''
    if param != 'Phase': 
        paramTitle = 'Amplitude'
        colUnity = ['(m/m)', AngleUnity]
    else:                
        paramTitle = param
        colUnity = ['(deg)', '(deg)']
    fig, axs = plt.subplots(3, 2, figsize=__FigSizeInInches, dpi=FigRes, layout='tight')    
    fig.subplots_adjust(wspace=HorizGap)
    for i, DOF in enumerate(__DOFsList):
        yValues = globals()['__'+DOF+param]
        row = i % 3
        col = i // 3
        ax = axs[row,col]
        mpl.rcParams['axes.titlesize'] = 'medium'
        #mpl.rcParams['ytick.labelsize'] = 'small'
        ax.tick_params(labelsize='small')
        maxT = __GetMaxT()
        for j, (Heading, T, A) in enumerate(zip(__HeadingList, __PeriodOrFreq, yValues)):
            iStyle = j % len(__LineFormatList)
            fmt = __LineFormatList[iStyle]
            lw = __LineWidthList[iStyle]
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
    # if SavePlots: __SaveFig(f'{vt.name}_{paramTitle}')
    if SavePlots: __SaveFig(folder, f'{vt.name}_{paramTitle}', figtype)
    if ShowPlots: plt.show()    