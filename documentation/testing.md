# Regression testing

NsgOrcFx is published on PyPI and used in engineering projects, so **a change must not alter
previously obtained results** unless it is an intentional correction. The regression tests
re-run the documented examples and compare their outputs with reference results stored in the
repository.

## Overview

| Item | Location |
|---|---|
| Example scripts (also shown in the README) | `tests/test*.py` |
| Regression tests (pytest) | `tests/regression/test_*.py` |
| Comparison helpers | `tests/regression/refcompare.py` |
| Fixtures / command line options | `tests/regression/conftest.py` |
| **Stored references** | `tests/regression/references/<test module>/<test id>/` |
| Environment used to generate the references | `tests/regression/references/_metadata.json` |
| Actual results of a failed comparison (git-ignored) | `tests/regression/_actual/` |

References are plain text (CSV for tables and Excel sheets, JSON for values and lists).
This makes every change to a reference visible and reviewable in `git diff` and in pull requests.

## Requirements

* Windows with OrcaFlex installed and an **available OrcaFlex licence**. Tests that need OrcaFlex
  are *skipped*, with the reason shown, when no licence can be obtained. If the licence comes
  from a network server, all seats may be in use ("Licensed number of users already reached").
* Python packages: `py -m pip install -e .[test]` (installs pytest and openpyxl in addition to
  the package dependencies).

## Running

From the repository root:

```
py -m pytest                        # all regression tests (compares with the references)
py -m pytest -m "not slow"          # skip the slow tests (simulations)
py -m pytest -k vessel              # only the tests whose name contains 'vessel'
py -m pytest --run-examples         # also run every example script tests/test*.py (smoke test)
py -m pytest --installed            # test the installed package (e.g. a wheel from PyPI) instead of ./src
py -m pytest --rtol 1e-4            # looser relative tolerance (default 1e-6; --atol default 1e-9)
```

By default the tests import the package from `./src` (the conftest checks this). Use `--installed`
to validate a built wheel, e.g. after `py -m pip install dist\nsgorcfx-X.Y.Z-py3-none-any.whl`.

Every test runs in its own temporary folder, so nothing is written to the repository. This matters
because some package functions write temporary files to the *current* folder (wave search,
spectral response).

## What is compared

| Test module | Example / README | Compared outputs |
|---|---|---|
| `test_00_refcompare` | – | Self-tests of the comparison helpers (no OrcaFlex needed) |
| `test_01_data_access` | Example 1 | Values read and written through the `data` attribute; `findLineByName`, `getAllLines` |
| `test_02_reduced_duration` | Example 2 | `WaveTimeOrigin`, `WaveTz`, stage durations after `SetReducedSimulationDuration(200)`; no temporary files left behind |
| `test_03_load_cases` | Example 3 | For regular, irregular and irregular-reduced runs: generated file names, `_CaseList.xlsx`, and the wave/stage parameters read back from every generated `.dat` |
| `test_04_modal` | Example 4 | First 10 mode frequencies; normalized shape of mode 0 (sign made deterministic, since eigenvector signs are arbitrary) |
| `test_05_fatigue` | Example 5 | Arc length, damage and life per node; total exposure time |
| `test_06_rao_plots` | Example 6 | Names of the generated plot files and that they are valid PNG files (no pixel comparison, since images change with matplotlib/font versions) |
| `test_07_constraint_loads` (slow) | Example 7 | Simulation files created; both sheets of the extreme constraint loads Excel file |
| `test_08_vessel_response` | Example 8 (`test8`, `test8a`, `test8b`) | Both sheets ("Critical LCs", "All results") of the Excel output for directions as letters, letters + gamma, and numbers; **cross-check** that letters and numbers give identical values |
| `test_99_examples_smoke` (opt-in) | all example scripts | Each script runs without error (`--run-examples`) |

### Comparison rules

* Every cell or value is compared. When both sides are numbers, the comparison is
  `math.isclose(actual, expected, rel_tol=rtol, abs_tol=atol)`, with `inf == inf` and `nan == nan`.
  Otherwise the strings must be identical.
