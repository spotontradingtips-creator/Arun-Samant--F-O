"""Test that .gitignore properly blocks credential and secret files."""

import subprocess
import os
from pathlib import Path


def get_tracked_files():
    """Get all files tracked by git."""
    result = subprocess.run(
        ["git", "ls-files"],
        capture_output=True,
        text=True,
        cwd=os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    )
    # Filter empty strings at source to avoid repeated filtering
    return [f for f in result.stdout.strip().split("\n") if f]


def test_no_credential_files_tracked():
    """Verify no credential files are tracked by git."""
    credential_patterns = [
        "credentials.json",
        ".env",
        "config_live.json",
        "account_secrets.json",
        "otp_response.txt",
        "session_token",
        "broker_auth",
        ".pem",
        ".key",
    ]

    tracked_files = get_tracked_files()
    for pattern in credential_patterns:
        for file in tracked_files:
            assert pattern not in file, f"Credential pattern '{pattern}' found in tracked file: {file}"


def test_no_api_response_files_tracked():
    """Verify no API response files are tracked."""
    api_patterns = [
        "_api_response",
        "_broker_response",
        "access_token",
        "refresh_token",
        "jwt_token",
    ]

    tracked_files = get_tracked_files()
    for pattern in api_patterns:
        for file in tracked_files:
            assert pattern not in file, f"API pattern '{pattern}' found in tracked file: {file}"


def test_no_temp_files_tracked():
    """Verify no temporary files are tracked."""
    temp_extensions = [".bak", ".backup", ".tmp"]

    tracked_files = get_tracked_files()
    for file in tracked_files:
        for ext in temp_extensions:
            assert not file.endswith(ext), f"Temp file '{file}' with extension '{ext}' is tracked"


def test_sensitive_dirs_not_tracked():
    """Verify sensitive directories are not tracked."""
    sensitive_dirs = [
        ".aws/",
        ".gcp/",
        ".azure/",
        ".vscode/",
        ".idea/",
    ]

    tracked_files = get_tracked_files()
    for dir_pattern in sensitive_dirs:
        for file in tracked_files:
            assert not file.startswith(dir_pattern), f"Sensitive dir '{dir_pattern}' found in tracked files: {file}"


def test_gitignore_file_exists():
    """Verify .gitignore file exists and is not empty."""
    gitignore_path = Path(__file__).parent.parent / ".gitignore"
    assert gitignore_path.exists(), ".gitignore file not found"
    assert gitignore_path.stat().st_size > 0, ".gitignore file is empty"


def test_gitignore_has_credential_rules():
    """Verify .gitignore contains credential protection rules."""
    gitignore_path = Path(__file__).parent.parent / ".gitignore"
    content = gitignore_path.read_text()

    required_patterns = [
        "credentials.json",
        ".env",
        "otp_response",
        "*.key",
        "*.pem",
    ]

    for pattern in required_patterns:
        assert pattern in content, f"Required pattern '{pattern}' not found in .gitignore"


if __name__ == "__main__":
    test_gitignore_file_exists()
    test_gitignore_has_credential_rules()
    test_no_credential_files_tracked()
    test_no_api_response_files_tracked()
    test_no_temp_files_tracked()
    test_sensitive_dirs_not_tracked()
    print("✅ All .gitignore compliance tests passed!")
