"""
Regression of example 5 (tests/test5_fatigue.py, README Example 5):
rainflow fatigue analysis with the DNV F3 (seawater) S-N curve - damage and life per node.
"""
import numpy as np


def test_fatigue_life(ofx, workdir, reference):
    sim_file = str(workdir / 'fatigue.sim')
    ftg_file = str(workdir / 'fatigue.ftg')

    model = ofx.Model()
    model.CreateLine()
    model.RunSimulation()
    model.Save(sim_file)

    analysis = ofx.FatigueAnalysis()
    analysis.data.AnalysisType = 'Rainflow'
    analysis.data.LoadCaseCount = 1
    analysis.addLoadCase(sim_file)
    analysis.addSNCurveByNameAndEnv('F3', 'seawater')
    analysis.addAnalysisData()
    analysis.Calculate()
    analysis.Save(ftg_file)

    df = analysis.getArcLengthDamageLifeListAsDF()
    assert len(df) > 0
    # consistency between the helper methods (assert_array_equal treats nan == nan)
    np.testing.assert_array_equal(df['Life (years)'].to_numpy(), analysis.getLifeList())
    np.testing.assert_array_equal(df['Damage'].to_numpy(), analysis.getDamageList())

    reference.check_values('summary', {
        'totalExposureTime': analysis.totalExposureTime(),
        'n_nodes': len(df),
    })
    # damage can be very small: no absolute tolerance, relative only
    reference.check_table('arc_damage_life', df, atol=0.0)
