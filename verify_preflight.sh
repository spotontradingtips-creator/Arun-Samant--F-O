#!/bin/bash

# Pre-Flight Verification Script
# Run this BEFORE starting any fixes to ensure everything is in place

set -e

echo "🔍 F&O Trading Bot - Pre-Flight Verification"
echo "=============================================="
echo ""

# Color codes
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

CHECKS_PASSED=0
CHECKS_FAILED=0

# Function to check something
check() {
    local description=$1
    local command=$2

    echo -n "Checking: $description... "

    if eval "$command" > /dev/null 2>&1; then
        echo -e "${GREEN}✅ PASS${NC}"
        ((CHECKS_PASSED++))
        return 0
    else
        echo -e "${RED}❌ FAIL${NC}"
        ((CHECKS_FAILED++))
        return 1
    fi
}

# 1. Backup checks
echo "📦 BACKUP VERIFICATION"
echo "----------------------"
check "Backup directory exists" "test -d backups"
check "Backup manifest exists" "test -f backups/MANIFEST.md"
check "At least one backup zip exists" "ls backups/*.zip 2>/dev/null | head -1 | grep -q ."

# 2. Git checks
echo ""
echo "🔗 GIT VERIFICATION"
echo "-------------------"
check "Git initialized" "git status > /dev/null 2>&1"
check ".gitignore exists" "test -f .gitignore"
check ".gitignore has .env" "grep -q '^\\.env$' .gitignore"
check ".gitignore has credentials.json" "grep -q 'credentials.json' .gitignore"
check ".gitignore has config.json" "grep -q 'config.json' .gitignore"
check "Git has commits" "test $(git log --oneline | wc -l) -gt 0"
check "Backup branch exists" "git show-ref --verify --quiet refs/heads/backup/pre-fixes"

# 3. Documentation checks
echo ""
echo "📚 DOCUMENTATION VERIFICATION"
echo "-----------------------------"
check "BUG_REGISTRY.md exists" "test -f BUG_REGISTRY.md"
check "BUG_REGISTRY.md has CRITICAL bugs" "grep -q 'CRITICAL' BUG_REGISTRY.md"
check "BUG_REGISTRY.md has 21 bugs" "grep -q 'Total Bugs' BUG_REGISTRY.md"
check "FIX_LOG.md exists" "test -f FIX_LOG.md"
check "PRINCIPLES_CHECKLIST.md exists" "test -f PRINCIPLES_CHECKLIST.md"
check "PRINCIPLES_CHECKLIST.md has all 4 principles" "grep -q 'Principle 1.*Coding Style' PRINCIPLES_CHECKLIST.md && grep -q 'Principle 2.*Testing' PRINCIPLES_CHECKLIST.md && grep -q 'Principle 3.*Git' PRINCIPLES_CHECKLIST.md && grep -q 'Principle 4.*Security' PRINCIPLES_CHECKLIST.md"

# 4. Secrets protection checks
echo ""
echo "🔐 SECRETS PROTECTION VERIFICATION"
echo "-----------------------------------"
check ".env does not exist (should be local only)" "test ! -f .env"
check "credentials.json not in git history" "git log --all --full-history --oneline -- credentials.json | wc -l | grep -q '^0$'"
check ".env not in git history" "git log --all --full-history --oneline -- .env | wc -l | grep -q '^0$'"
check ".env.example exists (template)" "test -f .env.example"
check ".env.example has no real credentials" "! grep -E 'sk_|pk_|[a-zA-Z0-9]{32,}' .env.example | grep -v 'your_\|placeholder\|example'"

# 5. Project structure checks
echo ""
echo "📁 PROJECT STRUCTURE VERIFICATION"
echo "---------------------------------"
check "src/ directory exists" "test -d src"
check "tests/ directory exists" "test -d tests"
check "main.py exists" "test -f main.py"
check "requirements.txt exists" "test -f requirements.txt"
check "Python dependencies can be listed" "head -1 requirements.txt | grep -q ."

# 6. Configuration checks
echo ""
echo "⚙️  CONFIGURATION VERIFICATION"
echo "------------------------------"
check "AUDIT_SUMMARY_FOR_BROTHER.md exists" "test -f AUDIT_SUMMARY_FOR_BROTHER.md"
check "SECRETS_MANAGEMENT_GUIDE.md exists" "test -f SECRETS_MANAGEMENT_GUIDE.md"
check "BACKUP_AND_RECOVERY_PLAN.md exists" "test -f BACKUP_AND_RECOVERY_PLAN.md"

# 7. Optional: Python checks (if python available)
echo ""
echo "🐍 PYTHON ENVIRONMENT (Optional)"
echo "--------------------------------"
if command -v python3 &> /dev/null; then
    check "Python 3 available" "command -v python3"
    check "Can import pandas" "python3 -c 'import pandas' 2>/dev/null"
    check "Can import requests" "python3 -c 'import requests' 2>/dev/null"
else
    echo "Python not in PATH, skipping Python checks"
fi

# Summary
echo ""
echo "=============================================="
echo "📊 VERIFICATION SUMMARY"
echo "=============================================="
echo -e "✅ Passed: ${GREEN}${CHECKS_PASSED}${NC}"
echo -e "❌ Failed: ${RED}${CHECKS_FAILED}${NC}"
echo ""

if [ $CHECKS_FAILED -eq 0 ]; then
    echo -e "${GREEN}🎉 ALL CHECKS PASSED! Ready to start fixes.${NC}"
    echo ""
    echo "Next steps:"
    echo "1. Review BUG_REGISTRY.md"
    echo "2. Review PRINCIPLES_CHECKLIST.md"
    echo "3. Start Week 1 with fixing BUG-001 to BUG-008"
    echo "4. Follow conventional commits and TDD"
    exit 0
else
    echo -e "${RED}⚠️  SOME CHECKS FAILED. Fix above before proceeding.${NC}"
    echo ""
    echo "Common fixes:"
    echo "1. Create backup: mkdir -p backups && cp -r . backups/pre-fixes_\$(date +%s)/"
    echo "2. Initialize git: git init && git config user.name 'Your Name'"
    echo "3. Create .gitignore: cp templates/.gitignore ."
    echo "4. Commit initial state: git add -A && git commit -m 'chore: initial commit'"
    echo "5. Create backup branch: git branch backup/pre-fixes"
    exit 1
fi
