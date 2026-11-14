"""
Self-tests of the reference comparison helpers (no OrcaFlex licence needed).
They guarantee the regression framework itself detects differences.
"""
import json
import math

import pandas as pd
import pytest

import refcompare as rc


def _checker(tmp_path, update):
    return rc.ReferenceChecker(str(tmp_path / 'ref'), str(tmp_path / 'actual'), update, rtol=1e-6, atol=1e-9)


def test_values_match_rules():
    assert rc.values_match('1.0', 1, 1e-6, 0)
    assert rc.values_match(1.0000001, 1.0, 1e-6, 0)
    assert not rc.values_match(1.001, 1.0, 1e-6, 0)
    assert rc.values_match('inf', math.inf, 1e-6, 0)
    assert rc.values_match('nan', float('nan'), 1e-6, 0)
    assert not rc.values_match('nan', 0.0, 1e-6, 0)
    assert rc.values_match('N', 'N', 1e-6, 0)
    assert not rc.values_match('N', 'NE', 1e-6, 0)
    assert not rc.values_match('', '0', 1e-6, 0)
    assert rc.values_match(0.0, 1e-12, 1e-6, 1e-9)  # absolute tolerance near zero


def test_table_roundtrip_and_mismatch(tmp_path):
    df = pd.DataFrame({'name': ['a', 'b'], 'value': [1.0 / 3.0, 2.5e-17]})
    _checker(tmp_path, update=True).check_table('table', df)
    _checker(tmp_path, update=False).check_table('table', df)  # identical -> passes

    df_bad = df.copy()
    df_bad.loc[1, 'name'] = 'c'
    df_bad.loc[0, 'value'] *= 1.001
    with pytest.raises(rc.RegressionMismatch) as err:
        _checker(tmp_path, update=False).check_table('table', df_bad)
    msg = str(err.value)
    assert '2 differing value(s)' in msg
    assert (tmp_path / 'actual' / 'table.csv').is_file()  # actual result saved for diffing


def test_table_shape_change_detected(tmp_path):
    df = pd.DataFrame({'x': [1.0, 2.0]})
    _checker(tmp_path, update=True).check_table('t', df)
    with pytest.raises(rc.RegressionMismatch, match='shape differs'):
        _checker(tmp_path, update=False).check_table('t', pd.DataFrame({'x': [1.0, 2.0, 3.0]}))


def test_values_json(tmp_path):
    import numpy as np
    vals = {'a': 1.5, 'b': [1, 2, 3], 'c': 'text', 'd': np.float64(math.inf), 'e': np.array([0.1, 0.2])}
    _checker(tmp_path, update=True).check_values('v', vals)
    stored = json.loads((tmp_path / 'ref' / 'v.json').read_text())
    assert stored['d'] == 'inf'
    _checker(tmp_path, update=False).check_values('v', vals)

    with pytest.raises(rc.RegressionMismatch, match='missing keys'):
        _checker(tmp_path, update=False).check_values('v', {k: v for k, v in vals.items() if k != 'c'})
    with pytest.raises(rc.RegressionMismatch, match='length differs'):
        _checker(tmp_path, update=False).check_values('v', {**vals, 'b': [1, 2]})


def test_missing_reference_is_an_error(tmp_path):
    with pytest.raises(rc.ReferenceMissing, match='--update-refs'):
        _checker(tmp_path, update=False).check_values('nothing', {'a': 1})


def test_excel_grids(tmp_path):
    xlsx = tmp_path / 'f.xlsx'
    idx = pd.MultiIndex.from_tuples([('d1', 'N', 1.0), ('d1', 'E', 2.0)], names=['Draught', 'Dir', 'Hs'])
    cols = pd.MultiIndex.from_tuples([('Position', 'Surge'), ('Position', 'Sway')])
    df = pd.DataFrame([[0.1, 0.2], [0.3, 0.4]], index=idx, columns=cols)
    with pd.ExcelWriter(xlsx) as w:
        df.to_excel(w, sheet_name='All results')
        df.T.to_excel(w, sheet_name='Other')
    _checker(tmp_path, update=True).check_excel('out', str(xlsx))
    assert (tmp_path / 'ref' / 'out__All_results.csv').is_file()
    _checker(tmp_path, update=False).check_excel('out', str(xlsx))

    df.iloc[1, 1] = 0.5
    with pd.ExcelWriter(xlsx) as w:
        df.to_excel(w, sheet_name='All results')
        df.T.to_excel(w, sheet_name='Other')
    with pytest.raises(rc.RegressionMismatch):
        _checker(tmp_path, update=False).check_excel('out', str(xlsx))


def test_numeric_only_comparison():
    a = rc.csv_text_to_grid('N,1.0,LC_N\nE,2.0,LC_E\n')
    b = rc.csv_text_to_grid('0,1.0,LC_0\n90,2.0,LC_90\n')
    assert rc.compare_grids(a, b, 1e-6, 0, numeric_only=True).ok
    assert not rc.compare_grids(a, b, 1e-6, 0).ok
