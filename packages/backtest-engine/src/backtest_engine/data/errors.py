class MarketDataError(Exception):
    """Base exception for market data loading errors."""


class MarketDatasetNotFoundError(MarketDataError):
    """Raised when the requested dataset directory does not exist."""


class InvalidMarketDatasetError(MarketDataError):
    """Raised when manifest or CSV contents violate dataset rules."""
