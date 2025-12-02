"""
Macroeconomic Indicators

Fetch and process macroeconomic indicators that influence retail demand:
- GDP growth
- Inflation rates (CPI, PPI)
- Unemployment rates
- Interest rates
- Housing market indicators
"""

import os
from datetime import datetime
from typing import Optional

import pandas as pd
from dotenv import load_dotenv
from fredapi import Fred

# Load environment variables
load_dotenv()


class MacroIndicators:
    """Fetch and process macroeconomic indicators from FRED."""

    # FRED series IDs for common economic indicators
    SERIES_IDS = {
        "gdp": "GDP",  # Gross Domestic Product
        "gdp_growth": "A191RL1Q225SBEA",  # Real GDP growth rate
        "cpi": "CPIAUCSL",  # Consumer Price Index for All Urban Consumers
        "core_cpi": "CPILFESL",  # CPI excluding food and energy
        "ppi": "PPIACO",  # Producer Price Index
        "unemployment": "UNRATE",  # Unemployment Rate
        "fed_funds": "FEDFUNDS",  # Federal Funds Effective Rate
        "treasury_10y": "DGS10",  # 10-Year Treasury Rate
        "housing_starts": "HOUST",  # Housing Starts
        "retail_sales": "RSXFS",  # Retail Sales
    }

    def __init__(self, api_key: Optional[str] = None):
        """
        Initialize MacroIndicators.

        Args:
            api_key: FRED API key. If not provided, will look for FRED_API_KEY in environment
        """
        self.api_key = api_key or os.getenv("FRED_API_KEY")
        if not self.api_key:
            raise ValueError(
                "FRED API key not found. Either pass api_key parameter or set FRED_API_KEY environment variable."
            )
        self.fred = Fred(api_key=self.api_key)

    def _fetch_series(
        self,
        series_id: str,
        start_date: Optional[str] = None,
        end_date: Optional[str] = None,
    ) -> pd.DataFrame:
        """
        Fetch a FRED series and return as DataFrame.

        Args:
            series_id: FRED series ID
            start_date: Start date in YYYY-MM-DD format
            end_date: End date in YYYY-MM-DD format

        Returns:
            DataFrame with the series data
        """
        data = self.fred.get_series(
            series_id,
            observation_start=start_date,
            observation_end=end_date,
        )
        return pd.DataFrame({series_id: data})

    def get_gdp(
        self,
        start_date: Optional[str] = None,
        end_date: Optional[str] = None,
    ) -> pd.DataFrame:
        """
        Fetch GDP data.

        Args:
            start_date: Start date in YYYY-MM-DD format
            end_date: End date in YYYY-MM-DD format

        Returns:
            DataFrame with GDP data (quarterly)
        """
        return self._fetch_series(self.SERIES_IDS["gdp"], start_date, end_date)

    def get_gdp_growth(
        self,
        start_date: Optional[str] = None,
        end_date: Optional[str] = None,
    ) -> pd.DataFrame:
        """
        Fetch GDP growth rate data.

        Args:
            start_date: Start date in YYYY-MM-DD format
            end_date: End date in YYYY-MM-DD format

        Returns:
            DataFrame with GDP growth rate (quarterly, annualized)
        """
        return self._fetch_series(self.SERIES_IDS["gdp_growth"], start_date, end_date)

    def get_cpi(
        self,
        start_date: Optional[str] = None,
        end_date: Optional[str] = None,
        core: bool = False,
    ) -> pd.DataFrame:
        """
        Fetch Consumer Price Index (CPI) data.

        Args:
            start_date: Start date in YYYY-MM-DD format
            end_date: End date in YYYY-MM-DD format
            core: If True, fetch core CPI (excluding food and energy)

        Returns:
            DataFrame with CPI data (monthly)
        """
        series_key = "core_cpi" if core else "cpi"
        return self._fetch_series(self.SERIES_IDS[series_key], start_date, end_date)

    def get_inflation_rate(
        self,
        start_date: Optional[str] = None,
        end_date: Optional[str] = None,
        core: bool = False,
    ) -> pd.DataFrame:
        """
        Calculate year-over-year inflation rate from CPI.

        Args:
            start_date: Start date in YYYY-MM-DD format
            end_date: End date in YYYY-MM-DD format
            core: If True, use core CPI

        Returns:
            DataFrame with inflation rate (%)
        """
        cpi = self.get_cpi(start_date, end_date, core)
        series_key = "core_cpi" if core else "cpi"
        series_id = self.SERIES_IDS[series_key]

        inflation = cpi[series_id].pct_change(periods=12) * 100
        return pd.DataFrame({"inflation_rate": inflation})

    def get_ppi(
        self,
        start_date: Optional[str] = None,
        end_date: Optional[str] = None,
    ) -> pd.DataFrame:
        """
        Fetch Producer Price Index (PPI) data.

        Args:
            start_date: Start date in YYYY-MM-DD format
            end_date: End date in YYYY-MM-DD format

        Returns:
            DataFrame with PPI data (monthly)
        """
        return self._fetch_series(self.SERIES_IDS["ppi"], start_date, end_date)

    def get_unemployment_rate(
        self,
        start_date: Optional[str] = None,
        end_date: Optional[str] = None,
    ) -> pd.DataFrame:
        """
        Fetch unemployment rate data.

        Args:
            start_date: Start date in YYYY-MM-DD format
            end_date: End date in YYYY-MM-DD format

        Returns:
            DataFrame with unemployment rate (monthly, %)
        """
        return self._fetch_series(self.SERIES_IDS["unemployment"], start_date, end_date)

    def get_interest_rates(
        self,
        start_date: Optional[str] = None,
        end_date: Optional[str] = None,
        rate_type: str = "fed_funds",
    ) -> pd.DataFrame:
        """
        Fetch interest rate data.

        Args:
            start_date: Start date in YYYY-MM-DD format
            end_date: End date in YYYY-MM-DD format
            rate_type: Type of rate ("fed_funds" or "treasury_10y")

        Returns:
            DataFrame with interest rate data (%)
        """
        if rate_type not in ["fed_funds", "treasury_10y"]:
            raise ValueError("rate_type must be 'fed_funds' or 'treasury_10y'")
        return self._fetch_series(self.SERIES_IDS[rate_type], start_date, end_date)

    def get_housing_starts(
        self,
        start_date: Optional[str] = None,
        end_date: Optional[str] = None,
    ) -> pd.DataFrame:
        """
        Fetch housing starts data.

        Args:
            start_date: Start date in YYYY-MM-DD format
            end_date: End date in YYYY-MM-DD format

        Returns:
            DataFrame with housing starts (monthly, thousands of units)
        """
        return self._fetch_series(self.SERIES_IDS["housing_starts"], start_date, end_date)

    def get_multiple_indicators(
        self,
        indicators: list[str],
        start_date: Optional[str] = None,
        end_date: Optional[str] = None,
    ) -> pd.DataFrame:
        """
        Fetch multiple indicators at once.

        Args:
            indicators: List of indicator names (keys from SERIES_IDS)
            start_date: Start date in YYYY-MM-DD format
            end_date: End date in YYYY-MM-DD format

        Returns:
            DataFrame with multiple indicators
        """
        dfs = []
        for indicator in indicators:
            if indicator not in self.SERIES_IDS:
                raise ValueError(
                    f"Unknown indicator: {indicator}. Available: {list(self.SERIES_IDS.keys())}"
                )
            data = self._fetch_series(self.SERIES_IDS[indicator], start_date, end_date)
            dfs.append(data)

        return pd.concat(dfs, axis=1)
