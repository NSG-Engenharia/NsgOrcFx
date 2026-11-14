"""
Smoke test: runs every example script tests/test*.py exactly as a user would
(they are the source of the README examples) and checks it finishes without error.

Opt-in (slow): py -m pytest --run-examples -m examples

Each script runs in an isolated temporary working folder (the scripts write to
relative paths such as `tests\\tmptestfiles` and `.`), so nothing is written to the repository.
Outputs are not compared here; the numeric regression is done by the test_0*.py modules.
"""
import os
import subprocess
import sys

import pytest

EXAMPLES_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))  # tests/
EXCLUDED = {
    'test8_HsTp-wave-selection_old.py',  # legacy script, depends on a local model file
}
EXAMPLES = sorted(
    f for f in os.listdir(EXAMPLES_DIR)
    if f.startswith('test') and f.endswith('.py') and f not in EXCLUDED
)
TIMEOUT = 1800  # seconds per script


@pytest.mark.examples
@pytest.mark.slow
@pytest.mark.parametrize('script', EXAMPLES)
def test_example_script_runs(ofx, tmp_path, script):
    (tmp_path / 'tests' / 'tmptestfiles').mkdir(parents=True)
    env = dict(os.environ, MPLBACKEND='Agg')
    proc = subprocess.run(
        [sys.executable, os.path.join(EXAMPLES_DIR, script)],
        cwd=tmp_path, env=env, capture_output=True, text=True, timeout=TIMEOUT,
    )
    assert proc.returncode == 0, (
        f'{script} failed (exit code {proc.returncode})\n'
        f'--- stdout (tail) ---\n{proc.stdout[-3000:]}\n--- stderr (tail) ---\n{proc.stderr[-3000:]}')
