# NsgOrcFx
Library of tools for the OrcaFlex API

This package wraps the original API from Orcina (OrcFxAPI) to include:
* methods: pre- and post-processing tools such as line selection, load case generation, modal and fatigue analysis
* coding facilities: auto-complete and hints with descriptions in IDE
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

# The data name may be found in the `data` attribute with the auto complete of the IDE
# in addition, a hint shows the description of the parameter (mouse cursor stopped in the data name)

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
line = lines[0]
```


## Example 2 - Generate load cases
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


## Example 3 - Calculating modal analysis and getting the normalized modal shape 
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


## Example 4 - Defining fatigue analysis and getting the fatigue life calculated
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


