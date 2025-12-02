"""
Market Indices

Fetch and process stock market indices that reflect economic sentiment:
- S&P 500
- Dow Jones Industrial Average
- NASDAQ Composite
- VIX (Volatility Index)
- Russell 2000
"""

from datetime import datetime
from typing import List, Optional

import pandas as pd
import yfinance as yf


class MarketIndices:
    """Fetch and process stock market indices."""

    # Common market index tickers
    INDICES = {
        "sp500": "^GSPC",
        "dow": "^DJI",
        "nasdaq": "^IXIC",
        "russell2000": "^RUT",
        "vix": "^VIX",
    }

    def __init__(self):
        """Initialize MarketIndices."""
        pass

    def get_index(
        self,
        index_name: str,
        start_date: Optional[str] = None,
        end_date: Optional[str] = None,
        interval: str = "1d"
    ) -> pd.DataFrame:
        """
        Fetch market index data.

        Args:
            index_name: Name of the index (sp500, dow, nasdaq, russell2000, vix)
            start_date: Start date in YYYY-MM-DD format
            end_date: End date in YYYY-MM-DD format
            interval: Data interval (1d, 1wk, 1mo)

        Returns:
            DataFrame with market index data
        """
        ticker = self.INDICES.get(index_name.lower())
        if not ticker:
            raise ValueError(f"Unknown index: {index_name}. Available: {list(self.INDICES.keys())}")

        data = yf.download(
            ticker,
            start=start_date,
            end=end_date,
            interval=interval,
            progress=False,
            auto_adjust=True
        )
        
        # Flatten MultiIndex columns if they exist
        if isinstance(data.columns, pd.MultiIndex):
            # For single ticker, get the first level (price type: Open, High, Low, Close, Volume)
            data.columns = data.columns.get_level_values(0)

        return data

    def get_returns(
        self,
        index_name: str,
        start_date: Optional[str] = None,
        end_date: Optional[str] = None,
        period: int = 1
    ) -> pd.DataFrame:
        """
        Calculate returns for a market index.

        Args:
            index_name: Name of the index
            start_date: Start date in YYYY-MM-DD format
            end_date: End date in YYYY-MM-DD format
            period: Period for return calculation (days)

        Returns:
            DataFrame with returns data
        """
        data = self.get_index(index_name, start_date, end_date)
        returns = data['Close'].pct_change(periods=period)
        return pd.DataFrame({'returns': returns})

    def get_multiple_indices(
        self,
        index_names: List[str],
        start_date: Optional[str] = None,
        end_date: Optional[str] = None
    ) -> pd.DataFrame:
        """
        Fetch multiple market indices at once.

        Args:
            index_names: List of index names
            start_date: Start date in YYYY-MM-DD format
            end_date: End date in YYYY-MM-DD format

        Returns:
            DataFrame with multiple index closing prices
        """
        dfs = []
        for name in index_names:
            data = self.get_index(name, start_date, end_date)
            dfs.append(data['Close'].rename(name))

        return pd.concat(dfs, axis=1)
