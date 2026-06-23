#!/usr/bin/env python3
"""
Simple Web UI for Paper Mode Setup
Perfect for non-technical users
"""

from flask import Flask, render_template_string, request, jsonify
import json
import os
import subprocess
import time
from pathlib import Path

app = Flask(__name__)

HTML_TEMPLATE = '''
<!DOCTYPE html>
<html>
<head>
    <title>Antigravity Bot - Paper Mode Setup</title>
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }

        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            display: flex;
            align-items: center;
            justify-content: center;
            padding: 20px;
        }

        .container {
            background: white;
            border-radius: 10px;
            box-shadow: 0 10px 40px rgba(0,0,0,0.2);
            max-width: 500px;
            width: 100%;
            padding: 40px;
        }

        .header {
            text-align: center;
            margin-bottom: 30px;
        }

        .header h1 {
            color: #333;
            font-size: 28px;
            margin-bottom: 10px;
        }

        .header p {
            color: #666;
            font-size: 14px;
        }

        .status-box {
            background: #f0f0f0;
            border-left: 4px solid #667eea;
            padding: 15px;
            margin-bottom: 20px;
            border-radius: 4px;
        }

        .status-box.active {
            border-left-color: #4caf50;
            background: #e8f5e9;
        }

        .status-box.error {
            border-left-color: #f44336;
            background: #ffebee;
        }

        .status-text {
            font-size: 14px;
            color: #666;
        }

        .status-text.success {
            color: #2e7d32;
        }

        .status-text.error {
            color: #c62828;
        }

        .form-group {
            margin-bottom: 20px;
        }

        label {
            display: block;
            margin-bottom: 8px;
            color: #333;
            font-weight: 500;
            font-size: 14px;
        }

        input[type="text"],
        input[type="password"],
        select {
            width: 100%;
            padding: 12px;
            border: 1px solid #ddd;
            border-radius: 4px;
            font-size: 14px;
            font-family: monospace;
        }

        input[type="text"]:focus,
        input[type="password"]:focus,
        select:focus {
            outline: none;
            border-color: #667eea;
            box-shadow: 0 0 0 3px rgba(102, 126, 234, 0.1);
        }

        .mode-selector {
            display: flex;
            gap: 10px;
            margin-bottom: 20px;
        }

        .mode-btn {
            flex: 1;
            padding: 12px;
            border: 2px solid #ddd;
            background: white;
            color: #333;
            border-radius: 4px;
            cursor: pointer;
            font-weight: 500;
            transition: all 0.3s ease;
        }

        .mode-btn.active {
            border-color: #667eea;
            background: #667eea;
            color: white;
        }

        .mode-btn:hover {
            border-color: #667eea;
        }

        .warning {
            background: #fff3cd;
            border: 1px solid #ffc107;
            color: #856404;
            padding: 12px;
            border-radius: 4px;
            margin-bottom: 20px;
            font-size: 13px;
        }

        .warning strong {
            display: block;
            margin-bottom: 5px;
        }

        .button-group {
            display: flex;
            gap: 10px;
            margin-top: 25px;
        }

        button {
            flex: 1;
            padding: 12px;
            border: none;
            border-radius: 4px;
            font-size: 14px;
            font-weight: 600;
            cursor: pointer;
            transition: all 0.3s ease;
        }

        .btn-start {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
        }

        .btn-start:hover {
            transform: translateY(-2px);
            box-shadow: 0 5px 15px rgba(102, 126, 234, 0.4);
        }

        .btn-stop {
            background: #f44336;
            color: white;
        }

        .btn-stop:hover {
            background: #d32f2f;
        }

        .btn-check {
            background: #2196f3;
            color: white;
        }

        .btn-check:hover {
            background: #1976d2;
        }

        button:disabled {
            opacity: 0.5;
            cursor: not-allowed;
        }

        .info-box {
            background: #e3f2fd;
            border: 1px solid #90caf9;
            color: #1565c0;
            padding: 12px;
            border-radius: 4px;
            font-size: 13px;
            margin-top: 15px;
        }

        .loading {
            display: none;
            text-align: center;
            color: #667eea;
            margin-top: 10px;
        }

        .spinner {
            border: 3px solid #f3f3f3;
            border-top: 3px solid #667eea;
            border-radius: 50%;
            width: 30px;
            height: 30px;
            animation: spin 1s linear infinite;
            margin: 0 auto 10px;
        }

        @keyframes spin {
            0% { transform: rotate(0deg); }
            100% { transform: rotate(360deg); }
        }

        .footer {
            margin-top: 20px;
            text-align: center;
            font-size: 12px;
            color: #999;
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🤖 Antigravity Bot</h1>
            <p>Paper Mode Testing Setup</p>
        </div>

        <div id="status" class="status-box">
            <div class="status-text">⏳ Loading status...</div>
        </div>

        <div class="mode-selector">
            <button class="mode-btn active" onclick="setMode('paper')">📄 PAPER MODE</button>
            <button class="mode-btn" onclick="setMode('live')">⚠️ LIVE MODE</button>
        </div>

        <div class="warning">
            <strong>⚠️ Important:</strong>
            Paper Mode is selected. Bot will use simulated trades (PAPER_ORDER_*). No real capital will be used.
        </div>

        <div class="form-group">
            <label>API Key</label>
            <input type="password" id="apiKey" placeholder="Enter API Key from mStock">
        </div>

        <div class="form-group">
            <label>API Secret</label>
            <input type="password" id="apiSecret" placeholder="Enter API Secret from mStock">
        </div>

        <div class="form-group">
            <label>Client Code</label>
            <input type="text" id="clientCode" placeholder="Enter your Client Code">
        </div>

        <div class="form-group">
            <label>Password</label>
            <input type="password" id="password" placeholder="Enter your mStock password">
        </div>

        <div class="button-group">
            <button class="btn-start" onclick="saveAndStart()">💾 SAVE & START BOT</button>
            <button class="btn-check" onclick="checkStatus()">📊 CHECK STATUS</button>
        </div>

        <div id="startButton">
            <button class="btn-stop" onclick="stopBot()" style="display:none;">🛑 STOP BOT</button>
        </div>

        <div class="loading" id="loading">
            <div class="spinner"></div>
            <div>Starting bot...</div>
        </div>

        <div class="info-box">
            💡 <strong>Info:</strong> Bot will run in PAPER MODE. All orders are simulated (PAPER_ORDER_*).
            Check hourly validation reports in the monitoring/validation_reports/ folder.
        </div>

        <div class="footer">
            <p>Made with ❤️ for testing</p>
            <p>For support, contact Arun</p>
        </div>
    </div>

    <script>
        let currentMode = 'paper';

        function setMode(mode) {
            currentMode = mode;
            const buttons = document.querySelectorAll('.mode-btn');
            buttons.forEach(btn => btn.classList.remove('active'));
            event.target.classList.add('active');

            if (mode === 'live') {
                const confirmed = confirm('⚠️ WARNING: Switch to LIVE MODE?\n\nThis will place REAL trades with REAL capital at risk!\n\nClick OK only if you\'re sure.');
                if (!confirmed) {
                    currentMode = 'paper';
                    buttons[0].classList.add('active');
                    buttons[1].classList.remove('active');
                }
            }
        }

        function saveAndStart() {
            const apiKey = document.getElementById('apiKey').value;
            const apiSecret = document.getElementById('apiSecret').value;
            const clientCode = document.getElementById('clientCode').value;
            const password = document.getElementById('password').value;

            if (!apiKey || !apiSecret || !clientCode || !password) {
                alert('❌ Please fill in all fields');
                return;
            }

            document.getElementById('loading').style.display = 'block';

            fetch('/api/save-and-start', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    api_key: apiKey,
                    api_secret: apiSecret,
                    client_code: clientCode,
                    password: password,
                    mode: currentMode
                })
            })
            .then(r => r.json())
            .then(data => {
                document.getElementById('loading').style.display = 'none';
                if (data.status === 'ok') {
                    alert('✅ Bot started successfully! Monitoring tab will open in 5 seconds.');
                    setTimeout(checkStatus, 5000);
                } else {
                    alert('❌ Error: ' + data.message);
                }
            })
            .catch(e => {
                document.getElementById('loading').style.display = 'none';
                alert('❌ Error: ' + e);
            });
        }

        function checkStatus() {
            fetch('/api/status')
                .then(r => r.json())
                .then(data => {
                    const statusBox = document.getElementById('status');
                    const stopBtn = document.querySelector('.btn-stop');

                    if (data.running) {
                        statusBox.className = 'status-box active';
                        statusBox.innerHTML = `
                            <div class="status-text success">
                                ✅ Bot is running! (PID: ${data.pid})
                            </div>
                            <div class="status-text success">
                                Mode: ${data.mode === 'live' ? '🔴 LIVE' : '🟢 PAPER'}
                            </div>
                            <div class="status-text success">
                                Trades: ${data.trades_today || 0}
                            </div>
                        `;
                        stopBtn.style.display = 'block';
                    } else {
                        statusBox.className = 'status-box error';
                        statusBox.innerHTML = `
                            <div class="status-text error">
                                ❌ Bot is not running
                            </div>
                        `;
                        stopBtn.style.display = 'none';
                    }
                });
        }

        function stopBot() {
            if (confirm('Are you sure you want to stop the bot?')) {
                fetch('/api/stop', { method: 'POST' })
                    .then(r => r.json())
                    .then(data => {
                        alert('✅ Bot stopped');
                        checkStatus();
                    });
            }
        }

        // Check status on load
        checkStatus();

        // Auto-refresh status every 30 seconds
        setInterval(checkStatus, 30000);
    </script>
</body>
</html>
'''

