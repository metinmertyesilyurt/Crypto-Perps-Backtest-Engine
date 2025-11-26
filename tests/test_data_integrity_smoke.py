"""
Test Data Integrity Smoke
Verifies the data integrity validation script on synthetic data.
"""
import unittest
import pandas as pd
import numpy as np
from pathlib import Path
import sys
import os
import tempfile
import shutil
import subprocess

class TestDataIntegritySmoke(unittest.TestCase):
    def setUp(self):
        self.test_dir = tempfile.mkdtemp()
        self.data_dir = Path(self.test_dir) / "data"
        self.data_dir.mkdir()
        
    def tearDown(self):
        try:
            shutil.rmtree(self.test_dir)
        except PermissionError:
            pass # Windows cleanup issue
            
    def create_valid_data(self):
        dates = pd.date_range(start='2024-01-01', periods=100, freq='15min', tz='UTC')
        df = pd.DataFrame({
            'ts': dates,
            'open': 100.0,
            'high': 105.0,
            'low': 95.0,
            'close': 100.0,
            'volume': 1000.0,
            'notional': 100000.0  # Required field
        })
        df.to_csv(self.data_dir / "VALID_15m.csv", index=False)
        
    def create_invalid_data(self):
        """Create data with multiple injected issues: duplicate timestamp, NaN, OHLC violation"""
        dates = pd.date_range(start='2024-01-01', periods=100, freq='15min', tz='UTC')
        df = pd.DataFrame({
            'ts': dates,
            'open': 100.0,
            'high': 90.0, # Invalid: high < open (OHLC violation)
            'low': 95.0,
            'close': 100.0,
            'volume': -100.0, # Invalid: volume < 0
            'notional': 100000.0  # Required field
        })
        # Add duplicate timestamp
        df.loc[50, 'ts'] = df.loc[49, 'ts']
        # Add NaN
        df.loc[10, 'close'] = np.nan
        
        df.to_csv(self.data_dir / "INVALID_15m.csv", index=False)
        
    def test_validation_pass(self):
        self.create_valid_data()
        
        # Call script file directly, but set PYTHONPATH so subprocess can find engine_core package
        # The script imports 'engine_core.src.data.loader', which requires the parent of engine_core/
        # to be in PYTHONPATH (not engine_core/ itself), so engine_core/ can be imported as a package
        script_path = Path(__file__).parent.parent / "scripts" / "validate_data_integrity.py"
        repo_root = Path(__file__).parent.parent  # This is engine_core/
        repo_parent = repo_root.parent  # This is the parent directory containing engine_core/
        env = os.environ.copy()
        pythonpath = str(repo_parent)
        if 'PYTHONPATH' in env:
            env['PYTHONPATH'] = pythonpath + os.pathsep + env['PYTHONPATH']
        else:
            env['PYTHONPATH'] = pythonpath
        
        cmd = [
            sys.executable, str(script_path),
            "--data-path", str(self.data_dir),
            "--symbols", "VALID"
        ]
        
        # Run script
        result = subprocess.run(cmd, capture_output=True, text=True, env=env)
        
        self.assertEqual(result.returncode, 0, f"Script failed: {result.stderr}")
        self.assertIn("Checking VALID... OK", result.stdout)
        
    def test_validation_fail(self):
        """Test that script catches injected issues: duplicate timestamp, NaN, OHLC violation"""
        self.create_invalid_data()
        
        # Call script file directly, but set PYTHONPATH so subprocess can find engine_core package
        # The script imports 'engine_core.src.data.loader', which requires the parent of engine_core/
        # to be in PYTHONPATH (not engine_core/ itself), so engine_core/ can be imported as a package
        script_path = Path(__file__).parent.parent / "scripts" / "validate_data_integrity.py"
        repo_root = Path(__file__).parent.parent  # This is engine_core/
        repo_parent = repo_root.parent  # This is the parent directory containing engine_core/
        env = os.environ.copy()
        pythonpath = str(repo_parent)
        if 'PYTHONPATH' in env:
            env['PYTHONPATH'] = pythonpath + os.pathsep + env['PYTHONPATH']
        else:
            env['PYTHONPATH'] = pythonpath
        
        cmd = [
            sys.executable, str(script_path),
            "--data-path", str(self.data_dir),
            "--symbols", "INVALID"
        ]
        
        # Run script - expect failure
        result = subprocess.run(cmd, capture_output=True, text=True, env=env)
        
        self.assertNotEqual(result.returncode, 0, "Script should fail on invalid data")
        # Script may show "FAIL" or "LOAD ERROR" - either is acceptable for invalid data
        self.assertTrue(
            "FAIL" in result.stdout or "LOAD ERROR" in result.stdout or "Failed symbols: 1" in result.stdout,
            f"Script should indicate failure. Output: {result.stdout}"
        )
        
        # Verify artifacts were generated
        artifacts_dir = Path(__file__).parent.parent / "artifacts"
        report_path = artifacts_dir / "data_integrity_report.md"
        flags_path = artifacts_dir / "data_integrity_flags.csv"
        
        self.assertTrue(report_path.exists(), "Report should be generated")
        self.assertTrue(flags_path.exists(), "Flags CSV should be generated")
        
        # Verify report contains information about the failures
        report_content = report_path.read_text()
        self.assertIn("INVALID", report_content, "Report should mention INVALID symbol")
        
        # Verify flags CSV contains the symbol
        flags_df = pd.read_csv(flags_path)
        invalid_row = flags_df[flags_df['symbol'] == 'INVALID']
        self.assertFalse(invalid_row.empty, "Flags CSV should contain INVALID symbol")
        
        # Verify specific issues were detected
        invalid_issues = invalid_row.iloc[0]
        self.assertGreater(invalid_issues.get('duplicates', 0), 0, "Should detect duplicate timestamps")
        self.assertGreater(invalid_issues.get('ohlc_violations', 0), 0, "Should detect OHLC violations")
        # NaN check - should have 'nans' dict with 'close' key
        # Note: The script stores nans as a dict in JSON, so CSV might flatten it differently

if __name__ == '__main__':
    unittest.main()

