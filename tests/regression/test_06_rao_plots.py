"""
Regression of example 6 (tests/test6_rao-plots.py, README Example 6):
RAO plots (amplitude and phase) of the default vessel type.

Images are NOT compared pixel by pixel (they change with matplotlib/fonts versions);
the names of the generated files and their validity (PNG, non-empty) are checked.
"""
import os

PNG_MAGIC = b'\x89PNG\r\n\x1a\n'


def test_rao_plots(ofx, workdir, reference):
    from matplotlib import pyplot as plt

    out = workdir / 'plots'
    out.mkdir()

    model = ofx.Model()
    model.CreateObject(ofx.ObjectType.VesselType)
    try:
        model.SaveRAOplots(str(out))
    finally:
        plt.close('all')

    files = sorted(os.listdir(out))
    # SaveFig swallows exceptions (prints 'Erro'), so the files must be checked explicitly
    assert files, 'no RAO plot was generated'
    for f in files:
        data = (out / f).read_bytes()
        assert data.startswith(PNG_MAGIC), f'{f} is not a PNG file'
        assert len(data) > 1000, f'{f} is suspiciously small ({len(data)} bytes)'

    reference.check_values('files', {'files': files})
