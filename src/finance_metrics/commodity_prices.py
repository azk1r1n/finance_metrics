"""
Commodity Prices

Fetch and process commodity prices that affect consumer costs:
- Crude Oil (WTI, Brent)
- Natural Gas
- Gold
- Agricultural commodities
"""

import pandas as pd
import yfinance as yf
from typing import Optional


class CommodityPrices:
    """Fetch and process commodity price data."""

    # Common commodity tickers
    COMMODITIES = {
        "crude_oil_wti": "CL=F",
        "crude_oil_brent": "BZ=F",
        "natural_gas": "NG=F",
        "gold": "GC=F",
        "silver": "SI=F",
        "corn": "ZC=F",
        "wheat": "ZW=F",
        "soybeans": "ZS=F",
    }

    def __init__(self):
        """Initialize CommodityPrices."""
        pass

    def get_commodity(
        self,
        commodity_name: str,
        start_date: Optional[str] = None,
        end_date: Optional[str] = None,
        interval: str = "1d"
    ) -> pd.DataFrame:
        """
        Fetch commodity price data.

        Args:
            commodity_name: Name of the commodity
            start_date: Start date in YYYY-MM-DD format
            end_date: End date in YYYY-MM-DD format
            interval: Data interval (1d, 1wk, 1mo)

        Returns:
            DataFrame with commodity price data
        """
        ticker = self.COMMODITIES.get(commodity_name.lower())
        if not ticker:
            raise ValueError(
                f"Unknown commodity: {commodity_name}. "
                f"Available: {list(self.COMMODITIES.keys())}"
            )

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
            data.columns = data.columns.get_level_values(0)

        return data

    def get_oil_spread(
        self,
        start_date: Optional[str] = None,
        end_date: Optional[str] = None
    ) -> pd.DataFrame:
        """
        Calculate the spread between WTI and Brent crude oil.

        Args:
            start_date: Start date in YYYY-MM-DD format
            end_date: End date in YYYY-MM-DD format

        Returns:
            DataFrame with WTI, Brent, and spread
        """
        wti = self.get_commodity("crude_oil_wti", start_date, end_date)
        brent = self.get_commodity("crude_oil_brent", start_date, end_date)

        result = pd.DataFrame({
            'wti': wti['Close'],
            'brent': brent['Close'],
            'spread': brent['Close'] - wti['Close']
        })

        return result
