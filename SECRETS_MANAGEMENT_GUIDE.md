# Secrets Management Guide

**TL;DR**: Secrets stay local. GitHub never sees them.

---

## The Problem

If you commit `.env` or `credentials.json` to GitHub:
1. Everyone with repo access sees your broker credentials
2. If repo ever becomes public, attacker can trade with your account
3. Token theft = real money loss

---

## The Solution: .gitignore

### Step 1: Create `.gitignore` in repo root

```bash
# Create the file
cat > .gitignore << 'EOF'
# Secrets (NEVER commit)
.env
.env.local
.env.*.local
credentials.json
otp_response.txt
config.json

# Python
__pycache__/
*.py[cod]
*$py.class
*.so
.Python
build/
develop-eggs/
dist/
downloads/
eggs/
.eggs/
lib/
lib64/
parts/
sdist/
var/
wheels/
*.egg-info/
.installed.cfg
*.egg

# IDE
.vscode/
.idea/
*.swp
*.swo
*~

# Logs
logs/
*.log

# Data
data/
*.csv
*.xlsx
~$*.xlsx

# OS
.DS_Store
Thumbs.db

EOF
```

**This goes into GitHub.** Everyone sees it.

---

## Step 2: Create `.env.example` (Template)

This goes **IN GitHub** so people know what secrets they need.

```bash
# .env.example
API_KEY=your_mstock_api_key_here
API_SECRET=your_mstock_api_secret_here
CLIENT_CODE=your_client_code_here
PASSWORD=your_password_here
```

**Note**: Use placeholder values, NEVER real credentials.

---

## Step 3: Your Brother's Local Setup

**On his laptop** (NEVER commit this):

```bash
# Copy the example as a template
cp .env.example .env

# Edit with his real credentials
nano .env
# or
code .env
# or
vim .env
```

**File contents**:
```bash
API_KEY=abc123def456...  # His real key
API_SECRET=xyz789abc...  # His real secret
CLIENT_CODE=CLIENT001    # His real code
PASSWORD=hispassword     # His real password
```

**What happens**:
- `.env` is on his laptop only
- `.gitignore` tells git to ignore it
- He can run `git status` and `.env` won't show up
- If he accidentally tries `git add .`, `.env` is skipped

---

## Step 4: Verify Setup is Correct

```bash
# In the repo directory
git status

# Expected output:
# On branch main
# nothing to commit, working tree clean
# 
# .env should NOT be listed

# Try to add it explicitly
git add .env

# Expected output:
# The following paths are ignored by one of your .gitignore files:
#   .env
# Use -f if you really want to add them.

✅ SUCCESS - .env is protected
```

---

## Step 5: If Credentials.json is Auto-Generated

`credentials.json` is created by the bot at runtime (broker access token).

**Strategy**:
```bash
# In .gitignore:
credentials.json  # ✅ Already protected

# On first run, bot generates this automatically
# Brother never needs to commit it
# Git ignores it, so it won't accidentally leak
```

---

## Step 6: Config.json Strategy

`config.json` has trading settings (capital, daily loss limit, lot sizes).

**Two options**:

### Option A: Keep Local (Current)
```bash
# .gitignore
config.json  # Keep local, never commit

# Brother has his own config.json with his settings
# You/reviewer can see template in repo, but brother's personal config stays local
```

**Pros**: Each person can customize without pushing changes
**Cons**: If you make a template improvement, brother has to manually merge

### Option B: Template + Local Override
```bash
# In repo
config.json.example  # Template (committed)

# Brother's local
config.json          # His custom version (not committed, from .gitignore)

# On first run:
if not os.path.exists("config.json"):
    shutil.copy("config.json.example", "config.json")
    print("Created config.json from template. Edit with YOUR settings.")
```

**Pros**: Best practice; template is versioned, but personal configs are protected
**Cons**: Slightly more complex

---

## Step 7: Logs and Data

These are **local too**:

```bash
# .gitignore
logs/
data/
*.csv
*.xlsx
```

**Why**:
- Logs contain account metadata (order history, positions, capital)
- Data files have trading history (sensitive)
- Brother's P&L is private

---

## Security Checklist

Before pushing to GitHub:

