"""
Example of extracting extreme constraint loads from multiple simulation files
"""

import sys
from os import path
sys.path.append( path.dirname( path.dirname( path.abspath(__file__) ) ) )

from src import NsgOrcFx as ofx

model = ofx.Model()
vessel = model.CreateObject(ofx.ObjectType.Vessel)
line = model.CreateObject(ofx.ObjectType.Line)