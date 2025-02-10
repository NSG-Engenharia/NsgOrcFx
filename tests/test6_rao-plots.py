"""
Example of RAO plot generation
"""

import sys
from os import path
sys.path.append( path.dirname( path.dirname( path.abspath(__file__) ) ) )

from src import NsgOrcFx as ofx

model = ofx.Model()
vt = model.CreateObject(ofx.ObjectType.VesselType)
model.SaveRAOplots(r'tests\tmptestfiles')