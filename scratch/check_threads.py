import psutil
import os

def find_main():
    for proc in psutil.process_iter(['pid', 'name', 'cmdline']):
        if proc.info['cmdline'] and 'main.py' in proc.info['cmdline']:
            return proc
    return None

proc = find_main()
if proc:
    print(f"Process {proc.pid} found: {proc.name()}")
    print(f"Status: {proc.status()}")
    print(f"Threads: {len(proc.threads())}")
    for t in proc.threads():
        print(f"  Thread ID: {t.id}")
else:
    print("Process main.py not found.")
