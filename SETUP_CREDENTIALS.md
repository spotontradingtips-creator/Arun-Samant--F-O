# 🔐 Setting Up Credentials for Paper Mode Testing

The bot needs mStock API credentials to authenticate and access market data. **Even in paper mode, real authentication is required.**

---

## 📋 What You Need

**From your mStock account**, you need:
1. **API_KEY** - Your API key from mStock portal
2. **API_SECRET** - Your API secret (keep secure!)
3. **CLIENT_CODE** - Your trading account code
4. **PASSWORD** - Your mStock login password

---

## 🔧 Option 1: Create `.env` File (Recommended)

Create a `.env` file in the bot directory:

```bash
# .env file location: C:\Antigravity\Arun Samant- F&O_Latest\.env

API_KEY=your_api_key_here
API_SECRET=your_api_secret_here
CLIENT_CODE=your_client_code_here
PASSWORD=your_password_here
```

**Then start bot**:
```bash
python main.py
```

---

## 🔧 Option 2: Create `credentials.json` File

Create `credentials.json` in the bot directory:

```json
{
    "api_key": "your_api_key_here",
    "api_secret": "your_api_secret_here",
    "client_code": "your_client_code_here",
    "password": "your_password_here"
}
```

**Note**: This file is in `.gitignore` - safe to store locally

---

## 🛡️ Security Notes

⚠️ **IMPORTANT:**
- Never commit credentials to git
- Never share .env or credentials.json files
- Credentials file is automatically protected (chmod 0o600)
- .gitignore prevents accidental commits

---

## 🚀 How to Get Credentials

1. **Login to mStock Portal**: https://www.mstocktrade.com/
2. **Navigate to**: API Settings / Developer Portal
3. **Copy**:
   - API Key
   - API Secret
   - Client Code
4. **Use your mStock login password**

---

## ✅ Testing in Paper Mode

Once credentials are set up:

1. **Bot starts in PAPER MODE** (live_trading=false in config.json)
2. **All orders are simulated** (PAPER_ORDER_* in logs)
3. **No real capital used**
4. **Market data is real** (uses broker connection)
5. **Perfect for testing all 21 bugs**

---

## 📝 Next Steps

1. Get your mStock API credentials
2. Create `.env` file with credentials
3. Start bot: `python main.py`
4. Bot runs in paper mode (safe testing)
5. All 21 bugs validated

---

**Ready to proceed?** Provide your mStock credentials and I'll set everything up!
