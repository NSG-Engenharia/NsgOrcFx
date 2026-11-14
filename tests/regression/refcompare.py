"""
Helpers to store and compare regression references.

Pure Python (pandas only): it does not import OrcFxAPI, so it can be tested
without an OrcaFlex licence (see `test_00_refcompare.py`).

Storage formats (text, so changes are reviewable in git diffs):
* tables / Excel sheets -> CSV "cell grid" (no header/index handling; every cell is compared)
* scalar values / lists -> JSON

Comparison rule for each cell/value:
* if both expected and actual parse as float -> math.isclose(actual, expected, rel_tol, abs_tol)
  (inf == inf, nan == nan)
* otherwise -> exact string equality (after stripping whitespace)
"""
from __future__ import annotations

import io
import json
import math
import os
from dataclasses import dataclass, field
from typing import Any

import pandas as pd

FLOAT_FORMAT = '%.17g'  # full double precision, so stored references are lossless
MAX_REPORTED_DIFFS = 25


# ---------------------------------------------------------------- cell level
def to_float(value: Any) -> float | None:
    """Return value as float if it represents a number, otherwise None."""
    if isinstance(value, bool):
        return None
    if isinstance(value, (int, float)):
        return float(value)
    if isinstance(value, str):
        s = value.strip()
        if s == '':
            return None
        try:
            return float(s)
        except ValueError:
            return None
    return None


def values_match(actual: Any, expected: Any, rtol: float, atol: float) -> bool:
    fa, fe = to_float(actual), to_float(expected)
    if fa is not None and fe is not None:
        if math.isnan(fa) or math.isnan(fe):
            return math.isnan(fa) and math.isnan(fe)
        return math.isclose(fa, fe, rel_tol=rtol, abs_tol=atol)
    return str(actual).strip() == str(expected).strip()


# ---------------------------------------------------------------- grid level
def frame_to_grid(df: pd.DataFrame, include_header: bool = True, include_index: bool = False) -> pd.DataFrame:
    """
    Serialize a DataFrame to CSV text and read it back as a grid of strings.
    Actual results and stored references go through the same path, so formatting is consistent.
    """
    text = df.to_csv(header=include_header, index=include_index, float_format=FLOAT_FORMAT, lineterminator='\n')
    return csv_text_to_grid(text)


def csv_text_to_grid(text: str) -> pd.DataFrame:
    if not text.strip():
        return pd.DataFrame()
    return pd.read_csv(io.StringIO(text), header=None, dtype=str, keep_default_na=False)


def grid_to_csv_text(grid: pd.DataFrame) -> str:
    return grid.to_csv(header=False, index=False, lineterminator='\n')


def excel_to_grids(path: str, sheets: list[str] | None = None) -> dict[str, pd.DataFrame]:
    """Read every (or the selected) sheet of an Excel file as raw cell grids (no header inference)."""
    raw = pd.read_excel(path, sheet_name=sheets if sheets else None, header=None)
    if isinstance(raw, pd.DataFrame):  # single sheet requested by name
        raw = {sheets[0]: raw}
    return {name: frame_to_grid(df, include_header=False) for name, df in raw.items()}


@dataclass
class Diff:
    location: str
    actual: Any
    expected: Any

    def __str__(self) -> str:
        fa, fe = to_float(self.actual), to_float(self.expected)
        extra = ''
        if fa is not None and fe is not None and fe != 0 and math.isfinite(fa) and math.isfinite(fe):
            extra = f'  (rel. diff {abs(fa - fe) / abs(fe):.3e})'
        return f'{self.location}: actual={self.actual!r} expected={self.expected!r}{extra}'


@dataclass
class CompareResult:
    diffs: list[Diff] = field(default_factory=list)
    structural: list[str] = field(default_factory=list)

    @property
    def ok(self) -> bool:
        return not self.diffs and not self.structural

    def report(self, title: str) -> str:
        lines = [f'{title}: regression mismatch']
        lines += [f'  * {s}' for s in self.structural]
        if self.diffs:
            lines.append(f'  {len(self.diffs)} differing value(s); first {min(len(self.diffs), MAX_REPORTED_DIFFS)}:')
            lines += [f'    - {d}' for d in self.diffs[:MAX_REPORTED_DIFFS]]
        return '\n'.join(lines)


def compare_grids(
        actual: pd.DataFrame,
        expected: pd.DataFrame,
        rtol: float,
        atol: float,
        numeric_only: bool = False,
        ) -> CompareResult:
    """
    Cell-by-cell comparison of two string grids.
    * numeric_only: compare only cells where both sides are numeric (used for cross-checks
      between runs that differ only in labels, e.g. 'N' vs 0 wave direction)
    """
    result = CompareResult()
    if actual.shape != expected.shape:
        result.structural.append(f'shape differs: actual {actual.shape} vs expected {expected.shape}')
    nrows = min(actual.shape[0], expected.shape[0])
    ncols = min(actual.shape[1], expected.shape[1])
    for i in range(nrows):
        for j in range(ncols):
            a, e = actual.iat[i, j], expected.iat[i, j]
            if numeric_only and (to_float(a) is None or to_float(e) is None):
                continue
            if not values_match(a, e, rtol, atol):
                result.diffs.append(Diff(f'row {i + 1}, col {j + 1}', a, e))
    return result


# --------------------------------------------------------------- value level
def normalize_values(obj: Any) -> Any:
    """Convert numpy scalars/arrays, tuples, etc. to JSON-friendly Python types."""
    try:
        import numpy as np
        if isinstance(obj, np.ndarray):
            return [normalize_values(v) for v in obj.tolist()]
        if isinstance(obj, np.generic):
            return normalize_values(obj.item())
    except ImportError:  # pragma: no cover
        pass
    if isinstance(obj, dict):
        return {str(k): normalize_values(v) for k, v in obj.items()}
    if isinstance(obj, (list, tuple)):
        return [normalize_values(v) for v in obj]
    if isinstance(obj, float) and not math.isfinite(obj):
        return repr(obj)  # 'inf', '-inf', 'nan' (JSON has no literal for them)
    return obj


