
# === LIBS === #
#from traceback import format_list
import OrcFxAPI as ofx
from OrcFxAPI import Model as ModelClass
from matplotlib import pyplot as plt
import matplotlib as mpl
import numpy as np
from tkinter import filedialog as fd
import os

# === CONSTANTS === #
DOFsList = ['Surge', 'Sway', 'Heave', 'Roll', 'Pitch', 'Yaw']
ParamList = ['Amp', 'Phase']
LineFormatList = ['--b','-.g','--r',':r',':y','--y','--g',':b','--m',':m'] # list of colores to be used for each wave heading
LineWidthList = [1, 1, 1, 2, 2, 1, 1, 2, 1, 2] # list of line width to be used for each wave heading
FileTypes = [('OrcaFlex file','*.dat *.sim')]

class RaoPlot():
    def __init__(self) -> None:
        # === INPUTS === #
        self.FigSize = [17, 24] # (cm) Figure size
        self.SavePlots = True
        self.ShowPlots = False
        self.FigRes = 300 # Figure resolution in dpi
        self.FigFormat = 'png' # file format to save the figures ('png', 'svg', 'pdf' or 'eps')
        self.HorizGap = 0.3 # Horizontal space between plots in the same page (fraction of the avarege axis width)
        self.raoOutputFolder = r'tests\tmptestfiles'


        # === GLOBAL VARIABLES === #
        # list of RAOs for each wave heading
        self.PeriodOrFreq = []
        self.SurgeAmp, self.SwayAmp, self.HeaveAmp, self.RollAmp, self.PitchAmp, self.YawAmp = [],[],[],[],[],[]
        self.SurgePhase, self.SwayPhase, self.HeavePhase, self.RollPhase, self.PitchPhase, self.YawPhase = [],[],[],[],[],[]
        self.HeadingList = []

        self.FigSizeInInches = [1/2.54*self.FigSize[0], 1/2.54*self.FigSize[1]] # conversion to inches


    def GetConventions(self, vesseltype: ofx.OrcaFlexObject):
        '''
        Get the conventions (e.g. units) in the vessel type
        '''
        # global AngleUnity, WaveRefQty
        __AngleUnity__ = vesseltype.RAOResponseUnits
        self.AngleUnity = '('+__AngleUnity__[:3]+'/m)'
        __WaveRefQty__ = vesseltype.WavesReferredToBy 
        self.WaveRefQty = __WaveRefQty__[:1].upper()+__WaveRefQty__[1:]

    def GetVesselTypeObjs(self, model: ModelClass):
        '''
        Generate the list of vessel objects in the model
        '''
        result = []
        for obj in model.objects:
            if obj.type == ofx.otVesselType:
                result.append(obj)
        return result.copy()

    def ResetGlobalVariables(self):
        for list in [self.SurgeAmp, self.SwayAmp, self.HeaveAmp, self.RollAmp, self.PitchAmp, self.YawAmp, \
            self.SurgePhase, self.SwayPhase, self.HeavePhase, self.RollPhase, self.PitchPhase, self.YawPhase, \
            self.PeriodOrFreq, self.HeadingList]:
            list.clear()

    def GetValuesFromRAOtable(self, vesseltype: ofx.OrcaFlexObject):
        '''
        Get the values from RAO table of OrcaFlex for the selected heading
        '''
        self.HeadingList.append(vesseltype.RAODirection)
        self.PeriodOrFreq.append(np.array(vesseltype.RAOPeriodOrFrequency))
        for DOF in DOFsList:
            for param in ParamList:
                # tovar = globals()[DOF+param]
                tovar: list[np.ndarray] = self.__getattribute__(DOF+param)
                # exec(f'tv.append(np.array(vt.RAO{DOF}{param}))',{'vt':vesseltype, 'tv':tovar, 'np':np})
                valueList = vesseltype.__getattr__(f'RAO{DOF}{param}')
                tovar.append(np.array(valueList))
                # print(valueList)

    def GetRAOData(self, vesseltype: ofx.OrcaFlexObject):
        '''
        Get RAO data from the model
        '''
        print(f'\nGetting data from vessel type \'{vesseltype.name}\'')
        self.GetConventions(vesseltype)
        vesseltype.SelectedRAOs = 'Displacement'
        # ndraughts = vesseltype.NumberOfDraughts
        for draugthname in vesseltype.DraughtName:
            self.ResetGlobalVariables()
            vesseltype.SelectedDraught = draugthname
            ndir = vesseltype.NumberOfRAODirections
            for idir in range(ndir):
                vesseltype.SelectedRAODirectionIndex = idir
                self.GetValuesFromRAOtable(vesseltype)
            self.GenPlotGraphs(vesseltype)

    def GetMaxT(self):
        '''
        Get the maximum period in all lists
        '''
        maxT = 0
        for list in self.PeriodOrFreq:
            for v in list:
                if v != ofx.OrcinaInfinity():
                    maxT = max(maxT, v)
        return maxT

    def GenPlotGraphs(self, vt: ofx.OrcaFlexObject):
        '''
        Generate the Amp and Phase RAO plots for the specified vessel type and the selected draught
        '''
        for param in ParamList:
            self.GenPlotRAOs(vt, param)

    def SaveFig(self, filename: str):
        '''
        Save the figure with the formats defined in 'FigFormats'
        '''
        path = fr'{self.raoOutputFolder}\\{filename}.{self.FigFormat}'
        print(f'Saving file {os.path.basename(path)} ...', end=' ')
        try: plt.savefig(path)
        except: print('Erro')
        else:   print('Done')

    def GenPlotRAOs(self, vt: ofx.OrcaFlexObject, param: str):
        '''
        Generate RAO plots for the specified param (Amp or Phase)
        '''
        if param != 'Phase': 
            paramTitle = 'Amplitude'
            colUnity = ['(m/m)', self.AngleUnity]
        else:                
            paramTitle = param
            colUnity = ['(deg)', '(deg)']
        fig, axs = plt.subplots(3, 2, figsize=self.FigSizeInInches, dpi=self.FigRes, layout='tight')    
        fig.subplots_adjust(wspace=self.HorizGap)
        for i, DOF in enumerate(DOFsList):
            # yValues = globals()[DOF+param]
            yValues = self.__getattribute__(DOF+param)
            row = i % 3
            col = i // 3
            ax = axs[row,col]
            mpl.rcParams['axes.titlesize'] = 'medium'
            #mpl.rcParams['ytick.labelsize'] = 'small'
            ax.tick_params(labelsize='small')
            maxT = self.GetMaxT()
            for j, (Heading, T, A) in enumerate(zip(self.HeadingList, self.PeriodOrFreq, yValues)):
                iStyle = j % len(LineFormatList)
                fmt = LineFormatList[iStyle]
                lw = LineWidthList[iStyle]
                if T[-1] == ofx.OrcinaInfinity(): 
                    _T = T[:-1]
                    _A = A[:-1]
                else:
                    _T = T
                    _A = A
                # print(T)
                ax.plot(_T, _A, fmt, label=str(Heading), linewidth=lw)
                # print(T, A)
                ax.set_title(DOF) 
            if row == 2: 
                ax.set_xlabel(self.WaveRefQty)
                if col == 0: ax.legend()                
            else:        ax.set_xticklabels([])
            ax.set_ylabel(colUnity[col])
            ax.set_ylim([0,None])
            ax.set_xlim([0,maxT])
            ax.grid()

        if vt.NumberOfDraughts == 1: figtitle = f'{vt.name}\n{paramTitle}'
        else:                        figtitle = f'{vt.name} - {vt.SelectedDraught}\n{paramTitle}'
        fig.suptitle(figtitle)
        if self.SavePlots: self.SaveFig(f'{vt.name}_{paramTitle}')
        if self.ShowPlots: plt.show()    

    # === MAIN === #
    # if SelectInFileDlg():
    #     if SelectOutFolderDlg():
    #         model = ofx.Model(ModelFile)
    #         VesselTypeList = GetVesselTypeObjs(model)
    #         for vt in VesselTypeList:
    #             GetRAOData(vt)




