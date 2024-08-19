# import NsgOrcFx
# from NsgOrcFx import main
# import src.main as NsgOrcFx
import src.NsgOrcFx.main as NsgOrcFx
# import NsgOrcFx_nsgeng as NsgOrcFx
# import src.NsgOrcFx_nsgeng as NsgOrcFx



model = NsgOrcFx.Model()
vt = model.CreateObject(NsgOrcFx.ObjectType.VesselType)
model.SaveRAOplots(r'tests\tmptestfiles', vt)