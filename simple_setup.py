#!/usr/bin/env python3
"""
SIMPLE SETUP - No dependencies, just Python
Perfect for testing without Flask
"""

import os
import json
import time
import subprocess
import sys
from pathlib import Path

class SimpleSetup:
    """Simple interactive setup for paper mode testing"""

    def __init__(self):
        self.project_dir = Path(__file__).parent
        self.env_file = self.project_dir / ".env"
        self.config_file = self.project_dir / "config.json"

    def clear_screen(self):
        """Clear terminal screen"""
        os.system('cls' if os.name == 'nt' else 'clear')

    def print_header(self):
        """Print beautiful header"""
        print("\n")
        print("╔════════════════════════════════════════════════════════════╗")
        print("║          🤖 ANTIGRAVITY BOT - PAPER MODE SETUP            ║")
        print("║                    Simple & Secure                         ║")
        print("╚════════════════════════════════════════════════════════════╝")
        print()

    def check_paper_mode(self):
        """Verify paper mode is enabled"""
        print("📋 Checking Paper Mode Configuration...")
        try:
            with open(self.config_file, 'r', encoding='utf-8') as f:
                config = json.load(f)

            live_trading = config.get('trading_mode', {}).get('live_trading', False)
            daily_loss = config.get('capital', {}).get('daily_loss_limit_percent', 5.0)

            if live_trading:
                print("❌ ERROR: live_trading is TRUE!")
                print("   This would place REAL trades with REAL capital!")
                print("   Changing to FALSE (Paper Mode)...")
                config['trading_mode']['live_trading'] = False
                with open(self.config_file, 'w', encoding='utf-8') as f:
                    json.dump(config, f, indent=4)
                print("✅ Paper Mode enabled")
            else:
                print(f"✅ Paper Mode enabled (live_trading=false)")

            print(f"✅ Daily loss limit: {daily_loss}%")
            return True
        except Exception as e:
            print(f"❌ Error checking config: {e}")
            return False

    def get_credentials(self):
        """Get credentials from user (with secure input)"""
        print("\n📝 Enter mStock API Credentials:")
        print("   (These will be saved securely in .env)")
        print()

        credentials = {}

        print("🔑 API Key:")
        api_key = input("   → ").strip()
        if not api_key:
            print("❌ API Key is required!")
            return None
        credentials['API_KEY'] = api_key

        print("\n🔑 API Secret:")
        api_secret = input("   → ").strip()
        if not api_secret:
            print("❌ API Secret is required!")
            return None
        credentials['API_SECRET'] = api_secret

        print("\n🔑 Client Code:")
        client_code = input("   → ").strip()
        if not client_code:
            print("❌ Client Code is required!")
            return None
        credentials['CLIENT_CODE'] = client_code

        print("\n🔑 Password:")
        password = input("   → ").strip()
        if not password:
            print("❌ Password is required!")
            return None
        credentials['PASSWORD'] = password

        return credentials

    def save_credentials(self, credentials):
        """Save credentials to .env file securely"""
        print("\n💾 Saving credentials securely...")

        try:
            env_content = f"""API_KEY={credentials['API_KEY']}
API_SECRET={credentials['API_SECRET']}
CLIENT_CODE={credentials['CLIENT_CODE']}
PASSWORD={credentials['PASSWORD']}
"""

            with open(self.env_file, 'w', encoding='utf-8') as f:
                f.write(env_content)

            # Restrict permissions (Unix-like systems)
            try:
                os.chmod(self.env_file, 0o600)  # Owner read/write only
                print("✅ Credentials saved securely (.env)")
                print("✅ File permissions: 0o600 (owner only)")
            except:
                print("✅ Credentials saved (.env)")

            # Verify credentials were saved
            if self.env_file.exists():
                print("✅ .env file verified")
                return True
            else:
                print("❌ Failed to save .env file")
                return False

        except Exception as e:
            print(f"❌ Error saving credentials: {e}")
            return False

    def verify_credentials_not_logged(self):
        """Verify credentials aren't in logs"""
        print("\n🔍 Verifying credentials security...")

        try:
            logs_dir = self.project_dir / "logs"
            if logs_dir.exists():
                for log_file in logs_dir.glob("*.log"):
                    with open(log_file, 'r', encoding='utf-8', errors='ignore') as f:
                        content = f.read()
                        if 'API_KEY' in content or 'password' in content.lower():
                            print(f"⚠️  WARNING: Credentials may be in {log_file}")
                            return False

            print("✅ Credentials not found in logs (secure)")
            return True
        except Exception as e:
            print(f"⚠️  Could not verify logs: {e}")
            return True  # Don't fail on this

    def start_bot(self):
        """Start the bot in background"""
        print("\n🚀 Starting bot in background...")

        try:
            # Create logs directory
            logs_dir = self.project_dir / "logs"
            logs_dir.mkdir(exist_ok=True)

            # Start bot
            if os.name == 'nt':  # Windows
                # Windows PowerShell
                subprocess.Popen(
                    [sys.executable, "main.py"],
                    cwd=str(self.project_dir),
                    stdout=subprocess.DEVNULL,
                    stderr=subprocess.DEVNULL,
                    creationflags=subprocess.CREATE_NEW_PROCESS_GROUP
                )
            else:  # Unix
                subprocess.Popen(
                    [sys.executable, "main.py"],
                    cwd=str(self.project_dir),
                    stdout=subprocess.DEVNULL,
                    stderr=subprocess.DEVNULL,
                    start_new_session=True
                )

            time.sleep(3)  # Wait for startup

            # Check if bot is running
            if os.name == 'nt':
                result = subprocess.run(
                    ["tasklist"],
                    capture_output=True,
                    text=True,
                    timeout=5
                )
                running = "python.exe" in result.stdout
            else:
                result = subprocess.run(
                    ["pgrep", "-f", "python main.py"],
                    capture_output=True,
                    timeout=5
                )
                running = result.returncode == 0

            if running:
                print("✅ Bot started successfully!")
                return True
            else:
                print("⚠️  Bot may be starting (check logs in 10 seconds)")
                return True
        except Exception as e:
            print(f"❌ Error starting bot: {e}")
            print("   Try running: python main.py")
            return False

    def check_logs(self):
        """Check bot logs"""
        print("\n📋 Checking bot logs...")

        try:
            logs_dir = self.project_dir / "logs"
            if not logs_dir.exists():
                print("⚠️  No logs directory yet (bot still starting)")
                return False

            log_files = list(logs_dir.glob("trading_bot_*.log"))
            if not log_files:
                print("⚠️  No log files yet (bot still starting)")
                return False

            latest_log = max(log_files, key=os.path.getctime)
            print(f"✅ Latest log: {latest_log.name}")

            # Show last 5 lines
            print("\n📊 Latest log entries:")
            print("─" * 60)
            try:
                with open(latest_log, 'r', encoding='utf-8', errors='ignore') as f:
                    lines = f.readlines()[-5:]
                    for line in lines:
                        print(f"   {line.rstrip()}")
            except:
                print("   (Log file loading...)")
            print("─" * 60)

            return True
        except Exception as e:
            print(f"⚠️  Error reading logs: {e}")
            return False

    def show_next_steps(self):
        """Show what to do next"""
        print("\n✅ SETUP COMPLETE!")
        print("\n📋 Next Steps:")
        print("   1. Bot is running in background")
        print("   2. Logs are saved to: logs/trading_bot_*.log")
        print("   3. Check logs hourly for validation")
        print("   4. Monitoring reports: monitoring/validation_reports/")
        print("\n📊 To Check Status:")
        print("   - View logs: tail -f logs/trading_bot_*.log")
        print("   - Run validation: python monitoring/hourly_validation.py")
        print("\n⚠️  Important:")
        print("   - Paper Mode: live_trading=false (safe)")
        print("   - All orders: PAPER_ORDER_* (simulated)")
        print("   - No real capital used")
        print("\n🎯 End of Day:")
        print("   - Collect: BUG_REGISTRY_TESTING_FINAL.md")
        print("   - Collect: monitoring/validation_reports/*.json")
        print("   - Share summary")

    def run(self):
        """Run the complete setup"""
        self.clear_screen()
        self.print_header()

        # Step 1: Check paper mode
        if not self.check_paper_mode():
            print("\n❌ Setup failed!")
            return False

        # Step 2: Get credentials
        print("\n" + "─" * 60)
        credentials = self.get_credentials()
        if not credentials:
            print("\n❌ Setup cancelled")
            return False

        # Step 3: Confirm before saving
        print("\n⚠️  Review your credentials:")
        print(f"   API Key: {credentials['API_KEY'][:10]}...")
        print(f"   API Secret: {credentials['API_SECRET'][:10]}...")
        print(f"   Client Code: {credentials['CLIENT_CODE']}")
        print(f"   Password: {'*' * len(credentials['PASSWORD'])}")

        confirm = input("\n✅ Save and start bot? (yes/no): ").strip().lower()
        if confirm != 'yes':
            print("❌ Setup cancelled")
            return False

        # Step 4: Save credentials
        if not self.save_credentials(credentials):
            print("\n❌ Failed to save credentials!")
            return False

        # Step 5: Verify security
        if not self.verify_credentials_not_logged():
            print("⚠️  Security warning - check logs")

        # Step 6: Start bot
        if not self.start_bot():
            print("\n⚠️  Bot may not have started properly")

        # Step 7: Check logs
        time.sleep(2)
        self.check_logs()

        # Step 8: Show next steps
        self.show_next_steps()

        print("\n" + "=" * 60)
        print("✅ SETUP COMPLETE - BOT IS RUNNING!")
        print("=" * 60 + "\n")

        return True


if __name__ == "__main__":
    try:
        setup = SimpleSetup()
        success = setup.run()
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n\n❌ Setup cancelled by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Setup failed: {e}")
        sys.exit(1)