def compare_values(actual: Any, expected: Any, rtol: float, atol: float, path: str = '$') -> CompareResult:
    result = CompareResult()
    if isinstance(expected, dict):
        if not isinstance(actual, dict):
            result.structural.append(f'{path}: expected a mapping, got {type(actual).__name__}')
            return result
        missing = sorted(set(expected) - set(actual))
        extra = sorted(set(actual) - set(expected))
        if missing:
            result.structural.append(f'{path}: missing keys {missing}')
        if extra:
            result.structural.append(f'{path}: unexpected new keys {extra}')
        for k in expected:
            if k in actual:
                sub = compare_values(actual[k], expected[k], rtol, atol, f'{path}.{k}')
                result.diffs += sub.diffs
                result.structural += sub.structural
    elif isinstance(expected, list):
        if not isinstance(actual, list):
            result.structural.append(f'{path}: expected a list, got {type(actual).__name__}')
            return result
        if len(actual) != len(expected):
            result.structural.append(f'{path}: length differs: actual {len(actual)} vs expected {len(expected)}')
        for i, (a, e) in enumerate(zip(actual, expected)):
            sub = compare_values(a, e, rtol, atol, f'{path}[{i}]')
            result.diffs += sub.diffs
            result.structural += sub.structural
    else:
        if not values_match(actual, expected, rtol, atol):
            result.diffs.append(Diff(path, actual, expected))
    return result


# ------------------------------------------------------------- the checker
class ReferenceMissing(Exception):
    pass


class RegressionMismatch(AssertionError):
    pass


class ReferenceChecker:
    """
    Bound to one test. Either compares results with stored references or (update mode)
    (re)writes them.

    * ref_dir: folder holding this test's reference files
    * actual_dir: where actual results are written when a comparison fails (for diffing)
    """

    def __init__(self, ref_dir: str, actual_dir: str, update: bool, rtol: float, atol: float):
        self.ref_dir = ref_dir
        self.actual_dir = actual_dir
        self.update = update
        self.rtol = rtol
        self.atol = atol
        self.written: list[str] = []

    # -- low level
    def _write(self, folder: str, filename: str, text: str) -> str:
        os.makedirs(folder, exist_ok=True)
        path = os.path.join(folder, filename)
        with open(path, 'w', encoding='utf-8', newline='\n') as f:
            f.write(text)
        return path

    def _read_reference(self, filename: str) -> str:
        path = os.path.join(self.ref_dir, filename)
        if not os.path.isfile(path):
            raise ReferenceMissing(
                f'Reference file not found: {path}\n'
                f'Generate it with: pytest --update-refs <this test>  (then review and commit it)')
        with open(path, encoding='utf-8') as f:
            return f.read()

    def _finish(self, result: CompareResult, filename: str, actual_text: str) -> None:
        if result.ok:
            return
        saved = self._write(self.actual_dir, filename, actual_text)
        raise RegressionMismatch(
            result.report(filename)
            + f'\n  actual result saved to: {saved}'
            + f'\n  reference file:         {os.path.join(self.ref_dir, filename)}')

    # -- public API
    def check_grid(self, name: str, grid: pd.DataFrame, rtol: float | None = None, atol: float | None = None) -> None:
        filename = f'{name}.csv'
        text = grid_to_csv_text(grid)
        if self.update:
            self.written.append(self._write(self.ref_dir, filename, text))
            return
        expected = csv_text_to_grid(self._read_reference(filename))
        actual = csv_text_to_grid(text)  # round trip, identical to how the reference was produced
        result = compare_grids(actual, expected, self.rtol if rtol is None else rtol, self.atol if atol is None else atol)
        self._finish(result, filename, text)

    def check_table(self, name: str, df: pd.DataFrame, include_index: bool = False,
                    rtol: float | None = None, atol: float | None = None) -> None:
        """Compare a DataFrame (header + values) with the reference `<name>.csv`."""
        self.check_grid(name, frame_to_grid(df, include_header=True, include_index=include_index), rtol, atol)

    def check_excel(self, name: str, path: str, sheets: list[str] | None = None,
                    rtol: float | None = None, atol: float | None = None) -> None:
        """Compare every (or selected) sheet of an Excel file; one reference CSV per sheet: `<name>__<sheet>.csv`."""
        grids = excel_to_grids(path, sheets)
        sheet_list_name = f'{name}__sheets'
        self.check_values(sheet_list_name, {'sheets': list(grids.keys())})
        for sheet, grid in grids.items():
            self.check_grid(f'{name}__{_safe(sheet)}', grid, rtol, atol)

    def check_values(self, name: str, values: Any, rtol: float | None = None, atol: float | None = None) -> None:
        """Compare JSON-serializable values (dict/list/scalars, numpy allowed) with `<name>.json`."""
        filename = f'{name}.json'
        values = normalize_values(values)
        text = json.dumps(values, indent=2, ensure_ascii=False) + '\n'
        if self.update:
            self.written.append(self._write(self.ref_dir, filename, text))
            return
        expected = json.loads(self._read_reference(filename))
        result = compare_values(values, expected, self.rtol if rtol is None else rtol, self.atol if atol is None else atol)
        self._finish(result, filename, text)


def _safe(name: str) -> str:
    """File-system safe version of a name (sheet or test id)."""
    out = ''.join(c if (c.isalnum() or c in '-_.') else '_' for c in str(name))
    return out.strip('_') or 'unnamed'


safe_name = _safe
