# Workspace Designation
This repository's workspace root is:

`d:\AI TRADER\Cryptobot\`

All future project work should be organized under this root. The active codebase
lives in `okx_trading_bot/`, and supporting assets/docs should remain at the root
or under `okx_trading_bot/docs/` as appropriate.

## Recommended Structure (grows with project)
- `okx_trading_bot/` — application code, configs, runtime assets
- `okx_trading_bot/docs/` — project documentation
- Root `*.md` / `*.pdf` — high-level project guides and references

## Notes
- Treat `okx_trading_bot/` as the primary app workspace for development.
- Keep sensitive files in `.env` (already git-ignored).
- If new large folders are needed later (datasets, experiments, backtests),
  create them under this root to keep everything centralized.
