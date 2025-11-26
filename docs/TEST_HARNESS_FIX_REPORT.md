# Test Harness Fix Report

**Date**: 2025-01-26  
**Commit**: `5503672ea5a0fc7fbf0b50deebc5dfb74967db8d` (frozen v1.0.0-engine-core)  
**Status**: ✅ **FIXED**

---

## Problem Summary

The `test_data_integrity_smoke.py` tests were failing with `ModuleNotFoundError: No module named 'engine_core'` when calling the `scripts/validate_data_integrity.py` script as a subprocess.

### Root Cause

1. The test called the script file directly via `subprocess.run([sys.executable, script_path, ...])`
2. When run as a subprocess, the script tried to import `engine_core.src.data.loader`
3. The import failed because the subprocess didn't have `engine_core` in its PYTHONPATH
4. The script's own `sys.path.insert(0, str(Path(__file__).resolve().parents[1]))` adds `engine_core/` to the path, but to import `engine_core` as a package, the **parent directory** of `engine_core/` must be in PYTHONPATH, not `engine_core/` itself

---

## Solution

Modified `tests/test_data_integrity_smoke.py` to set `PYTHONPATH` in the subprocess environment to include the parent directory of `engine_core/`, allowing the subprocess to import `engine_core` as a package.

### Changes Made

**File**: `tests/test_data_integrity_smoke.py`

1. **Added `os` import**: Required for `os.environ` and `os.pathsep`

2. **Updated `test_validation_pass()`**:
   - Set `PYTHONPATH` to the parent directory of `engine_core/` (not `engine_core/` itself)
   - Pass the environment to `subprocess.run()` via `env` parameter

3. **Updated `test_validation_fail()`**:
   - Same changes as above

### Code Changes

```python
# Before:
script_path = Path(__file__).parent.parent / "scripts" / "validate_data_integrity.py"
cmd = [sys.executable, str(script_path), ...]
result = subprocess.run(cmd, capture_output=True, text=True)

# After:
script_path = Path(__file__).parent.parent / "scripts" / "validate_data_integrity.py"
repo_root = Path(__file__).parent.parent  # This is engine_core/
repo_parent = repo_root.parent  # This is the parent directory containing engine_core/
env = os.environ.copy()
pythonpath = str(repo_parent)
if 'PYTHONPATH' in env:
    env['PYTHONPATH'] = pythonpath + os.pathsep + env['PYTHONPATH']
else:
    env['PYTHONPATH'] = pythonpath

cmd = [sys.executable, str(script_path), ...]
result = subprocess.run(cmd, capture_output=True, text=True, env=env)
```

---

## Verification

### Test Results

**Before fix**:
```
FAILED tests/test_data_integrity_smoke.py::TestDataIntegritySmoke::test_validation_pass
FAILED tests/test_data_integrity_smoke.py::TestDataIntegritySmoke::test_validation_fail
2 failed, 54 passed, 6 skipped
```

**After fix**:
```
PASSED tests/test_data_integrity_smoke.py::TestDataIntegritySmoke::test_validation_pass
PASSED tests/test_data_integrity_smoke.py::TestDataIntegritySmoke::test_validation_fail
56 passed, 6 skipped, 0 failed
```

### Full Test Suite

Running `pytest tests/ -q` now shows:
- ✅ **56 passed, 6 skipped, 0 failed**

All tests pass, confirming that:
1. The fix works correctly
2. No other tests were broken by the change
3. Engine behavior remains unchanged

---

## Engine Behavior Confirmation

✅ **No engine behavior was modified**

- Only the test harness was changed (`tests/test_data_integrity_smoke.py`)
- No changes to `src/` code
- No changes to script behavior (`scripts/validate_data_integrity.py`)
- No changes to public API
- No reintroduction of strategy-specific logic

The fix only affects how the test invokes the script as a subprocess, ensuring the subprocess can find the `engine_core` package in its PYTHONPATH.

---

## Technical Details

### Why Parent Directory?

The script imports `from engine_core.src.data.loader import DataLoader`. For Python to resolve `engine_core` as a package:

1. The directory containing `engine_core/` must be in `sys.path` (or PYTHONPATH)
2. `engine_core/` must have an `__init__.py` file (it does)
3. The import path `engine_core.src.data.loader` then resolves correctly

Setting PYTHONPATH to `engine_core/` itself would not work because Python would look for `engine_core/engine_core/`, which doesn't exist.

### Why Not Use `-m engine_core.scripts.validate_data_integrity`?

Initially attempted to call the script as a module using `python -m engine_core.scripts.validate_data_integrity`, but this requires the package to be properly installed via `pip install -e .`. The PYTHONPATH approach works regardless of installation status, making the tests more robust.

---

## Conclusion

The test harness has been fixed with minimal changes. The tests now pass consistently, and the engine behavior remains unchanged. The fix is robust and doesn't depend on package installation status or hardcoded paths.

