"""
Regression of example 8 (tests/test8_*.py, README Example 8):
vessel extreme responses for multiple wave directions and Hs x Tp (x Gamma) combinations.

Variants (same as the example scripts):
* letters_hs_tp       -> tests/test8_HsTp-wave-selection.py   (directions as 'N', 'NE', ...; (Hs, Tp))
* letters_hs_tp_gamma -> tests/test8a_HsTp-wave-selection.py  (directions as letters; (Hs, Tp, Gamma))
* numbers_hs_tp       -> tests/test8b_HsTp-wave-selection.py  (directions as numbers 0, 45, ...; (Hs, Tp))

Besides the comparison with the references, the numeric results of `letters_hs_tp` and
`numbers_hs_tp` must be identical (same directions, given as letters or as numbers).
"""
import os

import pytest

import refcompare as rc

HS_TP = [
    [(4.1, 5.1), (4.4, 5.6), (4.6, 6.1), (4.8, 6.5), (5, 7), (5.2, 7.5), (5.3, 7.9)],
    [(5.4, 8.4), (5.5, 8.9), (5.5, 9.3), (5.5, 9.8), (5.5, 10.3), (5.4, 10.7), (5.3, 11.2)],
    [(5, 11.7), (4.9, 12.1), (4.6, 12.6), (4.3, 13.1), (3.9, 13.5), (3.5, 14), (2.8, 14.5)],
    [(5.9, 8.5), (6.1, 8.9), (6.2, 9.4), (6.3, 9.9), (6.3, 10.3), (6.4, 10.8), (6.4, 11.3)],
    [(4.5, 5.2), (4.7, 5.6), (4.9, 6.1), (5.2, 6.6), (5.5, 7), (5.6, 7.5), (5.7, 8)],
    [(6.4, 11.7), (6.3, 12.2), (6.3, 12.7), (6.2, 13.1), (6, 13.6), (5.7, 14.1), (5.6, 14.6)],
    [(5.2, 15), (4.8, 15.5), (4.3, 16), (3.6, 16.4)],
    [(3.1, 9), (3.3, 9.5), (3.5, 10), (3.7, 10.4), (3.9, 10.9), (4.1, 11.4), (4.3, 11.8)],
]
HS_TP_GAMMA = [
    [(4.1, 5.1, 3.3), (4.4, 5.6, 3.32), (4.6, 6.1, 3.34), (4.8, 6.5, 3.36), (5, 7, 3.38), (5.2, 7.5, 3.4), (5.3, 7.9, 3.42)],
    [(5.4, 8.4, 3.43), (5.5, 8.9, 3.45), (5.5, 9.3, 3.47), (5.5, 9.8, 3.49), (5.5, 10.3, 3.51), (5.4, 10.7, 3.53), (5.3, 11.2, 3.55)],
    [(5, 11.7, 3.56), (4.9, 12.1, 3.58), (4.6, 12.6, 3.6), (4.3, 13.1, 3.62), (3.9, 13.5, 3.64), (3.5, 14, 3.66), (2.8, 14.5, 3.68)],
    [(5.9, 8.5, 3.45), (6.1, 8.9, 3.47), (6.2, 9.4, 3.49), (6.3, 9.9, 3.51), (6.3, 10.3, 3.53), (6.4, 10.8, 3.55), (6.4, 11.3, 3.57)],
    [(4.5, 5.2, 3.2), (4.7, 5.6, 3.22), (4.9, 6.1, 3.24), (5.2, 6.6, 3.26), (5.5, 7, 3.28), (5.6, 7.5, 3.3), (5.7, 8, 3.32)],
    [(6.4, 11.7, 3.55), (6.3, 12.2, 3.57), (6.3, 12.7, 3.59), (6.2, 13.1, 3.61), (6, 13.6, 3.63), (5.7, 14.1, 3.65), (5.6, 14.6, 3.67)],
    [(5.2, 15, 3.6), (4.8, 15.5, 3.62), (4.3, 16, 3.64), (3.6, 16.4, 3.66)],
    [(3.1, 9, 3.25), (3.3, 9.5, 3.27), (3.5, 10, 3.29), (3.7, 10.4, 3.31), (3.9, 10.9, 3.33), (4.1, 11.4, 3.35), (4.3, 11.8, 3.37)],
]
LETTERS = ['N', 'NE', 'E', 'SE', 'S', 'SW', 'W', 'NW']
NUMBERS = [0, 45, 90, 135, 180, 225, 270, 315]

VARIANTS = {
    'letters_hs_tp': dict(zip(LETTERS, HS_TP)),
    'letters_hs_tp_gamma': dict(zip(LETTERS, HS_TP_GAMMA)),
    'numbers_hs_tp': dict(zip(NUMBERS, HS_TP)),
}

POSITION = [35, 0, 0]
NORTH_DIRECTION = 90


@pytest.fixture(scope='module')
def responses(ofx, tmp_path_factory):
    """Runs every variant once per module; returns {variant: output .xlsx path}."""
    root = tmp_path_factory.mktemp('vessel_response')
    cwd = os.getcwd()
    os.chdir(root)  # spectral response temporary .csv files are written to the current folder
    outputs = {}
    try:
        for variant, wave_params in VARIANTS.items():
            model = ofx.Model()
            vessel = model.CreateObject(ofx.ObjectType.Vessel)
            model.environment.WaveType = 'JONSWAP'
            model.general.NorthDirection = NORTH_DIRECTION
            out = root / f'{variant}.xlsx'
            model.ProcessExtremeResponses(vessel.name, POSITION, wave_params, str(out))
            outputs[variant] = out
        leftovers = [f for f in os.listdir(root) if f.endswith('.csv')]
    finally:
        os.chdir(cwd)
    assert leftovers == [], f'temporary files left behind: {leftovers}'
    return outputs


@pytest.mark.parametrize('variant', list(VARIANTS))
def test_extreme_responses(responses, reference, variant):
    reference.check_excel('vessel_response', str(responses[variant]))


def test_letters_and_numbers_give_same_results(responses, pytestconfig):
    """Directions given as letters ('N', 'NE', ...) or numbers (0, 45, ...) must give the same values."""
    a = rc.excel_to_grids(str(responses['letters_hs_tp']))
    b = rc.excel_to_grids(str(responses['numbers_hs_tp']))
    assert list(a) == list(b)
    for sheet in a:
        result = rc.compare_grids(a[sheet], b[sheet], rtol=1e-12, atol=0.0, numeric_only=True)
        assert result.ok, result.report(f'sheet "{sheet}" (letters vs numbers)')