@app.route('/')
def index():
    return render_template_string(HTML_TEMPLATE)

@app.route('/api/status')
def get_status():
    """Get current bot status"""
    try:
        # Check if bot process is running
        result = subprocess.run(
            ["pgrep", "-f", "python main.py"],
            capture_output=True,
            text=True,
            timeout=5
        )

        running = result.returncode == 0
        pid = result.stdout.strip() if running else None

        # Check config for mode
        mode = 'paper'
        try:
            with open('config.json', 'r', encoding='utf-8') as f:
                config = json.load(f)
                mode = 'live' if config.get('trading_mode', {}).get('live_trading', False) else 'paper'
        except:
            pass

        # Count trades today
        trades = 0
        try:
            with open('data/daily_history.json', 'r', encoding='utf-8') as f:
                history = json.load(f)
                trades = len(history) if isinstance(history, list) else 0
        except:
            pass

        return jsonify({
            'running': running,
            'pid': pid,
            'mode': mode,
            'trades_today': trades
        })
    except Exception as e:
        return jsonify({'running': False, 'error': str(e)})

@app.route('/api/save-and-start', methods=['POST'])
def save_and_start():
    """Save credentials and start bot"""
    try:
        data = request.json

        # Create .env file
        env_content = f"""API_KEY={data['api_key']}
API_SECRET={data['api_secret']}
CLIENT_CODE={data['client_code']}
PASSWORD={data['password']}
"""

        with open('.env', 'w', encoding='utf-8') as f:
            f.write(env_content)

        # Update config if switching to live
        if data['mode'] == 'live':
            with open('config.json', 'r', encoding='utf-8') as f:
                config = json.load(f)
            config['trading_mode']['live_trading'] = True
            with open('config.json', 'w', encoding='utf-8') as f:
                json.dump(config, f, indent=4)

        # Start bot in background
        subprocess.Popen(
            ["python", "main.py"],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            start_new_session=True
        )

        time.sleep(3)  # Wait for startup

        return jsonify({'status': 'ok', 'message': 'Bot started successfully'})

    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)})

@app.route('/api/stop', methods=['POST'])
def stop_bot():
    """Stop the bot"""
    try:
        subprocess.run(
            ["pkill", "-f", "python main.py"],
            capture_output=True,
            timeout=5
        )
        return jsonify({'status': 'ok'})
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)})

if __name__ == '__main__':
    print("""
    ╔════════════════════════════════════════╗
    ║  Antigravity Bot - Web UI Setup        ║
    ╚════════════════════════════════════════╝

    Opening: http://localhost:5000

    Instructions:
    1. Enter API credentials from mStock
    2. Keep PAPER MODE selected (recommended)
    3. Click "SAVE & START BOT"
    4. Check status and monitoring
    5. At end of day, collect reports

    Press Ctrl+C to stop the UI
    """)

    app.run(debug=False, port=5000, host='localhost')
