import NsgOrcFx
# import NsgOrcFx_nsgeng as NsgOrcFx
# import src.NsgOrcFx_nsgeng as NsgOrcFx

model = NsgOrcFx.Model()
# model.CreateObject(NsgOrcFx.ObjectType.Line)
# lines = model.getAllLines()
# line = lines[0]
line = model.CreateLine()

line.params.EndAGamma

print(line.params.EndAConnection)
line.params.EndAConnection = 'Anchored'
print(line.params.EndAConnection)

# model = NsgOrcFx.Model(r'.\tests\stiffeners.dat')
# lines = model.getAllLines()

# for line in lines:
#     print(line.params.Name)

