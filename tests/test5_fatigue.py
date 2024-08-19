"""
Example of defining fatigue analysis and getting the fatigue life calculated
"""

import sys
from os import path
sys.path.append( path.dirname( path.dirname( path.abspath(__file__) ) ) )

from src import NsgOrcFx as ofx

simFile = r'tests\tmptestfiles\fatigue.sim'
ftgFile = r'tests\tmptestfiles\fatigue.ftg'

model = ofx.Model()
model.CreateLine()
model.RunSimulation()
model.Save(simFile)

analysis = ofx.FatigueAnalysis()
analysis.data.AnalysisType = 'Rainflow'
analysis.data.LoadCaseCount = 1
analysis.addLoadCase(simFile)
analysis.addSNCurveByNameAndEnv('F3','seawater')
analysis.addAnalysisData()
analysis.Calculate()
analysis.Save(ftgFile)

lifePerNode = analysis.getLifeList()
print(lifePerNode)