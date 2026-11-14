"""
Regression of example 4 (tests/test4_modal-analysis.py, README Example 4):
modal analysis of the default line - mode frequencies and normalized mode shape.
"""
import numpy as np
import pandas as pd

N_MODES = 10  # number of mode frequencies stored in the reference


def _canonical_sign(*components):
    """
    Eigenvectors are defined up to a sign, which may flip between OrcaFlex versions/machines.
    Make the sign deterministic: the largest absolute displacement is positive.
    """
    values = np.concatenate([np.asarray(c, dtype=float) for c in components])
    sign = -1.0 if values[np.argmax(np.abs(values))] < 0 else 1.0
    return [sign * np.asarray(c, dtype=float) for c in components]


def test_modal_analysis(ofx, reference):
    model = ofx.Model()
    line = model.CreateLine()

    modes = model.CalculateModal()
    n = min(N_MODES, modes.modeCount)
    assert n > 0

    freqs = pd.DataFrame({
        'mode': list(range(n)),
        'frequency_Hz': [modes.getModeFrequency(i) for i in range(n)],
    })
    reference.check_table('frequencies', freqs)

    mode_index = 0
    arc, ux, uy, uz = modes.GlobalDispShape(line.name, mode_index, True)
    ux, uy, uz = _canonical_sign(ux, uy, uz)
    shape = pd.DataFrame({'arc_length': arc, 'Ux': ux, 'Uy': uy, 'Uz': uz})
    reference.check_table('mode0_shape_normalized', shape)
