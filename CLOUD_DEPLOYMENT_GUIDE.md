# ☁️ Cloud Deployment Guide - OKX Trading Bot

## Overview

This guide covers deploying your OKX Trading Bot to cloud platforms for 24/7 operation without keeping your PC running.

## 🆓 Free Hosting Options

### Option 1: Railway.app (Recommended - Free Tier Available)
- **Free Tier**: $5 credit/month (enough for small bot)
- **Pros**: Easy setup, automatic deployments, good documentation
- **Cons**: Limited free tier, may need paid plan for 24/7

### Option 2: Render.com (Free Tier Available)
- **Free Tier**: Free web services (spins down after inactivity)
- **Pros**: Truly free, good for testing
- **Cons**: Spins down after 15 min inactivity (not ideal for trading bot)

### Option 3: Fly.io (Free Tier Available)
- **Free Tier**: 3 shared VMs, 3GB storage
- **Pros**: Good free tier, global deployment
- **Cons**: More complex setup

### Option 4: Oracle Cloud (Always Free)
- **Free Tier**: 2 VMs with 1GB RAM each
- **Pros**: Truly free, powerful VMs
- **Cons**: More setup required, Oracle account needed

## 🚀 Deployment: Railway.app (Recommended)

### Step 1: Prepare Your Code

1. **Ensure all files are in Cryptobot folder**
   ```bash
   cd "d:/AI TRADER/Cryptobot/okx_trading_bot"
   ```

