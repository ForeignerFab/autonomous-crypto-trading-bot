# Live Trading Settings Reference

This file preserves the original (pre-demo) configuration values so they can be
restored when switching to live trading. It is a reference only.

## Original settings (pre-demo tuning)

Source files:
- `okx_trading_bot/config_template.yml`
- `okx_trading_bot/config.yml` (local only)

### Trading
- `trading.initial_capital`: 500.0
- `trading.risk_per_trade`: 0.015
- `trading.max_risk_amount`: 7.5
- `trading.strategy.signal_confirmation`: true
- `trading.strategy.stop_loss_multiplier`: 2.0

### Risk management
- `risk_management.max_daily_loss`: 25.0
- `risk_management.max_drawdown`: 60.0

Notes:
- `risk_management.min_stop_loss_pct` and `risk_management.max_stop_loss_pct`
  did not exist in the original configuration.
