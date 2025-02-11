"""
Example of extracting extreme constraint loads from multiple simulation files
"""

import sys
from os import path
sys.path.append( path.dirname( path.dirname( path.abspath(__file__) ) ) )

from src import NsgOrcFx as ofx

# create the model
model = ofx.Model()

# create the objects (vessel, constraint, and line)
vessel = model.CreateObject(ofx.ObjectType.Vessel)
constraint = model.CreateObject(ofx.ObjectType.Constraint)
line = model.CreateObject(ofx.ObjectType.Line)

# connect the constraint to the vessel
constraint.name = 'Hang-off'
constraint.InFrameConnection = vessel.name
constraint.InFrameInitialX = 35
constraint.InFrameInitialY = 0
constraint.InFrameInitialZ = -7
constraint.InFrameInitialDeclination = 155 # adjust the nominal top angle

# connect the line End A to the constraint, 
# anchor the End B, 155m horizontally away from A, 
# and set the line length
line.EndAConnection = constraint.name
line.EndAX, line.EndAY, line.EndAZ = 0, 0, 0
line.EndAxBendingStiffness = ofx.OrcinaInfinity() # to produce moment reaction loads to extract
line.EndBConnection = 'Anchored'
line.PolarReferenceAxes[1] = 'Global Axes'
line.PolarR[1], line.EndBY, line.EndBHeightAboveSeabed = 155, 0, 0
line.Length[0] = 200

# generate the load cases
model.GenerateLoadCases('Dean stream', [135,180,225], [6,7], [9,10], '.')

# run the simulations with multi-threading
ofx.ProcMultiThread('.','.')

# extract extreme loads for the constraint
ofx.ExtremeLoadsFromConstraints('.','.\Results.xlsx')