```bash
# Check: Do NOT commit secrets
[ ] git diff --cached | grep -i "api_key\|password\|token\|secret"
    # Should return NOTHING

# Check: .gitignore protects secrets
[ ] git check-ignore .env
    # Should say: .env matched by pattern in .gitignore

# Check: .env.example has only placeholders (no real credentials)
[ ] grep -v "your_\|fake_\|placeholder" .env.example
    # Should return NOTHING (only placeholder content)

# Check: No credentials in code
[ ] grep -r "API_KEY\s*=" src/ | grep -v "os.environ"
    # Should return NOTHING (only env var references)

# Check: Credentials.json ignored
[ ] git check-ignore credentials.json
    # Should say: credentials.json matched by pattern in .gitignore

# Safe to push!
[ ] git push origin main
```

---

## What Happens If Brother Forgets and Commits .env?

**Recovery**:

```bash
# 1. Remove from git history (irreversible!)
git filter-branch --tree-filter 'rm -f .env' HEAD

# 2. Rotate credentials (they're now exposed in git history)
# Contact broker: "Reset my API key and token"

# 3. Never do this again:
- Add .env to .gitignore FIRST
- Use git hooks to prevent accidental commits (see below)
```

---

## Prevent Accidental Commits (Git Hooks)

Create a pre-commit hook that **blocks commits if secrets are detected**:

```bash
# .git/hooks/pre-commit
#!/bin/bash

# Check: Don't commit .env or credentials.json
FILES_NOT_ALLOWED=".env credentials.json config.json otp_response.txt"

for file in $FILES_NOT_ALLOWED; do
    if git diff --cached --name-only | grep -q "^$file$"; then
        echo "❌ ERROR: Cannot commit $file (contains secrets)"
        echo "Add to .gitignore and try again"
        exit 1
    fi
done

# Check: Don't commit real credentials in code
if git diff --cached | grep -E "API_KEY\s*[=:]\s*['\"]?[a-zA-Z0-9]{20,}"; then
    echo "❌ ERROR: Hardcoded credentials detected"
    echo "Use os.environ or .env instead"
    exit 1
fi

echo "✅ Pre-commit check passed"
exit 0
```

**Install hook**:
```bash
chmod +x .git/hooks/pre-commit

# Now every commit runs this check automatically
git commit -m "Fix something"
# Pre-commit hook runs and blocks if secrets detected
```

---

## Sharing Fixes with Brother (Workflow)

```bash
# 1. You/reviewer create a fix branch
git checkout -b fixes/order-rejection

# 2. Make changes, add tests
# (No secrets committed due to .gitignore)

# 3. Create PR
git push origin fixes/order-rejection

# 4. Brother reviews & approves

# 5. Merge to main
git checkout main
git merge fixes/order-rejection

# 6. Brother pulls latest
git pull origin main

# 7. Brother creates his .env locally (if not exists)
# .env is NOT in the repo, only .env.example
# He manually copies and edits:
cp .env.example .env
# Edit .env with HIS credentials (broker API key, etc.)

# 8. He runs tests
pytest tests/ -v

# 9. He runs the bot
python main.py

# His .env is never committed, never leaks
```

---

## Reference: Files That STAY LOCAL vs COMMITTED

| File | Local Only | Committed | Notes |
|------|-----------|-----------|-------|
| `.env` | ✅ | ❌ | Real credentials |
| `.env.example` | ❌ | ✅ | Template for others |
| `credentials.json` | ✅ | ❌ | Broker access token |
| `config.json` | ✅ | ❌ | Personal settings |
| `.gitignore` | ❌ | ✅ | Rules for all |
| `logs/` | ✅ | ❌ | Trading history |
| `data/` | ✅ | ❌ | Local positions/history |
| `src/` | ❌ | ✅ | Code |
| `tests/` | ❌ | ✅ | Tests |
| `.gitignore` | ❌ | ✅ | Security rules |

---

## Summary

✅ **Safe**:
- Brother's `.env` stays on his laptop only
- His `credentials.json` never touches GitHub
- His personal `config.json` is local
- `.gitignore` prevents accidental commits

✅ **Collaborative**:
- You/reviewer can see `.env.example` template
- You can improve it and brother pulls the update
- He never has to worry about his secrets leaking

✅ **Recoverable**:
- If bot crashes, his state files are in `data/` (local, backed up)
- Logs are local for debugging
- GitHub has only the code (shareable, reviewable)

**Result**: Brother can share his code with you for review, but you never see his actual credentials.
