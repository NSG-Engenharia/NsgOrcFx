# AGENTS.md

Guidance for Codex (and human contributors) working in this repository.

## What this is

**NsgOrcFx** is a public Python package ([PyPI](https://pypi.org/project/NsgOrcFx/),
[GitHub](https://github.com/NSG-Engenharia/NsgOrcFx)) by NSG Engenharia that wraps Orcina's
OrcaFlex API (`OrcFxAPI`). It adds:
* pre/post-processing tools: line selection, load case generation, reduced irregular-wave
  simulation time, modal and fatigue analysis, RAO plots, extreme constraint loads,
  vessel extreme responses, multi-thread simulation;
* IDE auto-complete and hints through the `data` attribute of the objects (`line.data.EndAConnection`).

Every original `OrcFxAPI` attribute and method must remain accessible in the same way:
`NsgOrcFx.Model` subclasses `OrcFxAPI.Model`, and `from OrcFxAPI import *` is re-exported.

**Users depend on the published results.** Any change must preserve previous results unless it is
an intentional correction.

> **Rule: run the regression tests (`py -m pytest`) before and after EVERY change to the package.**
> This includes small changes: one-line fixes, refactoring, renaming internals, changes to defaults,
> dependency or Python/OrcaFlex version bumps. The only exceptions are changes limited to
> documentation or comments.
> If the tests cannot run (e.g. no OrcaFlex licence, so they are skipped), the change is **not
> verified**. Say so explicitly. Do not report it as tested, commit it as verified, or release it.

## Repository layout

```
src/NsgOrcFx/           the package (setuptools, src layout)
  __init__.py           public API: `from .main import *`, FatigueAnalysis
  main.py               Model (subclass of OrcFxAPI.Model) and LineSelection; most public methods
  classes.py            object wrappers (OrcaFlexObject/Line/General/Environment) adding `.data`; Modes
  params.py             `data` attribute classes (auto-complete/hints); thin get/set proxies to OrcFxAPI
  auxfuncs.py           version checks, reduced simulation duration / largest rise-fall wave search
  loadcases.py          GenerateLoadCases implementation (+ `_CaseList.xlsx`)
  modal.py              modal shapes, normalization, stress shapes
  fatigue.py, sncurves.py  FatigueAnalysis wrapper, DNV S-N curves (only F3 seawater so far)
  raos.py               RAO plots (matplotlib); raos_old.py is legacy, not imported
  constraintloads.py    ExtremeLoadsFromConstraints (Excel/CSV output)
  multiproc.py          ProcMultiThread (threads running .dat -> .sim)
  vessel.py             ProcessExtremeResponses (spectral response -> Excel)
  environment.py        wave kinematics / drag coefficient helpers
  utils.py, constants.py, objauxfuncs.py, sortlines.py, weight.py, weightaux.py
tests/
  test*.py              EXAMPLE scripts (the README examples are based on them); not pytest tests
  tmptestfiles/         output folder of the example scripts (git-ignored)
  regression/           pytest regression suite + stored references  -> documentation/testing.md
documentation/
  testing.md            how the regression tests work, workflow, updating references
  images/               images used by README.md (linked by absolute GitHub URL)
README.md               shown on the PyPI page
pyproject.toml          package metadata, version, dependencies, pytest config
upload_production.py, upload_test.py   build + twine upload helpers
```

## Environment

* Windows only (OrcaFlex). Python launcher: `py`. OrcaFlex >= 11.3a is required at runtime
  (`requiredOrcFxVer` in main.py).
* Any `OrcFxAPI.Model()` needs an **OrcaFlex licence**. At NSG it comes from a network FlexNet
  server: in a sandboxed shell the licence request is blocked, and the server may have no
  free seats. Without a licence, the OrcaFlex-dependent tests are skipped (with the reason).
* Dev install: `py -m pip install -e .[test]`.

## Testing (mandatory for every change)

```
py -m pytest                    # regression tests: compare with tests/regression/references
py -m pytest -m "not slow"      # quick run
py -m pytest --run-examples     # + run every example script (before a release)
py -m pytest --update-refs -k X # regenerate references of selected tests (only for intended changes)
```

* Check that the summary shows **0 skipped** OrcaFlex tests. A skipped test proves nothing.
* A failing comparison means a result changed. Fix the code, unless the change is an intended
  correction. In that case regenerate only the affected references, review
  `git diff tests/regression/references`, and explain the change in the commit message.
* Never update references just to make tests pass. Never loosen tolerances in the code to hide a change.
* New feature → add a regression test `tests/regression/test_NN_<topic>.py` using the `ofx`,
  `workdir` and `reference` fixtures, plus preferably an example script `tests/testN_<topic>.py`
  and a README example.
* Full details: [documentation/testing.md](documentation/testing.md).

## Implementation guidelines

* **Backward compatibility of the public API**: do not rename or remove public functions, methods,
  parameters or change default values. Add new parameters at the end, with defaults that keep the old
  behaviour. If something must change, keep the old name as a deprecated alias.
* Naming follows the existing style: OrcFxAPI-like `PascalCase` for main model methods
  (`GenerateLoadCases`, `CalculateModal`, `ProcessExtremeResponses`), `camelCase` for helpers
  (`findLineByName`, `getAllLines`). Keep type hints and docstrings (they power the IDE hints,
  which are a feature of the package).
* `requires-python >= 3.8` is declared, but the code already uses `X | Y` annotations (with
  `from __future__ import annotations` in some modules). Do not use syntax newer than the
  versions the users actually run (3.10+) without discussing it.
* Functions that call OrcaFlex wave search or spectral response write **temporary files in the
  current working directory** (`utils.getAvailableFileName`). Keep them cleaned up (`os.remove`), and
  never assume the cwd is the repository.
* Do not print-and-swallow exceptions in new code. `raos.SaveFig` does this today; the tests
  check that the files exist for that reason.
* Excel output uses pandas → requires `openpyxl` (currently not listed in the package
  dependencies, only in the `test` extra).
* Source files use CRLF line endings. Keep them when editing.
* `__pycache__/*.pyc` files are tracked by git by mistake. Do not add more.

## README.md = PyPI page

* README changes are published with the next release. Keep it user-oriented (installation +
  examples). Development topics go in `documentation/`.
* Images and links must be **absolute GitHub URLs** (`https://github.com/NSG-Engenharia/NsgOrcFx/blob/main/...?raw=True`):
  relative links do not work on PyPI.
* Already-published PyPI versions link to files on the `main` branch. **Do not rename or move
  `documentation/` or `documentation/images/`**, or the images break on every published PyPI page.
* README code examples must run as written. Keep them in sync with the scripts in `tests/`.

## Release checklist

1. `py -m pytest --run-examples`: all pass, nothing skipped.
2. Bump `version` in `pyproject.toml`. `src/NsgOrcFx/__init__.py` has its own `__version__`, which is
   currently out of date. Keep both in sync.
3. `py -m build`, install the wheel in a clean venv, run `py -m pytest --installed`.
4. Upload with `upload_production.py` (twine). Use `upload_test.py` (TestPyPI) for trials.
5. Only publish after the user explicitly asks for it. Publishing to PyPI is irreversible for that version number.
