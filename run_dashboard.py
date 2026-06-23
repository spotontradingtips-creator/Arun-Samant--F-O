#!/usr/bin/env python3
"""
Dashboard launcher with proper Python path setup
"""
import subprocess
import sys
import os

if __name__ == "__main__":
    project_root = os.path.dirname(os.path.abspath(__file__))
    dashboard_path = os.path.join(project_root, "dashboard.py")

    # Run streamlit with proper environment
    env = os.environ.copy()
    env['PYTHONPATH'] = project_root

    subprocess.run(
        [sys.executable, "-m", "streamlit", "run", dashboard_path],
        env=env,
        cwd=project_root
    )
