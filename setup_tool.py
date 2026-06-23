#!/usr/bin/env python3
"""
Setup Tool for F&O Trading Bot
Validates environment, dependencies, and credentials
"""

import os
import sys
import json
from pathlib import Path
from dotenv import load_dotenv

def check_python_version():
    """Check if Python version is 3.9+"""
    if sys.version_info < (3, 9):
        print(f"[FAIL] Python 3.9+ required. You have {sys.version_info.major}.{sys.version_info.minor}")
        return False
    print(f"[OK] Python version: {sys.version_info.major}.{sys.version_info.minor}")
    return True

def check_dependencies():
    """Check if all required packages are installed"""
    required = {
        'pandas': 'pandas',
        'numpy': 'numpy',
        'requests': 'requests',
        'python-dotenv': 'dotenv',
        'pytz': 'pytz',
        'streamlit': 'streamlit',
        'rich': 'rich',
        'fastapi': 'fastapi',
        'uvicorn': 'uvicorn',
        'websockets': 'websockets'
    }

    missing = []
    for package_name, import_name in required.items():
        try:
            __import__(import_name)
        except ImportError:
            missing.append(package_name)

    if missing:
        print(f"[FAIL] Missing packages: {', '.join(missing)}")
        print(f"   Run: pip install {' '.join(missing)}")
        return False

    print(f"[OK] All {len(required.keys())} dependencies installed")
    return True

def check_config():
    """Verify config.json is valid"""
    config_path = Path("config.json")
    if not config_path.exists():
        print("[FAIL] config.json not found")
        return False

    try:
        with open(config_path, 'r', encoding='utf-8') as f:
            config = json.load(f)
        print("[OK] config.json is valid")

        # Show current mode
        mode = "PAPER MODE" if not config.get('trading_mode', {}).get('live_trading') else "LIVE MODE"
        capital = config.get('capital', {}).get('initial_capital', 'N/A')
        print(f"   Mode: {mode} | Capital: Rs {capital}")
        return True
    except json.JSONDecodeError as e:
        print(f"[FAIL] config.json is invalid: {e}")
        return False

def check_credentials():
    """Check if credentials are set up"""
    env_file = Path(".env")
    if not env_file.exists():
        print("[WARN] .env file not found (optional for paper mode)")
        print("   For live trading, create .env with:")
        print("   - FINVESMART_API_KEY=your_key")
        print("   - FINVESMART_API_SECRET=your_secret")
        return True

    load_dotenv()

    required_vars = ['FINVESMART_API_KEY', 'FINVESMART_API_SECRET']
    missing = [var for var in required_vars if not os.getenv(var)]

    if missing:
        print(f"[WARN] Missing credentials: {', '.join(missing)}")
        return False

    print("[OK] Credentials configured (.env found)")
    return True

def check_directories():
    """Create required directories"""
    dirs = ['logs', 'data', 'cache']
    for dir_name in dirs:
        dir_path = Path(dir_name)
        dir_path.mkdir(exist_ok=True)

    print(f"[OK] Directories ready: {', '.join(dirs)}")
    return True

def check_gitignore():
    """Verify .gitignore is protecting sensitive files"""
    gitignore_path = Path(".gitignore")
    if not gitignore_path.exists():
        print("[WARN] .gitignore not found")
        return False

    with open(gitignore_path, 'r') as f:
        content = f.read()

    required_patterns = ['.env', '__pycache__', '*.log', 'logs/', 'cache/', '.DS_Store']
    missing = [p for p in required_patterns if p not in content]

    if missing:
        print(f"[WARN] .gitignore missing patterns: {missing}")
        return False

    print("[OK] .gitignore properly configured")
    return True

def main():
    """Run all checks"""
    print("\n" + "="*60)
    print("[BOT] F&O TRADING BOT - SETUP VALIDATION")
    print("="*60 + "\n")

    checks = [
        ("Python Version", check_python_version),
        ("Dependencies", check_dependencies),
        ("Configuration", check_config),
        ("Credentials", check_credentials),
        ("Directories", check_directories),
        (".gitignore Security", check_gitignore),
    ]

    results = []
    for name, check_fn in checks:
        print(f"\n[CHECK] {name}...")
        try:
            result = check_fn()
            results.append((name, result))
        except Exception as e:
            print(f"[ERROR] {e}")
            results.append((name, False))

    print("\n" + "="*60)
    print("SUMMARY")
    print("="*60)

    passed = sum(1 for _, result in results if result)
    total = len(results)

    for name, result in results:
        status = "[OK]" if result else "[FAIL]"
        print(f"{status} {name}")

    print(f"\nScore: {passed}/{total} checks passed")

    if passed == total:
        print("\n[READY] BOT IS READY TO RUN!")
        print("\nNext steps:")
        print("  1. Run: python -m src.fno_trading_bot")
        print("  2. View dashboard: streamlit run dashboard.py")
        return 0
    else:
        print(f"\n[WARNING] Fix {total - passed} issue(s) before running")
        return 1

if __name__ == "__main__":
    sys.exit(main())