* Excel files are compared sheet by sheet as raw cell grids, so headers, index labels, load case
  names and values are all checked. The list of sheet names is also checked.
* A change in shape (rows/columns, list length, dictionary keys) is always a failure.
* A missing reference is an **error**, not a skip. It tells you to generate the reference.

When a comparison fails, the message lists the first differing cells (with relative difference)
and the full actual result is saved under `tests/regression/_actual/`, so it can be diffed against
the reference file.

## Workflow for a change in the package

1. Before changing anything, run `py -m pytest` and confirm all tests pass with **0 skipped**
   (except the opt-in examples).
2. Make the change.
3. Run `py -m pytest` again.
   * **All pass:** previous results are preserved.
   * **Failures:** decide whether the change in results is intended.
     * Not intended: fix the code.
     * Intended (bug fix or a deliberate improvement): regenerate only the affected references
       (next section) and explain the change in the commit / pull request.
4. For new features, add a regression test (and preferably an example script + README example).

## Generating / updating references

```
py -m pytest --update-refs                          # all tests
py -m pytest --update-refs -k "modal or fatigue"   # only selected tests
```

In update mode the tests write their current results as the references and also record the
environment (OrcaFlex DLL, OrcFxAPI, Python, numpy, pandas versions) in `references/_metadata.json`.
Afterwards:

```
git diff --stat tests/regression/references
git diff tests/regression/references
```

Review every changed file before committing, and commit references together with the code
change that justifies them. Never update references only to make failing tests pass without
understanding the difference.

## Different OrcaFlex / Python versions

The references are generated with one specific OrcaFlex version (see `_metadata.json`). When the
current environment differs, pytest prints a summary of the differences at the end of the run.
New OrcaFlex versions may change results slightly (numerics) or significantly (changed defaults
of new objects). In that case:

1. Run the tests on the **unchanged** code (e.g. the latest released tag) with the new
   environment. Differences seen at this stage come from the environment, not from NsgOrcFx.
2. If they are small, the tolerance can be loosened for that run (`--rtol 1e-4`). Otherwise,
   regenerate the references with the unchanged code (`--update-refs`) and commit them
   separately ("update references for OrcaFlex X.Y").
3. Only then apply and test the code changes.

## Adding a new regression test

Create `tests/regression/test_NN_<topic>.py` and use the fixtures:

```python
def test_my_feature(ofx, workdir, reference):
    # ofx       -> the NsgOrcFx package under test (skips when no licence is available)
    # workdir   -> temporary folder, also the current working directory
    # reference -> ReferenceChecker bound to this test
    model = ofx.Model()
    ...
    reference.check_values('summary', {'value': x, 'list': [1, 2]})   # -> summary.json
    reference.check_table('table', dataframe)                         # -> table.csv
    reference.check_excel('output', str(workdir / 'out.xlsx'))        # -> output__<sheet>.csv
```

Then run `py -m pytest --update-refs -k my_feature`, review the generated files and commit them.

Guidelines:
* Write outputs to `workdir`/`tmp_path`, never to the repository.
* Compare numbers that are produced or transformed by NsgOrcFx. Avoid comparing binary files
  (`.dat`, `.sim`, images) directly. Read back the relevant parameters instead.
* Make results deterministic, e.g. sort file lists and fix the sign of mode shapes.
* Mark tests that take more than about a minute with `@pytest.mark.slow`.
* Use a module-scoped fixture when several tests share one expensive computation
  (see `test_03_load_cases.py` and `test_08_vessel_response.py`).

## Before publishing a release on PyPI

1. `py -m pytest --run-examples`: everything passes, with nothing skipped.
2. Bump the version in `pyproject.toml` (and keep `src/NsgOrcFx/__init__.py` `__version__` in sync).
3. Build (`py -m build`), install the wheel in a clean environment and run
   `py -m pytest --installed`.
4. Upload (see `upload_production.py`).
