"""
Example of defining fatigue analysis and getting the fatigue life calculated
"""

import NsgOrcFx

simFile = r'tests\tmptestfiles\fatigue.sim'
ftgFile = r'tests\tmptestfiles\fatigue.ftg'

model = NsgOrcFx.Model()
model.CreateLine()
model.RunSimulation()
model.Save(simFile)

analysis = NsgOrcFx.FatigueAnalysis()
analysis.data.AnalysisType = 'Rainflow'
analysis.data.LoadCaseCount = 1
analysis.addLoadCase(simFile)
analysis.addSNCurveByNameAndEnv('F3','seawater')
analysis.addAnalysisData()
analysis.Calculate()
analysis.Save(ftgFile)

lifePerNode = analysis.getLifeList()
print(lifePerNode)