2. **Create .env file** (don't commit this!)
   ```bash
   cp .env.example .env
   # Edit .env with your API keys
   ```

3. **Test locally first**
   ```bash
   python main.py
   ```

### Step 2: Setup Railway Account

1. Go to [railway.app](https://railway.app)
2. Sign up with GitHub
3. Create new project

### Step 3: Deploy to Railway

1. **Connect Repository**
   - Click "New Project"
   - Select "Deploy from GitHub repo"
   - Select your repository (or create one first)

2. **Configure Environment Variables**
   - Go to "Variables" tab
   - Add all variables from your .env file:
     ```
     OKX_API_KEY=your_key
     OKX_SECRET_KEY=your_secret
     OKX_PASSPHRASE=your_passphrase
     DISCORD_BOT_TOKEN=your_token
     DISCORD_CHANNEL_ID=your_channel_id
     OLLAMA_BASE_URL=https://your-ollama-instance.com
     OLLAMA_MODEL=llama3.2:7b
     ```

3. **Configure Build Settings**
   - Railway auto-detects Dockerfile
   - Or set build command: `pip install -r requirements.txt`
   - Start command: `python main.py`

4. **Deploy**
   - Railway will automatically build and deploy
   - Check logs for any errors

### Step 4: Setup Ollama (Free AI)

**Option A: Use External Ollama Service**
- Use a free Ollama hosting service
- Set `OLLAMA_BASE_URL` to the service URL

**Option B: Run Ollama in Separate Railway Service**
- Create new service in Railway
- Use Docker image: `ollama/ollama:latest`
- Expose port 11434
- Pull model: `ollama pull llama3.2:7b`

**Option C: Use Deepseek API (Alternative)**
- Deepseek offers free API tier
- Update `ollama_service.py` to support Deepseek API

### Step 5: Monitor Deployment

1. **Check Logs**
   - Railway dashboard → Your service → Logs
   - Monitor for errors

2. **Verify Bot is Running**
   - Check Discord for startup notification
   - Check Railway metrics

## 🚀 Deployment: Render.com

### Step 1: Prepare for Render

1. **Create render.yaml** (already created in project)
2. **Ensure Dockerfile exists**

### Step 2: Deploy to Render

1. Go to [render.com](https://render.com)
2. Sign up with GitHub
3. New → Web Service
4. Connect your repository
5. Configure:
   - **Name**: okx-trading-bot
   - **Environment**: Docker
   - **Region**: Choose closest to OKX servers
   - **Instance Type**: Free (or paid for 24/7)

6. **Add Environment Variables** (same as Railway)

7. **Deploy**

**Note**: Free tier spins down after 15 min inactivity. For 24/7, upgrade to paid plan ($7/month).

## 🚀 Deployment: Fly.io

### Step 1: Install Fly CLI

```bash
# Windows (PowerShell)
iwr https://fly.io/install.ps1 -useb | iex

# Or download from: https://fly.io/docs/hands-on/install-flyctl/
```

### Step 2: Login and Setup

```bash
fly auth login
fly launch
```

### Step 3: Configure

1. **Create fly.toml** (if not exists)
2. **Set secrets**:
   ```bash
   fly secrets set OKX_API_KEY=your_key
   fly secrets set OKX_SECRET_KEY=your_secret
   fly secrets set OKX_PASSPHRASE=your_passphrase
   fly secrets set DISCORD_BOT_TOKEN=your_token
   ```

3. **Deploy**:
   ```bash
   fly deploy
   ```

## 🚀 Deployment: Oracle Cloud (Always Free)

### Step 1: Create VM Instance

1. Go to [Oracle Cloud](https://cloud.oracle.com)
2. Create Always Free VM:
   - **Shape**: VM.Standard.E2.1.Micro
   - **OS**: Ubuntu 22.04
   - **SSH Key**: Generate and download

### Step 2: Setup VM

```bash
# SSH into VM
ssh -i your-key.pem ubuntu@your-vm-ip

# Update system
sudo apt update && sudo apt upgrade -y

# Install Docker
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh

# Install Docker Compose
sudo apt install docker-compose -y

# Add user to docker group
sudo usermod -aG docker ubuntu
```

### Step 3: Deploy Bot

```bash
# Clone your repository
git clone your-repo-url
cd okx_trading_bot

# Create .env file
nano .env
# Add your API keys

# Start with Docker Compose
docker-compose up -d

# Check logs
docker-compose logs -f
```

## 🔧 Ollama Setup for Cloud

### Option 1: External Ollama Service

Use a free Ollama hosting:
- [Ollama Cloud](https://ollama.ai) (if available)
- Self-hosted on separate free VM
- Community Ollama instances

### Option 2: Deepseek API (Free Alternative)

Deepseek offers free API access:
1. Sign up at [deepseek.com](https://deepseek.com)
2. Get API key
3. Update `ollama_service.py` to support Deepseek

### Option 3: Run Ollama in Same Container

Add to Dockerfile:
```dockerfile
RUN curl -fsSL https://ollama.ai/install.sh | sh
RUN ollama pull llama3.2:7b
```

**Note**: This increases container size significantly.

## 📊 Monitoring & Maintenance

### Health Checks

All platforms support health checks:
- Railway: Automatic
- Render: Configure in dashboard
- Fly.io: Add to fly.toml
- Oracle: Use systemd service

### Logs

Monitor logs regularly:
- Railway: Dashboard → Logs
- Render: Dashboard → Logs
- Fly.io: `fly logs`
- Oracle: `docker-compose logs -f`

### Alerts

Set up alerts for:
- Bot crashes
- High error rates
- API failures
- Discord notifications

## 💰 Cost Comparison

| Platform | Free Tier | Paid (24/7) | Best For |
|----------|-----------|-------------|----------|
| Railway | $5 credit/month | $5-20/month | Easy setup |
| Render | Free (spins down) | $7/month | Simple deployment |
| Fly.io | 3 VMs free | $0-5/month | Global deployment |
| Oracle | Always free | $0 | Maximum free resources |

## ✅ Post-Deployment Checklist

- [ ] Bot starts successfully
- [ ] Environment variables set correctly
- [ ] Ollama AI connected (if using)
- [ ] Discord notifications working
- [ ] OKX API connection successful
- [ ] Logs showing normal operation
- [ ] Health checks passing
- [ ] Monitoring alerts configured

## 🐛 Troubleshooting

### Bot Won't Start

1. Check logs for errors
2. Verify environment variables
3. Check API credentials
4. Verify Docker build succeeded

### Ollama Not Working

1. Check `OLLAMA_BASE_URL` is correct
2. Verify Ollama service is running
3. Check network connectivity
4. Try fallback mode (disable Ollama)

### High Resource Usage

1. Optimize Docker image
2. Reduce logging verbosity
3. Limit concurrent operations
4. Upgrade to larger instance

## 📚 Additional Resources

- [Railway Docs](https://docs.railway.app)
- [Render Docs](https://render.com/docs)
- [Fly.io Docs](https://fly.io/docs)
- [Oracle Cloud Docs](https://docs.oracle.com/en-us/iaas/)

## 🎉 Success!

Your bot is now running in the cloud 24/7! Monitor it regularly and adjust as needed.








