"""
Generates a report with the total weight of the structures in the model
"""

from dataclasses import dataclass
import math
from typing import TextIO
import OrcFxAPI as orc
from types import FunctionType
from NsgOrcFx.classes import *
from NsgOrcFx.weightaux import *
from NsgOrcFx.objauxfuncs import *

def __getLineObjList(model: orc.Model) -> list[OrcaFlexObject]:
    # lineList: list[OrcaFlexObject] = []
    # for obj in model.objects:
    #     if obj.type == orc.ObjectType.Line:
    #         lineList.append(obj)
    # return lineList
    return getLinesToList(model)

def __getModelFromObj(obj: OrcaFlexObject) -> orc.Model:
    return orc.Model(handle=obj.modelHandle)

@dataclass
class WeightReport:
    dryStructure: float = 0.0
    equips: float = 0.0
    marineGrowth: float = 0.0
    contents: float = 0.0
    addedMassHP: float = 0.0
    addedMassG: float = 0.0

    def total(self) -> float:
        return self.dryStructure + self.equips + self.marineGrowth + \
            self.contents + self.addedMassHP + self.addedMassG

def __calcCoatingLinearMass(
        lt: OrcaFlexObject,
        ) -> float:
    """Calculates the linear mass (ton/m) contribution due to coating (marine growth)"""
    result = 0.0

    if lt.Category == 'Homogeneous pipe':
        thickness: float = lt.CoatingThickness
        if thickness != 0:
            density: float = lt.CoatingMaterialDensity
            OD: float = lt.OD
            area = math.pi/4 * ((OD+2*thickness)**2 - OD**2)
            result = area * density

    return result

def __getLineWeight(line: OrcaFlexLineObject, weight: WeightReport) -> None:
    """Get the line weight"""
    for ltName, length in zip(line.LineType, line.Length):
        model = orc.Model(handle=line.modelHandle)
        lt = model[ltName]
        totalLinDensity = lt.MassPerUnitLength # (ton/m)
        coatingLinDensity = __calcCoatingLinearMass(lt)
        if not totalLinDensity:
            print(f'Warning! It was not possible to add the weight of line type {ltName}')
        else:
            weight.dryStructure += (totalLinDensity-coatingLinDensity) * length # (ton)
            weight.marineGrowth += coatingLinDensity * length

def __getEquipWeight(lines: list[OrcaFlexLineObject], weight: WeightReport) -> None:
    equipWeight = 0
    model = __getModelFromObj(lines[0])
    for line in lines:
        for attachTypeName in line.AttachmentType:
            attach = model[attachTypeName]
            equipWeight += attach.Mass

    weight.equips += equipWeight

def __getContentsWeight(lines: list[OrcaFlexLineObject], weight: WeightReport, msgFunc: FunctionType) -> None:
    model = __getModelFromObj(lines[0])
    contentMass = 0
    for line in lines:
        contentMethod = line.ContentsMethod
        if contentMethod == 'Uniform':
            density = line.ContentsDensity
            if density > 0.0:
                volume = getTotalInnerVolume(line)
                contentMass += density * volume
        elif contentMethod == 'Free flooding':
            density = model.environment.Density
            volume = getSubmergedVolume(line)            
            contentMass += density * volume
        else:
            if msgFunc:
                msgFunc(f'Warning! Contents method {contentMethod} not supported. The contents will be negleted.')            

    weight.contents += contentMass

def __getAddedMass(lines: list[OrcaFlexLineObject], weight: WeightReport) -> None:
    model = __getModelFromObj(lines[0])
    seaDensity = model.environment.Density # (t/m3)
    addedMassHP = 0.0
    addedMassG = 0.0
    for line in lines:
        for iSeg in range(line.NumberOfSections):
            lt = model[line.LineType[iSeg]]
            # OD = lt.OD
            # length = line.Length[iSeg]
            if lt.Category == 'Homogeneous pipe':
                # tCoating = lt.CoatingThickness
                CaHP = lt.Cax
                CaG = 0.0
            else: # "General"
                # tCoating = 0.0
                CaG = lt.Cax
                if lt.Cay != orc.OrcinaDefaultReal():
                    CaG = max(CaG, lt.Cay)
                CaHP = 0.0

            # area = math.pi/4 * (OD+2*tCoating)**2
            volume = getSubmergedVolume(line, False, iSeg)
            addedMassHP += CaHP * seaDensity * volume # (length * area)
            addedMassG += CaG * seaDensity * volume # (length * area)

            # if line.name == 'Bm228':
            #     print(volume)

    weight.addedMassHP += addedMassHP
    weight.addedMassG += addedMassG


def __print(txt: str, file: TextIO = None):
    print(txt)
    if file: file.write(txt)

def __printWeightReport(weight: WeightReport, outFile: str=None) -> None:
    if outFile != None: file = open(outFile, 'w')
    else: file = None
    __print('\n==== WEIGHT REPORT ====', file)
    __print(f'Structural dry: {weight.dryStructure:0.2f} ton', file)
    __print(f'Marine growth: {weight.marineGrowth:0.2f} ton (coating)', file)
    __print(f'Equipments: {weight.equips:0.2f} ton (attachments)', file)
    __print(f'Internal water: {weight.contents:0.2f} ton (contents)', file)
    __print(f'Added masss: {weight.addedMassHP:0.2f} ton ("Homogeneous Pipe")', file)
    __print(f'Added masss: {weight.addedMassG:0.2f} ton ("General Pipe")', file)
    __print(f'TOTAL: {weight.total():0.2f} ton', file)
    __print('', file)


def genWeightReport(model: orc.Model, outFile: str=None, msgFunc: FunctionType=None) -> None:
    weights = WeightReport()
    lineList = __getLineObjList(model)
    for line in lineList:
        __getLineWeight(line, weights)

    __getEquipWeight(lineList, weights)
    __getContentsWeight(lineList, weights, msgFunc)
    __getAddedMass(lineList, weights)
    __printWeightReport(weights, outFile)


