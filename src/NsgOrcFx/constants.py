"""
Constants
"""

import math

gravity = 9.81 # (m/s2)
pi = math.pi

# Degree of fredoom string ids
dofStrs = ['Ux', 'Uy', 'Uz', 'Rx', 'Ry', 'Rz']


# Wave types
regularWaveTypes = ['Airy', 'Dean stream', "Stokes' 5th", 'Cnoidal',] 
irregularWaveTypes = [
    'JONSWAP', 'ISSC', 'Ochi-Hubble', 'Torsethaugen', 'Gaussian swell',
    'User defined spectrum', 'User specified components', 'Time history',
    'Response calculation']
