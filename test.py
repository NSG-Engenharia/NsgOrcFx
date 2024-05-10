# import NsgOrcFx
# from NsgOrcFx import main
from src import NsgOrcFx as NsgOrcFxTest
# import NsgOrcFx_nsgeng as NsgOrcFx
# import src.NsgOrcFx_nsgeng as NsgOrcFx


model = NsgOrcFxTest.Model()
line = model.CreateLine()
"""
Create line:
  * line = model.CreateLine()
Find by line name:
  * line = model.findLineByName('Line1')
Get the list of all lines
  * lines = model.getAllLines()
  * line = lines[0]
"""

# The data name may be found in the `data` attribute with the auto complete of the IDE
# in addition, a hint shows the description of the parameter (mouse cursor stopped in the data name)


model.general.data.ImplicitConstantTimeStep = 0.01

model.environment.data.WaveHeight = 5.0

print(line.data.EndAConnection)
line.data.EndAConnection = 'Anchored'
print(line.data.EndAConnection)