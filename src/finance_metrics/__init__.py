"""
Finance Metrics Library

A collection of financial and economic metrics to support retail demand forecasting.
"""

from .macro_indicators import MacroIndicators
from .market_indices import MarketIndices
from .consumer_metrics import ConsumerMetrics
from .commodity_prices import CommodityPrices
from .custom_metrics import CustomMetrics

__version__ = "0.1.0"

__all__ = [
    "MacroIndicators",
    "MarketIndices",
    "ConsumerMetrics",
    "CommodityPrices",
    "CustomMetrics",
]
