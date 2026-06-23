import json
import os
import sys

# Path to the positions file
POSITIONS_PATH = "data/positions.json"

def repair():
    print("--- FnO Bot Live Trade Metadata Repair ---")
    if not os.path.exists(POSITIONS_PATH):
        print(f"Error: {POSITIONS_PATH} not found.")
        return

    try:
        with open(POSITIONS_PATH, "r") as f:
            positions = json.load(f)
    except Exception as e:
        print(f"Error reading positions: {e}")
        return

    if not positions:
        print("No active trades found in data/positions.json.")
        return

    updated = False
    for key, pos in positions.items():
        sym = pos.get("option_symbol", "")
        # If symbol is CE but trade_type is PE
        if "CE" in sym.upper() and pos.get("trade_type") == "PE":
            print(f"FIXING {key}: Type PE -> CE (matched symbol {sym})")
            pos["trade_type"] = "CE"
            updated = True
        elif "PE" in sym.upper() and pos.get("trade_type") == "CE":
            print(f"FIXING {key}: Type CE -> PE (matched symbol {sym})")
            pos["trade_type"] = "PE"
            updated = True

    if updated:
        with open(POSITIONS_PATH, "w") as f:
            json.dump(positions, f, indent=4)
        print("\nSUCCESS: Trade type metadata corrected in data/positions.json.")
        print("IMPORTANT: You must restart the bot now. It will reload the fixed file and track your trade correctly.")
    else:
        print("No mismatches found. Your local state file is already correct.")

if __name__ == "__main__":
    repair()
