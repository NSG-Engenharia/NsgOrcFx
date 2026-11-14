"""
Regression of example 1 (tests/test1_data-auto-complete.py, README Example 1):
`data` attribute access (get/set), line creation and line lookup helpers.
"""


def test_data_access(ofx, reference):
    model = ofx.Model()
    line = model.CreateLine()

    values = {
        'line_name': line.name,
        'EndAConnection_default': line.data.EndAConnection,
        'general_ImplicitConstantTimeStep_default': model.general.data.ImplicitConstantTimeStep,
        'environment_WaveType_default': model.environment.data.WaveType,
        'environment_WaveHeight_default': model.environment.data.WaveHeight,
    }

    # set through the `data` attribute (as in the example)
    model.general.data.ImplicitConstantTimeStep = 0.01
    model.environment.data.WaveHeight = 5.0
    line.data.EndAConnection = 'Anchored'

    # values must be visible both through `data` and through the original OrcFxAPI attribute
    assert model.general.data.ImplicitConstantTimeStep == model.general.ImplicitConstantTimeStep == 0.01
    assert model.environment.data.WaveHeight == model.environment.WaveHeight == 5.0
    assert line.data.EndAConnection == line.EndAConnection == 'Anchored'

    # lookup helpers
    found = model.findLineByName(line.name)
    assert found.name == line.name
    assert hasattr(found, 'data')
    lines = model.getAllLines()
    assert [ln.name for ln in lines] == [line.name]

    values.update({
        'general_ImplicitConstantTimeStep_set': model.general.data.ImplicitConstantTimeStep,
        'environment_WaveHeight_set': model.environment.data.WaveHeight,
        'EndAConnection_set': line.data.EndAConnection,
        'all_lines': [ln.name for ln in lines],
        'line_TotalLength': line.TotalLength,
    })
    reference.check_values('values', values)
