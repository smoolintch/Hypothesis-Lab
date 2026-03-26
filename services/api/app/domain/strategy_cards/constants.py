SUPPORTED_SYMBOLS = {"BTCUSDT", "ETHUSDT"}
SUPPORTED_TIMEFRAMES = {"4H", "1D"}
STRATEGY_CARD_DEFAULT_STATUS = "draft"

ALLOWED_RULE_TEMPLATES_BY_POSITION = {
    "entry": {"ma_cross", "rsi_threshold", "price_breakout", "streak_reversal"},
    "exit": {"ma_cross", "rsi_threshold", "price_breakout", "streak_reversal"},
    "stop_loss": {"fixed_stop_loss"},
    "take_profit": {"fixed_take_profit"},
}
