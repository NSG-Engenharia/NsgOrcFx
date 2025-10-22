import sys
from os import path
sys.path.append( path.dirname( path.dirname( path.abspath(__file__) ) ) )

from src import NsgOrcFx as ofx


# for each wave direction (coming from), define the list with tuples of (Hs, Tp) values
# below is an example with 8 wave directions
# this data is typically obtained from the metocean report
waveDirsHsTp = {
    'N': [
        (4.1,5.1), (4.4,5.6), (4.6,6.1), (4.8,6.5), (5,7), (5.2,7.5), (5.3,7.9),
    ],
    'NE': [
        (5.4,8.4), (5.5,8.9), (5.5,9.3), (5.5,9.8), (5.5,10.3), (5.4,10.7), (5.3,11.2)
    ],
    'E': [
        (5,11.7), (4.9,12.1), (4.6,12.6), (4.3,13.1), (3.9,13.5), (3.5,14), (2.8,14.5)       
    ],
    'SE': [
        (5.9,8.5), (6.1,8.9), (6.2,9.4), (6.3,9.9), (6.3,10.3), (6.4,10.8), (6.4,11.3),
    ],
    'S': [
        (4.5,5.2), (4.7,5.6), (4.9,6.1), (5.2,6.6), (5.5,7), (5.6,7.5), (5.7,8), 
    ],
    'SW': [
        (6.4,11.7), (6.3,12.2), (6.3,12.7), (6.2,13.1), (6,13.6), (5.7,14.1), (5.6,14.6),
    ],
    'W': [
        (5.2,15), (4.8,15.5), (4.3,16), (3.6,16.4), 
    ],
    'NW': [
        (3.1,9), (3.3,9.5), (3.5,10), (3.7,10.4), (3.9,10.9), (4.1,11.4), (4.3,11.8),
    ],
    }


# create model and vessel
model = ofx.Model()
vessel = model.CreateObject(ofx.ObjectType.Vessel)
vesselName = vessel.name

# set irregular wave (required for vessel response analysis)
model.environment.WaveType = 'JONSWAP'

# set north direction (required for wave direction definition)
model.general.NorthDirectionDefined = 'Yes'
model.general.NorthDirection = 90

# process extreme responses
model.ProcessExtremeResponses(
    vesselName, 
    [35, 0, 0], # position where responses are extracted
    waveDirsHsTp, # wave directions with Hs and Tp values
    r".\tests\tmptestfiles\vessel response.xlsx", # output excel file
    )

# the generated excel file lists the extreme responses for all wave conditions defined above
# and the load cases that lead to the maximum value for each response DOF parameter
# in addition to the results directly provided by OrcaFlex, rotation (vectorial sum of roll and pitch) is included