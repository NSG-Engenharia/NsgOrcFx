# NsgOrcFx
Library of tools for the OrcaFlex API

This package wraps the original API from Orcina (OrcFxAPI) to include:
* methods: pre- and post-processing tools such as line selection, load case generation, modal and fatigue analysis
* coding facilities: auto-complete and hints with descriptions in IDE

\
All the attributes and methods from the source (OrcFxAPI) still accessible in the same way.

\
Installation:
```
pip install --upgrade NsgOrcFx
```

## Example 1 - Auto-complete feature of IDE (e.g. VS Code and Spyder)
```
import NsgOrcFx

model = NsgOrcFx.Model()
line = model.CreateLine()

```
The data name may be found in the `data` attribute with the auto complete of the IDE (e.g., Visual Studio Code, Spyder, and PyCharm).
![Screenshot of auto-complete with the 'data' component of objects (e.g., line.data.{data name})](https://github.com/NSG-Engenharia/NsgOrcFx/blob/main/documentation/images/autocomplete_linedata.png?raw=True)

In addition, a hint shows the description of the parameter (mouse cursor stopped in the data name).
![Screenshot of hint with the 'data' component of objects (e.g., line.data.{data name})](https://github.com/NSG-Engenharia/NsgOrcFx/blob/main/documentation/images/hint_linedata.png?raw=True)


In the exemple below, data names of `general`, `environment`, and `line` objects are accessed 
```
model.general.data.ImplicitConstantTimeStep = 0.01 # data from general object
model.environment.data.WaveHeight = 5.0 # data from environment object
line.data.EndAConnection = 'Anchored' # data form the line object
```

The line could be alse located by name with the following method. Although it could be done with the original method (`line = model['Line1']`), the new method is recommended to allow the functionality of auto-complete (`data` attribute)
```
line = model.findLineByName('Line1')
```

A list of all lines in the model may be retrieved and then select the first one by
```
lines = model.getAllLines()
line1 = lines[0]
```

## Example 2 - Reduced simulation time for irregular wave
```
import NsgOrcFx as ofx

model = ofx.Model()

# set irregular wave
model.environment.data.WaveType = 'JONSWAP'
model.environment.data.WaveHs = 2.5
model.environment.data.WaveGamma = 2
model.environment.data.WaveTp = 8

# set reduced simulation duration with 200 seconds
model.SetReducedSimulationDuration(200)

# save data file to check the wave history
model.Save('reduced.dat')

# after executing this code, open the generated data file
# then open Environment -> Waves preview, and set duration of 200s 
# click in View profile and observe that the largest event (rise or fall)
# is in the midle of the sea elevation history

```
![Screenshot of Wave preview (Environment -> Waves preview -> View profile) for a simulation of irregular wave with reduced duration based on the largest rise/fall occurence](https://github.com/NSG-Engenharia/NsgOrcFx/blob/main/documentation/images/wave_preview.png?raw=True)


## Example 3 - Generate load cases
```
import NsgOrcFx

model = NsgOrcFx.Model()
model.CreateLine()

# list of wave direction, height, and periods to define the Load Cases (LCs)
directions = [0, 45, 90] 
heights = [1.5, 2.0, 3.0]
periods = [5, 7, 9]

# Folder to save the generated files (LCs)
outFolder = 'tmp'

# Regular waves
model.GenerateLoadCases('Dean stream', directions, heights, periods, outFolder)

```

\
In case of irregular wave:
```
model.GenerateLoadCases('JONSWAP', directions, heights, periods, outFolder)
```
\
To run irregular waves with reduced simulation time, based on the occurance of the largest rise or fall in the specified storm period.
```
model.GenerateLoadCases('JONSWAP', directions, heights, periods, outFolder, reducedIrregDuration=200)
```


## Example 4 - Calculating modal analysis and getting the normalized modal shape 
```
import NsgOrcFx

model = NsgOrcFx.Model()
model.CreateLine()

modes = model.CalculateModal()

# mode shape index (0 for the 1st)
modeIndex = 0

# mode frequency
freq = modes.getModeFrequency(modeIndex)

# if normalize = True, the displacements will be normalized, so the maximum total displacements is equal to the line diameter
[arcLengths, Ux, Uy, Uz] = modes.GlobalDispShape('Line1', modeIndex, True)
print('Frequency = ', freq, 'Hz')
print(arcLengths, Ux, Uy, Uz)
```


## Example 5 - Defining fatigue analysis and getting the fatigue life calculated
```
import NsgOrcFx

simFile = r'tests\tmp\fatigue.sim'
ftgFile = r'tests\tmp\fatigue.ftg'

# First, it is necessary a model with simulation complete
model = NsgOrcFx.Model()
model.CreateLine()
model.RunSimulation()
model.Save(simFile) 

# The fatigue analysis is defined, including the S-N curve based on the DNV-RP-C203
analysis = NsgOrcFx.FatigueAnalysis()
analysis.data.AnalysisType = 'Rainflow'
analysis.data.LoadCaseCount = 1
analysis.addLoadCase(simFile)
analysis.addSNCurveByNameAndEnv('F3','seawater')
analysis.addAnalysisData()
analysis.Calculate()
analysis.Save(ftgFile)

# Result of fatigue life in each node
lifePerNode = analysis.getLifeList()
print(lifePerNode)
```


## Example 6 - Generates RAO plots from vessel type data
```
import NsgOrcFx as ofx

model = ofx.Model()

# Create a 'Vessel Type' object with default data
model.CreateObject(ofx.ObjectType.VesselType)

# Create RAO plots (amplitude and phase) and save to the defined folder
model.SaveRAOplots(r'tests\tmptestfiles')
```
![ plot generated with SaveRAOplots() method](https://github.com/NSG-Engenharia/NsgOrcFx/blob/main/documentation/images/Vessel_type1_Amplitude.png?raw=True)


