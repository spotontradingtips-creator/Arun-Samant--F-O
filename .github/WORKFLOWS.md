# GitHub Actions Workflows

This project uses automated CI/CD pipelines to ensure code quality, security, and reliability. All workflows run automatically on push and pull requests.

## Workflows Overview

### 1. **CI - Test, Lint & Security** (`ci.yml`)

Main continuous integration pipeline that runs on every push and PR.

**Triggers:**
- Push to `main`, `master`, `develop`
- Pull requests to `main`, `master`, `develop`

**Jobs:**

#### Test Job
- Runs pytest on Python 3.11
- Generates coverage reports
- Uploads to Codecov
- **Requirements:** Tests must pass, coverage tracked

```bash
pytest tests/ --cov=src --cov=monitoring --timeout=30
```

#### Lint Job
- **Black:** Code formatting check
- **isort:** Import sorting validation
- **flake8:** Code style and complexity analysis
- Continues on failure (warnings only)

#### Security Job
- **Bandit:** Scans for common security issues in Python code
- **Safety:** Checks for known vulnerabilities in dependencies
- **Secret Detection:** Scans for hardcoded credentials
- ⚠️ Fails if hardcoded secrets found (CRITICAL)

#### Config Validation Job
- Validates `config.json` JSON structure
- Checks for required configuration keys:
  - `live_trading`
  - `max_loss_per_day`

**Success Criteria:**
- ✅ All tests pass
- ✅ No hardcoded secrets
- ✅ Config is valid

---

### 2. **Paper Mode Validation** (`paper-mode-validation.yml`)

Validates trading logic in paper mode (no real money).

**Triggers:**
- Automatically on `main`/`master` when `src/`, `main.py`, or `tests/` changes
- Can be manually triggered with "Run workflow" button

**Jobs:**

#### Paper Mode Test
1. Prepares config with `live_trading=false` and `paper_trading=true`
2. Runs critical bugs validation tests
3. Validates trading logic
4. Generates validation report

**Important:** This ensures:
- ✅ Live trading is disabled
- ✅ Paper trading is enabled
- ✅ All trading logic works in paper mode

**Artifacts Generated:**
- `paper-mode-validation-report.md` - Test results summary

**Manual Trigger:**
Go to "Actions" tab → "Paper Mode Validation" → "Run workflow"

---

### 3. **Dependency & Vulnerability Check** (`dependency-check.yml`)

Monitors dependencies for security vulnerabilities and license compliance.

**Triggers:**
- When `requirements.txt` changes
- Weekly on Monday at 2 AM UTC (scheduled)
- Manual trigger available

**Jobs:**

#### Dependency Check
- **Safety:** Scans for known CVEs
- **pip-audit:** Detailed dependency vulnerability audit
- Generates JSON and markdown reports

#### License Check
- Generates license report for all dependencies
- Warns if GPL/AGPL licenses detected
- Ensures compliance with your license terms

**Artifacts Generated:**
- `safety-report.json` - Vulnerability data
- `pip-audit-report.md` - Detailed audit
- `dependencies.txt` - Full dependency list
- `licenses.md` - License compliance report

---

## How to Use

### View Workflow Results

1. Go to your GitHub repository
2. Click **"Actions"** tab
3. Select a workflow to see:
   - ✅ Successful runs
   - ❌ Failed runs
   - Logs with detailed error messages
   - Artifacts (reports, coverage, etc.)

### Manually Trigger a Workflow

1. Go to **Actions** tab
2. Select the workflow
3. Click **"Run workflow"** button
4. Choose branch (usually `main`)
5. Click **"Run workflow"**

### Fix CI Failures

**Tests Failed:**
```bash
# Run tests locally
pytest tests/ -v

# Run specific test
pytest tests/test_critical_bugs.py -v
```

**Linting Issues:**
```bash
# Format code with Black
black src/ tests/ main.py

# Fix import order with isort
isort src/ tests/ main.py

# Check flake8 violations
flake8 src/ main.py --max-line-length=120
```

**Security Issues:**
```bash
# Find security issues
bandit -r src/ main.py

# Check for hardcoded secrets
grep -r "password\|secret\|api_key" src/ main.py
```

**Config Issues:**
```bash
# Validate JSON
python -c "import json; json.load(open('config.json'))"

# Check required keys
python -c "import json; config = json.load(open('config.json')); print(config.get('live_trading'))"
```

---

## Environment Variables & Secrets

For workflows that need credentials (future enhancement):

1. Go to **Settings** → **Secrets and variables** → **Actions**
2. Click **"New repository secret"**
3. Add secret (e.g., `MSTOCK_API_KEY`)
4. Use in workflow:
   ```yaml
   env:
     MSTOCK_API_KEY: ${{ secrets.MSTOCK_API_KEY }}
   ```

---

## Status Badge

Add this to your `README.md` to show CI status:

```markdown
[![CI Status](https://github.com/YOUR_USERNAME/YOUR_REPO/actions/workflows/ci.yml/badge.svg)](https://github.com/YOUR_USERNAME/YOUR_REPO/actions)
```

---

## Common Issues & Solutions

### Issue: "Tests Failed"
```bash
# Check what's failing
pytest tests/ -v --tb=short

# Run with more timeout if bot needs setup
pytest tests/ --timeout=60 -v
```

### Issue: "Hardcoded Secrets Detected"
**This FAILS the build intentionally.** Remove any:
- API keys
- Passwords
- Tokens
- Private keys

Use environment variables instead:
```python
import os
api_key = os.getenv('MSTOCK_API_KEY')
```

### Issue: "Paper Mode Config Not Applied"
The workflow automatically sets:
- `live_trading = false`
- `paper_trading = true`

Verify locally:
```bash
python -c "import json; config = json.load(open('config.json')); print('Live:', config.get('live_trading'), 'Paper:', config.get('paper_trading'))"
```

### Issue: "Dependencies have vulnerabilities"
```bash
# Check what's vulnerable
safety check

# Audit dependencies
pip-audit --desc

# Update if possible
pip install --upgrade <package_name>
```

---

## Best Practices

✅ **DO:**
- Check CI results before merging PRs
- Fix failing tests before pushing more code
- Keep `requirements.txt` updated
- Review security reports weekly
- Run tests locally before pushing: `pytest tests/ -v`

❌ **DON'T:**
- Hardcode secrets or credentials
- Push to `main` without CI passing
- Ignore security warnings
- Skip tests with unreviewed changes

---

## Testing Locally Before Push

Run everything locally to avoid CI failures:

```bash
# Install dependencies
pip install -r requirements.txt
pip install pytest black isort flake8 bandit safety

# Run tests
pytest tests/ -v --cov=src

# Format code
black src/ tests/ main.py
isort src/ tests/ main.py

# Check security
bandit -r src/ main.py
safety check

# Validate config
python -c "import json; json.load(open('config.json'))"
```

---

## Contact & Support

For workflow issues:
- Check GitHub Actions logs for detailed error messages
- Review the relevant workflow file (`.github/workflows/*.yml`)
- Contact the maintainer with the error logs

---

**Last Updated:** 2026-06-23
**Python Version:** 3.11
**Status:** ✅ All workflows operational
