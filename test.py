# import NsgOrcFx
import src.NsgOrcFx as NsgOrcFx
# import NsgOrcFx_nsgeng as NsgOrcFx
# import src.NsgOrcFx_nsgeng as NsgOrcFx

model = NsgOrcFx.Model()
# model.CreateObject(NsgOrcFx.ObjectType.Line)
# lines = model.getAllLines()
# line = lines[0]
line = model.CreateLine()

print(line.data.EndAConnection)
line.data.EndAConnection = 'Anchored'
print(line.data.EndAConnection)

# model = NsgOrcFx.Model(r'.\tests\stiffeners.dat')
# lines = model.getAllLines()

# for line in lines:
#     print(line.params.Name)

# model.environment.WaveType = 'JONSWAP'
# model.SetReducedSimulationDuration(200)
# model.SaveData(r'tests\tmp\test.dat')
model.GenerateLoadCases('JONSWAP', [0,45,90], [1.5, 2.0], [5,7,9], r'tests\tmp', reducedIrregDuration=100)