"""
Regression of example 7 (tests/test7_constraint-load-results.py, README Example 7):
load case generation + multi-thread simulation + extreme constraint loads to Excel.

Slow: runs 12 dynamic simulations.
"""
import os

import pytest


@pytest.mark.slow
def test_extreme_constraint_loads(ofx, workdir, reference):
    model = ofx.Model()

    vessel = model.CreateObject(ofx.ObjectType.Vessel)
    constraint = model.CreateObject(ofx.ObjectType.Constraint)
    line = model.CreateObject(ofx.ObjectType.Line)

    constraint.name = 'Hang-off'
    constraint.InFrameConnection = vessel.name
    constraint.InFrameInitialX = 35
    constraint.InFrameInitialY = 0
    constraint.InFrameInitialZ = -7
    constraint.InFrameInitialDeclination = 155

    line.EndAConnection = constraint.name
    line.EndAX, line.EndAY, line.EndAZ = 0, 0, 0
    line.EndAxBendingStiffness = ofx.OrcinaInfinity()
    line.EndBConnection = 'Anchored'
    line.PolarReferenceAxes[1] = 'Global Axes'
    line.PolarR[1], line.EndBY, line.EndBHeightAboveSeabed = 155, 0, 0
    line.Length[0] = 200

    # the example uses '.' for every folder; here they are separated to check each step
    lc_dir = workdir / 'lc'
    sim_dir = workdir / 'sim'
    lc_dir.mkdir()
    sim_dir.mkdir()
    results = workdir / 'Results.xlsx'

    model.GenerateLoadCases('Dean stream', [135, 180, 225], [6, 7], [9, 10], str(lc_dir))
    ofx.ProcMultiThread(str(lc_dir), str(sim_dir))
    ofx.ExtremeLoadsFromConstraints(str(sim_dir), str(results))

    sims = sorted(f for f in os.listdir(sim_dir) if f.endswith('.sim'))
    assert len(sims) == 12, f'expected 12 simulation files, got {sims}'
    # successfully simulated .dat files are deleted by default (del_success_dat=True)
    assert sorted(f for f in os.listdir(lc_dir) if f.endswith('.dat')) == []
    assert results.is_file()

    reference.check_values('sim_files', {'files': sims})
    reference.check_excel('results', str(results))
