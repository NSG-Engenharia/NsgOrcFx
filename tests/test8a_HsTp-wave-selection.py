import sys
from os import path
sys.path.append( path.dirname( path.dirname( path.abspath(__file__) ) ) )

from src import NsgOrcFx as ofx


# for each wave direction (coming from), define the list with tuples of (Hs, Tp, Gamma) values
# if Gamma is not provided, the value defined in the OrcaFlex model will be used
# below is an example with 8 wave directions
# this data is typically obtained from the metocean report
waveDirsHsTpGamma = {
    'N': [
        (4.1, 5.1, 3.3), (4.4, 5.6, 3.32), (4.6, 6.1, 3.34), (4.8, 6.5, 3.36), (5, 7, 3.38), (5.2, 7.5, 3.4), (5.3, 7.9, 3.42),
    ],
    'NE': [
        (5.4, 8.4, 3.43), (5.5, 8.9, 3.45), (5.5, 9.3, 3.47), (5.5, 9.8, 3.49), (5.5, 10.3, 3.51), (5.4, 10.7, 3.53), (5.3, 11.2, 3.55)
    ],
    'E': [
        (5, 11.7, 3.56), (4.9, 12.1, 3.58), (4.6, 12.6, 3.6), (4.3, 13.1, 3.62), (3.9, 13.5, 3.64), (3.5, 14, 3.66), (2.8, 14.5, 3.68)       
    ],
    'SE': [
        (5.9, 8.5, 3.45), (6.1, 8.9, 3.47), (6.2, 9.4, 3.49), (6.3, 9.9, 3.51), (6.3, 10.3, 3.53), (6.4, 10.8, 3.55), (6.4, 11.3, 3.57),
    ],
    'S': [
        (4.5, 5.2, 3.2), (4.7, 5.6, 3.22), (4.9, 6.1, 3.24), (5.2, 6.6, 3.26), (5.5, 7, 3.28), (5.6, 7.5, 3.3), (5.7, 8, 3.32), 
    ],
    'SW': [
        (6.4, 11.7, 3.55), (6.3, 12.2, 3.57), (6.3, 12.7, 3.59), (6.2, 13.1, 3.61), (6, 13.6, 3.63), (5.7, 14.1, 3.65), (5.6, 14.6, 3.67),
    ],
    'W': [
        (5.2, 15, 3.6), (4.8, 15.5, 3.62), (4.3, 16, 3.64), (3.6, 16.4, 3.66), 
    ],
    'NW': [
        (3.1, 9, 3.25), (3.3, 9.5, 3.27), (3.5, 10, 3.29), (3.7, 10.4, 3.31), (3.9, 10.9, 3.33), (4.1, 11.4, 3.35), (4.3, 11.8, 3.37),
    ],
}


# create model and vessel
model = ofx.Model()
vessel = model.CreateObject(ofx.ObjectType.Vessel)
vesselName = vessel.name

# set irregular wave (required for vessel response analysis)
model.environment.WaveType = 'JONSWAP'

# set north direction (required for wave direction definition)
model.general.NorthDirection = 90

# process extreme responses
model.ProcessExtremeResponses(
    vesselName, 
    [35, 0, 0], # position where responses are extracted
    waveDirsHsTpGamma, # wave directions with Hs and Tp values
    r".\tests\tmptestfiles\test8a vessel response.xlsx", # output excel file
    )

# the generated excel file lists the extreme responses for all wave conditions defined above
# and the load cases that lead to the maximum value for each response DOF parameter
# in addition to the results directly provided by OrcaFlex, rotation (vectorial sum of roll and pitch) is included