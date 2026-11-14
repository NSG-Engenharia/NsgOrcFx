"""
Regression of example 3 (tests/test3_generate-loadcases.py, README Example 3):
load case generation for regular, irregular and irregular-with-reduced-duration waves.

Compared for each run:
* list of generated files
* the `_CaseList.xlsx` table
* the wave/stage parameters read back from every generated .dat file
"""
import os

import pandas as pd
import pytest

DIRECTIONS = [0, 45, 90]
HEIGHTS = [1.5, 2.0, 3.0]
PERIODS = [5, 7, 9]

# (run id, wave type, extra kwargs) - executed in this order on the same model, as in the example
RUNS = [
    ('regular', 'Dean stream', {}),
    ('irregular', 'JONSWAP', {}),
    ('irregular_reduced', 'JONSWAP', {'reducedIrregDuration': 200}),
]


@pytest.fixture(scope='module')
def generated(ofx, tmp_path_factory):
    """Generates the three sets of load cases (once per module), each in its own folder."""
    root = tmp_path_factory.mktemp('loadcases')
    cwd = os.getcwd()
    os.chdir(root)  # wave search writes temporary files to the current folder
    try:
        model = ofx.Model()
        model.CreateLine()
        folders = {}
        for run_id, wave_type, kwargs in RUNS:
            folder = root / run_id
            folder.mkdir()
            model.GenerateLoadCases(wave_type, DIRECTIONS, HEIGHTS, PERIODS, str(folder), **kwargs)
            folders[run_id] = folder
    finally:
        os.chdir(cwd)
    return folders


def _read_case_parameters(ofx, folder) -> pd.DataFrame:
    rows = []
    for f in sorted(os.listdir(folder)):
        if not f.endswith('.dat'):
            continue
        model = ofx.Model(str(folder / f))
        env, gen = model.environment, model.general
        regular = env.WaveType in ('Airy', 'Dean stream', "Stokes' 5th", 'Cnoidal')
        rows.append({
            'File': f,
            'WaveType': env.WaveType,
            'WaveDirection': env.WaveDirection,
            'WaveHeight': env.WaveHeight if regular else None,
            'WavePeriod': env.WavePeriod if regular else None,
            'WaveHs': None if regular else env.WaveHs,
            'WaveTp': None if regular else env.WaveTp,
            'WaveGamma': None if regular else env.WaveGamma,
            'WaveTimeOrigin': None if regular else env.WaveTimeOrigin,
            'StageDuration0': gen.StageDuration[0],
            'StageDuration1': gen.StageDuration[1],
        })
    return pd.DataFrame(rows)


@pytest.mark.parametrize('run_id', [r[0] for r in RUNS])
def test_generate_load_cases(ofx, generated, reference, run_id):
    folder = generated[run_id]
    files = sorted(os.listdir(folder))
    n_cases = len(DIRECTIONS) * len(HEIGHTS) * len(PERIODS)
    assert len([f for f in files if f.endswith('.dat')]) == n_cases
    assert '_CaseList.xlsx' in files

    reference.check_values('files', {'files': files})
    reference.check_excel('case_list', str(folder / '_CaseList.xlsx'))
    reference.check_table('case_parameters', _read_case_parameters(ofx, folder))
