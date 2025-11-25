# Publish engine_core to GitHub
# 
# Prerequisites:
# 1. Create a new GitHub repository named "crypto-perps-backtest-engine" at https://github.com/new
#    - Description: "Strategy-agnostic crypto perps backtesting engine with realistic execution, risk controls, and validation harness."
#    - Visibility: Public
#    - Do NOT initialize with README, .gitignore, or license (we already have them)
# 2. Replace YOUR_USERNAME below with your GitHub username
#
# Then run this script from the engine_core directory

$GITHUB_USERNAME = "YOUR_USERNAME"  # Replace with your GitHub username
$REPO_NAME = "crypto-perps-backtest-engine"

Write-Host "Setting up remote and pushing to GitHub..." -ForegroundColor Green

# Add remote (replace YOUR_USERNAME with your actual GitHub username)
git remote add origin "https://github.com/$GITHUB_USERNAME/$REPO_NAME.git"

# Push main branch
Write-Host "Pushing main branch..." -ForegroundColor Yellow
git push -u origin main

# Push tags
Write-Host "Pushing tags..." -ForegroundColor Yellow
git push origin --tags

Write-Host "`nDone! Repository is now available at:" -ForegroundColor Green
Write-Host "https://github.com/$GITHUB_USERNAME/$REPO_NAME" -ForegroundColor Cyan

Write-Host "`nNext steps:" -ForegroundColor Yellow
Write-Host "1. Update pyproject.toml URLs with your actual repository URL"
Write-Host "2. Commit and push the pyproject.toml update"

