"""
Library for environmental loads (DNV-RP-C205)
"""

import NsgOrcFx.constants as constants
import math

pi = constants.pi
g = constants.gravity

def WaveSpeed(
        waterDepth: float,          # (m) water depth
        period: float,              # (s) wave period
        convCrit: float = 0.001,    # () convergence criteria ratio
        itMax: int = 100            # () max num of iterations
        ) -> float:
    """
    Calculates the wave speed for a given period and water depth
    """
    T = period
    d = waterDepth
    def c(c: float) -> float:
        return g*T/(2*pi)*math.tanh(2*pi*d/(c*T))
    def conv(c: float, cPrev: float) -> bool:
        return abs(c-cPrev)/c <= convCrit
    i = 0
    c0 = 1.0
    c1 = c(c0)
    while i < itMax and not conv(c1, c0):
        i += 1
        c0 = c1
        c1 = c(c0)
    if i == itMax: print('Warning! Max. number of iterations reached.')
    return c1

def WaveParticleHorizMotionAmplitude(
        wavePeriod: float,     # (s) wave period
        waveHeight: float,     # (m) wave height
        waterDepth: float,     # (m) water depth
        z: float,              # (m) vertical coordinate (0 at sea surface and negative value for submerged positions)
        waveSpeed: float=None  # (m/s) wave speed (automatically calculated if = None)
        ) -> float:
    """
    Amplitude the wave particle horizontal motion
    """
    T = wavePeriod
    d = waterDepth
    if waveSpeed == None: waveSpeed = WaveSpeed(d, T)
    L = waveSpeed * T
    H = waveHeight
    k = 2*pi/L
    return H/2.*math.cosh(k*(z+d))/math.sinh(k*d)

def MaxWaveParticleHorizSpeed(
        wavePeriod: float,      # (s) wave period
        waveHeight: float,      # (m) wave height
        waterDepth: float,      # (m) water depth
        z: float,               # (m) vertical coordinate (0 at sea surface)
        waveSpeed: float=None   # (m/s) wave speed (automatically calculated if = None)
        ) -> float:
    """
    Horizontal maximum speed of the wave particle
    """
    T = wavePeriod
    eta = WaveParticleHorizMotionAmplitude(T, waveHeight, waterDepth, z, waveSpeed)
    return 2.*pi*eta/T

def KeuleganCarpenterNumber(
        diameter: float,       # (m) outer diameter (including coating and marine growth)
        wavePeriod: float,     # (s) wave period
        waveHeight: float,     # (m) wave height
        waterDepth: float,     # (m) water depth
        z: float,              # (m) vertical coordinate (0 at sea surface and negative value for submerged positions)
        waveSpeed: float=None  # (m/s) wave speed (automatically calculated if = None)
        )-> float:
    """
    Keulegan-Carpenter number
    """
    eta = WaveParticleHorizMotionAmplitude(wavePeriod, waveHeight, waterDepth, z, waveSpeed)
    return 2*pi*eta/diameter

def DragAmplificationFactor(
        C_DS: float,           # () stead flow drag coefficient
        diameter: float,       # (m) outer diameter (including coating and marine growth)
        wavePeriod: float,     # (s) wave period
        waveHeight: float,     # (m) wave height
        waterDepth: float,     # (m) water depth
        z: float,              # (m) vertical coordinate (0 at sea surface and negative value for submerged positions)
        ) -> float:
    """
    Amplification factor (phi) applied to the stead flow drag coefficient (C_DS)
    to obtain the drag coefficient (C_D) which takes into acount the wave dynamic behavior
    """
    KC = KeuleganCarpenterNumber(diameter, wavePeriod, waveHeight, waterDepth, z)
    Cpi = 1.50-0.024*(12./C_DS-10.)
    if KC <= 0.75:
        return Cpi - 1.0 - 2.0*(KC-0.75)
    elif KC < 2.0:
        return Cpi - 1.0
    elif KC < 12:
        return Cpi + 0.1*(KC-12.)
    elif KC <= 20:
        return -0.0234*KC/C_DS + 1.736
    elif KC < 60:
        return 6.14e-5*(KC/C_DS)**2 - 1.15e-2*(KC/C_DS) + 1.47
    else:
        return 1.0

def SteadFlowDragCoeff(
        roughness: float, # (m) roughness of outer surface
        diameter: float,  # (m) outer diameter
    ) -> float:
    """Stead flow drag coefficient (C_DS)"""
    delta = roughness/diameter
    if delta < 1e-4: # smooth
        return 0.65
    elif delta < 1e-2:
        return (29.+4*math.log10(delta))/20.
    else: # > 1e-2 (rougth)
        return 1.05

def DragCoefficient(
        roughness: float, # (m) roughness of outer surface
        diameter: float,  # (m) outer diameter        
        wavePeriod: float,     # (s) wave period
        waveHeight: float,     # (m) wave height
        waterDepth: float,     # (m) water depth
        z: float,              # (m) vertical coordinate (0 at sea surface and negative value for submerged positions)        
    ) -> float:
    """Drag coefficient in cilinders (e.g., pipe), taking int acount the aplification due to wave (dynamic effect)"""
    C_DS = SteadFlowDragCoeff(roughness, diameter)
    phi = DragAmplificationFactor(C_DS, diameter, wavePeriod, waveHeight, waterDepth, z)
    return C_DS * phi


    
