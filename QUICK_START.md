# 🚀 Quick Start Guide - AI Trader Bot

## ⚡ Fast Setup (5 Minutes)

### Step 1: Install Ollama (Free AI)

**Windows:**
1. Download from https://ollama.ai/download
2. Install and run
3. Open terminal: `ollama pull llama3.2:7b`

**Linux/WSL:**
```bash
curl -fsSL https://ollama.ai/install.sh | sh
ollama pull llama3.2:7b
ollama serve
```

### Step 2: Setup Bot

```bash
cd "d:/AI TRADER/Cryptobot/okx_trading_bot"

# Install dependencies
pip install -r requirements.txt

# Copy config
cp config_template.yml config.yml

# Create .env file (add your API keys)
# OKX_API_KEY=...
# OKX_SECRET_KEY=...
# OKX_PASSPHRASE=...
# DISCORD_BOT_TOKEN=...
```

### Step 3: Test

```bash
# Test Ollama integration
python test_ollama_integration.py

# Run bot
python main.py
```

## ☁️ Deploy to Cloud (10 Minutes)

### Railway.app (Easiest)

1. Push code to GitHub
2. Go to railway.app
3. New Project → Deploy from GitHub
4. Add environment variables
5. Deploy!

See `CLOUD_DEPLOYMENT_GUIDE.md` for details.

## ✅ Verification

- [ ] Ollama running (`ollama list`)
- [ ] Dependencies installed
- [ ] Config files created
- [ ] API keys set
- [ ] Bot starts successfully
- [ ] Discord notifications work

## 🎉 You're Ready!

Your bot is now running with free AI capabilities!








