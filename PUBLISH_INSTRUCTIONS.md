# Publishing Instructions

## Current Status

✅ Local Git repository initialized  
✅ All files committed (76 files)  
✅ Tag created: `engine_core_v0.1.0`  
✅ Branch: `main`

## Step 1: Create GitHub Repository

1. Go to https://github.com/new
2. **Repository name**: `crypto-perps-backtest-engine`
3. **Description**: `Strategy-agnostic crypto perps backtesting engine with realistic execution, risk controls, and validation harness.`
4. **Visibility**: **Public**
5. **Important**: Do NOT check "Add a README file", "Add .gitignore", or "Choose a license" (we already have these)
6. Click **"Create repository"**

## Step 2: Push to GitHub

After creating the repository, run one of the following:

### Option A: Use the PowerShell script

1. Edit `publish_to_github.ps1` and replace `YOUR_USERNAME` with your GitHub username
2. Run:
   ```powershell
   .\publish_to_github.ps1
   ```

### Option B: Manual commands

Replace `YOUR_USERNAME` with your GitHub username:

```powershell
cd C:\Users\Metin\Downloads\hand_off_pack_v2025-11-11\engine_core

# Add remote
git remote add origin https://github.com/YOUR_USERNAME/crypto-perps-backtest-engine.git

# Push main branch
git push -u origin main

# Push tags
git push origin --tags
```

## Step 3: Update pyproject.toml URLs

After pushing, update `pyproject.toml` to replace placeholder URLs:

```toml
[project.urls]
Homepage = "https://github.com/YOUR_USERNAME/crypto-perps-backtest-engine"
Documentation = "https://github.com/YOUR_USERNAME/crypto-perps-backtest-engine/docs"
Repository = "https://github.com/YOUR_USERNAME/crypto-perps-backtest-engine"
```

Then commit and push:
```powershell
git add pyproject.toml
git commit -m "docs: update repository URLs in pyproject.toml"
git push
```

## Verification

After publishing, verify the repository:
- ✅ README.md is visible at the root
- ✅ LICENSE file is present
- ✅ All directories (src/, config/, scripts/, tests/, docs/) are visible
- ✅ No artifacts/, runs/, or other temporary files are present
- ✅ Tag `engine_core_v0.1.0` is visible in releases/tags

## Test Fresh Clone (Optional)

To verify the repository works from a fresh clone:

```powershell
cd C:\Users\Metin\Downloads
git clone https://github.com/YOUR_USERNAME/crypto-perps-backtest-engine.git engine_core_test
cd engine_core_test
pip install -r requirements.txt
pip install -e .
pytest tests/ -q
python scripts/run_example_oracle.py
```

Expected results:
- ✅ All tests pass (56 passed, 6 skipped)
- ✅ Oracle example runs successfully

