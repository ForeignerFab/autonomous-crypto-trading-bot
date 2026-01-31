# OKX Autonomous Trading Bot - Detailed Project Overview

This document is the up-to-date, high-level overview for onboarding a new bot or
assistant. It describes where everything lives, how the system works end-to-end,
and what to configure before deployment.

## 1) Purpose
An autonomous OKX trading bot with:
- AI-assisted trade gating (hard gate) using a remote Ollama model.
- Config-only AI optimizations with Discord approval.
- Pattern research pipeline with scheduled runs.
- Discord control and alerting.
- Cloud deployment (Railway) for 24/7 operation.

## 2) Workspace Layout (Root)
Root: `d:\AI TRADER\Cryptobot\`

Key files:
- `PROJECT_CONTEXT.md` - historical decisions and scope notes.
- `PROJECT_OVERVIEW.md` - this document.
- `WORKSPACE.md` - workspace designation and structure.
- `QUICK_START.md` - quick instructions.

App code (primary):
- `okx_trading_bot/` - main application directory.

## 3) Application Entry Points
- `okx_trading_bot/main.py`
  - Starts the bot manager and trading engine.
  - On startup: if `config.yml` missing, copies from `config_template.yml`.
  - Uses env vars if `.env` is not present (for cloud deployments).

## 4) Core Modules
All are under `okx_trading_bot/src/`:
- `engine.py` - trading engine, AI gating, research scheduling, Discord callbacks.
- `okx_client.py` - OKX exchange API access (via ccxt).
- `indicators.py` - technical indicator calculations.
- `risk.py` - risk management logic.
- `ai_assistant.py` - AI optimization and trade gating logic (Ollama).
- `ollama_service.py` - remote Ollama health and request handling.
- `discord_bot.py` - Discord bot commands, notifications, approvals.
- `database.py` - SQLite DB manager and schema.
- `research.py` - pattern research pipeline (historical analysis).
- `reporter.py` - reports and summaries.

## 5) Configuration
Primary config:
- `okx_trading_bot/config.yml` (runtime)
- `okx_trading_bot/config_template.yml` (template used if config.yml is missing)

Key configuration areas:
- `trading`:
  - `strategy.timeframe`: 5m default.
  - `max_active_pairs`: 3 (demo tuning).
  - Indicators include `enabled` flags for each indicator.
- `okx`:
  - `sandbox: true` for demo.
- `risk_management`:
  - Tuned limits for 5m demo trading.
- `ai_assistant.trade_gating`:
  - `enabled: true`
  - `fail_open: false` (hard gate, blocks trades if AI unavailable).
- `research`:
  - `enabled: true`
  - `top_pairs: 20`
  - `timeframes: ["5m"]`
  - `days: 90`, `interval_hours: 48`

## 6) Environment Variables
Set via Railway Variables or `.env` locally.

Required:
- `OKX_API_KEY`
- `OKX_SECRET_KEY`
- `OKX_PASSPHRASE`

Discord:
- `DISCORD_BOT_TOKEN`
- `DISCORD_CHANNEL_ID`
- `DISCORD_WEBHOOK_URL` (optional if using channel notifications only)

Ollama (remote):
- `OLLAMA_BASE_URL` (example: `http://<ip>:11434`)
- `OLLAMA_MODEL` (default used if unset: `llama3.1:8b`)

## 7) AI Hard-Gating (Trade Approval)
Flow:
1. Engine generates a trade signal.
2. Risk checks run first.
3. AI assistant evaluates the trade (Ollama).
4. If AI rejects or is unavailable and `fail_open: false`, trade is blocked.
5. Decision is logged and posted to Discord.

Relevant code:
- `src/engine.py` (`_can_execute_trade`)
- `src/ai_assistant.py` (`evaluate_trade_signal`)
- `src/discord_bot.py` (`send_ai_gating_log`)

## 8) Config-Only AI Suggestions (Discord Approval)
The AI can suggest safe parameter changes only (no code edits).
These suggestions are posted to Discord and must be approved by an admin.

Commands:
- `!optimize` - request new suggestions
- `!suggestions` - list pending suggestion IDs
- `!approve <id>` - apply a suggestion to `config.yml`
- `!reject <id>` - discard a suggestion

Expired suggestions:
- Auto-expire after 24 hours (no changes applied).
- Expiration is logged and notified in Discord.

Relevant code:
- `src/discord_bot.py` (commands + expiration)
- `src/engine.py` (`_apply_config_updates` and logging)

## 9) Discord Bot Control Commands
Commands:
- `!status` - bot status summary
- `!balance` - OKX balance
- `!positions` - open positions
- `!pause` - pause trading
- `!resume` - resume trading
- `!stop` - request shutdown

Callbacks are wired in `src/engine.py` and handled in `src/discord_bot.py`.

## 10) Pattern Research Pipeline
Runs on a schedule defined in `config.yml`:
- Pulls historical OHLCV data for top USDT pairs.
- Calculates indicators and extracts patterns.
- Computes success rates and average returns.
- Stores results in SQLite and notifies Discord with a summary.

Relevant code:
- `src/research.py`
- `src/okx_client.py` (`get_klines_since`, `get_top_usdt_pairs`)
- `src/database.py` (pattern_research table)

## 11) Data and Logs
SQLite DB:
- `okx_trading_bot/data/trading_bot.db`

Logs:
- `okx_trading_bot/logs/ai_gating.log`
- `okx_trading_bot/logs/config_changes.log`

## 12) Deployment (Railway + Remote Ollama)
Railway deploys the bot container from GitHub.
Ollama runs on a separate VM (Hetzner) and is accessed via `OLLAMA_BASE_URL`.

Critical points:
- Railway must deploy the latest commit.
- If `config.yml` is missing, the app copies `config_template.yml`.
- Set env vars in Railway Variables.

## 13) Common Issues and Fixes
- `config.yml not found`: Ensure latest commit is deployed. The app auto-copies
  from `config_template.yml` now.
- Ollama unavailable: if `fail_open: false`, trades are blocked. Check the VM
  and open port 11434.
- Discord silent: verify bot token, channel ID, and permissions.
- GitHub push blocked by secrets: never commit tokens/keys; use placeholders.

## 14) Quick Start (Local)
1. Copy `config_template.yml` to `config.yml`.
2. Create `.env` using `.env.example`.
3. Install deps: `pip install -r requirements.txt`
4. Run: `python main.py`

## 15) Where to Look First (New Bot/Agent)
Start here:
- `okx_trading_bot/README.md`
- `okx_trading_bot/START_HERE.md`
- `okx_trading_bot/docs/discord_integration.md`
- `okx_trading_bot/docs/trading_strategy.md`
- `okx_trading_bot/docs/troubleshooting.md`
