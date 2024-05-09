# import NsgOrcFx
import src.NsgOrcFx as NsgOrcFx
# import NsgOrcFx_nsgeng as NsgOrcFx
# import src.NsgOrcFx_nsgeng as NsgOrcFx

model = NsgOrcFx.Model()
# model.CreateObject(NsgOrcFx.ObjectType.Line)
# lines = model.getAllLines()
# line = lines[0]
line = model.CreateLine()

print(line.params.EndAConnection)
line.params.EndAConnection = 'Anchored'
print(line.params.EndAConnection)

# model = NsgOrcFx.Model(r'.\tests\stiffeners.dat')
# lines = model.getAllLines()

# for line in lines:
#     print(line.params.Name)

model.SetReducedSimulationDuration(200)