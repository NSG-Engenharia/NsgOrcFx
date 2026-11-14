"""
Pytest configuration for the NsgOrcFx regression tests.

See documentation/testing.md for the full description. Quick reference:

    py -m pytest                          # compare with stored references
    py -m pytest -m "not slow"            # skip the slow tests (e.g. simulations)
    py -m pytest --update-refs -k modal   # (re)generate references of the selected tests
    py -m pytest --run-examples           # also run the example scripts tests/test*.py
    py -m pytest --installed              # test the installed package instead of ./src
"""
from __future__ import annotations

import datetime
import json
import os
import platform
import sys

os.environ.setdefault('MPLBACKEND', 'Agg')  # no GUI windows from matplotlib during tests

import pytest

HERE = os.path.dirname(os.path.abspath(__file__))
REPO_ROOT = os.path.dirname(os.path.dirname(HERE))
SRC_DIR = os.path.join(REPO_ROOT, 'src')
REFERENCES_DIR = os.path.join(HERE, 'references')
ACTUAL_DIR = os.path.join(HERE, '_actual')  # git-ignored; actual results of failing comparisons
METADATA_FILE = os.path.join(REFERENCES_DIR, '_metadata.json')

DEFAULT_RTOL = 1e-6
DEFAULT_ATOL = 1e-9

sys.path.insert(0, HERE)  # make `refcompare` importable from the test modules
import refcompare  # noqa: E402


# ------------------------------------------------------------------ options
def pytest_addoption(parser):
    group = parser.getgroup('nsgorcfx', 'NsgOrcFx regression tests')
    group.addoption('--update-refs', action='store_true', default=False,
                    help='Write the current results as the new references instead of comparing.')
    group.addoption('--installed', action='store_true', default=False,
                    help='Test the installed NsgOrcFx package instead of the local ./src folder.')
    group.addoption('--run-examples', action='store_true', default=False,
                    help='Also run the example scripts tests/test*.py (smoke test, slow).')
    group.addoption('--rtol', type=float, default=DEFAULT_RTOL,
                    help=f'Relative tolerance for numeric comparisons (default {DEFAULT_RTOL}).')
    group.addoption('--atol', type=float, default=DEFAULT_ATOL,
                    help=f'Absolute tolerance for numeric comparisons (default {DEFAULT_ATOL}).')


def pytest_configure(config):
    if not config.getoption('--installed'):
        sys.path.insert(0, SRC_DIR)  # `import NsgOrcFx` -> ./src/NsgOrcFx
    config.addinivalue_line('markers', 'slow: long running test (e.g. runs OrcaFlex simulations)')
    config.addinivalue_line('markers', 'examples: runs the example scripts in tests/ (needs --run-examples)')


def pytest_collection_modifyitems(config, items):
    if config.getoption('--run-examples'):
        return
    skip = pytest.mark.skip(reason='example scripts run only with --run-examples')
    for item in items:
        if 'examples' in item.keywords:
            item.add_marker(skip)


# ----------------------------------------------------------------- fixtures
@pytest.fixture(scope='session')
def ofx(pytestconfig):
    """
    The NsgOrcFx package under test (local ./src unless --installed).
    Skips the test when OrcFxAPI cannot be imported or no OrcaFlex licence is available.
    """
    try:
        import NsgOrcFx
    except ImportError as err:
        pytest.skip(f'NsgOrcFx/OrcFxAPI could not be imported: {err}')

    pkg_file = os.path.abspath(NsgOrcFx.__file__)
    if not pytestconfig.getoption('--installed'):
        assert pkg_file.startswith(os.path.abspath(SRC_DIR)), (
            f'Expected NsgOrcFx from {SRC_DIR}, but imported {pkg_file}. '
            'Use --installed to test the installed package on purpose.')

    try:
        NsgOrcFx.Model()  # requires a licence
    except Exception as err:  # OrcFxAPI.DLLError when the licence is not available
        msg = ' | '.join(ln.strip() for ln in str(err).splitlines() if ln.strip())
        pytest.skip(f'OrcaFlex licence not available: {msg[:300]}')

    return NsgOrcFx


@pytest.fixture
def workdir(tmp_path, monkeypatch):
    """
    Temporary working folder (also set as current dir), because some package functions
    write temporary files to the current folder (wave search, spectral response).
    """
    monkeypatch.chdir(tmp_path)
    return tmp_path


@pytest.fixture
def reference(request) -> refcompare.ReferenceChecker:
    """Reference checker bound to the current test: references/<module>/<test id>/"""
    module = request.node.module.__name__.split('.')[-1]
    test_id = refcompare.safe_name(request.node.name)
    sub = os.path.join(module, test_id)
    checker = refcompare.ReferenceChecker(
        ref_dir=os.path.join(REFERENCES_DIR, sub),
        actual_dir=os.path.join(ACTUAL_DIR, sub),
        update=request.config.getoption('--update-refs'),
        rtol=request.config.getoption('--rtol'),
        atol=request.config.getoption('--atol'),
    )
    yield checker
    if checker.written:
        request.config._nsg_refs_written = getattr(request.config, '_nsg_refs_written', 0) + len(checker.written)


# --------------------------------------------------- environment / metadata
def current_environment() -> dict:
    env = {
        'python': platform.python_version(),
        'platform': platform.platform(),
    }
    for mod in ('numpy', 'pandas', 'scipy', 'matplotlib', 'openpyxl'):
        try:
            env[mod] = __import__(mod).__version__
        except Exception:
            env[mod] = None
    try:
        import OrcFxAPI
        env['OrcFxAPI'] = getattr(OrcFxAPI, '__version__', None)
        env['OrcaFlex DLL'] = OrcFxAPI.DLLVersion()
    except Exception:
        env['OrcFxAPI'] = env['OrcaFlex DLL'] = None
    try:
        import tomllib
        with open(os.path.join(REPO_ROOT, 'pyproject.toml'), 'rb') as f:
            env['NsgOrcFx (pyproject)'] = tomllib.load(f)['project']['version']
    except Exception:
        env['NsgOrcFx (pyproject)'] = None
    return env


def pytest_sessionfinish(session, exitstatus):
    if getattr(session.config, '_nsg_refs_written', 0):
        meta = current_environment()
        meta['generated'] = datetime.datetime.now().isoformat(timespec='seconds')
        os.makedirs(REFERENCES_DIR, exist_ok=True)
        with open(METADATA_FILE, 'w', encoding='utf-8', newline='\n') as f:
            json.dump(meta, f, indent=2)
            f.write('\n')


def pytest_terminal_summary(terminalreporter, exitstatus, config):
    written = getattr(config, '_nsg_refs_written', 0)
    if written:
        terminalreporter.write_sep('=', f'{written} reference file(s) written to {REFERENCES_DIR}', yellow=True)
        terminalreporter.write_line('Review the changes with `git diff tests/regression/references` before committing.')
        return
    if not os.path.isfile(METADATA_FILE):
        return
    with open(METADATA_FILE, encoding='utf-8') as f:
        ref_meta = json.load(f)
    cur = current_environment()
    keys = ('OrcaFlex DLL', 'OrcFxAPI', 'python', 'numpy', 'pandas')
    changed = [k for k in keys if ref_meta.get(k) != cur.get(k)]
    if changed:
        terminalreporter.write_sep('-', 'environment differs from the one used to generate the references')
        for k in changed:
            terminalreporter.write_line(f'  {k}: reference={ref_meta.get(k)}  current={cur.get(k)}')
        terminalreporter.write_line('  Small numeric differences may come from this (see documentation/testing.md).')
