"""
Regression of example 2 (tests/test2_searchwave.py, README Example 2):
reduced simulation duration for irregular waves (largest rise placed at the middle of stage 1).
"""
import os


def test_reduced_simulation_duration(ofx, workdir, reference):
    model = ofx.Model()
    env = model.environment
    env.data.WaveType = 'JONSWAP'
    env.data.WaveHs = 2.5
    env.data.WaveGamma = 2
    env.data.WaveTp = 8

    model.SetReducedSimulationDuration(200)

    # the example saves the data file; check that it is still possible
    model.Save(str(workdir / 'reduced.dat'))
    assert (workdir / 'reduced.dat').is_file()

    # no temporary wave search file must be left in the working folder
    leftovers = [f for f in os.listdir(workdir) if f.startswith('SearchWave')]
    assert leftovers == [], f'temporary files left behind: {leftovers}'

    general = model.general
    assert general.StageDuration[1] == 200

    reference.check_values('values', {
        'WaveTimeOrigin': env.WaveTimeOrigin,
        'WaveTz': env.WaveTz,
        'WaveHs': env.WaveHs,
        'WaveTp': env.WaveTp,
        'WaveGamma': env.WaveGamma,
        'StageDuration': [general.StageDuration[0], general.StageDuration[1]],
    })
