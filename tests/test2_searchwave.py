import NsgOrcFx as ofx

model = ofx.Model()

# set irregular wave
model.environment.data.WaveType = 'JONSWAP'
model.environment.data.WaveHs = 2.5
model.environment.data.WaveGamma = 2
model.environment.data.WaveTp = 8

# set reduced simulation duration with 200 seconds
model.SetReducedSimulationDuration(200)

# save data file to check the wave history
model.Save('reduced.dat')

# after executing this code, open the generated data file
# then open Environment -> Waves preview, and set duration of 200s 
# click in View profile and observe that the largest event (rise or fall)
# is in the midle of the sea elevation history
