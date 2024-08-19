"""
Example of calculating modal analysis and getting the normalized modal shape 
"""

import sys
from os import path
sys.path.append( path.dirname( path.dirname( path.abspath(__file__) ) ) )

from src import NsgOrcFx as ofx

model = ofx.Model()
model.CreateLine()


modes = model.CalculateModal()

# mode shape index (0 for the 1st)
modeIndex = 0

# mode frequency
freq = modes.getModeFrequency(modeIndex)

# if normalize = True, the displacements will be normalized, so the maximum total displacements is equal to the line diameter
[arcLengths, Ux, Uy, Uz] = modes.GlobalDispShape('Line1', modeIndex, True)
print('Frequency = ', freq, 'Hz')
print(arcLengths, Ux, Uy, Uz)
