"""
Example of calculating modal analysis and getting the normalized modal shape 
"""

import NsgOrcFx

model = NsgOrcFx.Model()
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
