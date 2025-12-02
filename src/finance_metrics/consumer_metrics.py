"""
Consumer Metrics

Fetch and process consumer-related economic indicators:
- Consumer Confidence Index
- Retail Sales
- Personal Consumption Expenditures
- Consumer Sentiment Index
- Disposable Personal Income
"""

import os
from datetime import datetime
from typing import Optional

import pandas as pd
from dotenv import load_dotenv
from fredapi import Fred

# Load environment variables
load_dotenv()


class ConsumerMetrics:
    """Fetch and process consumer economic metrics from FRED."""

    # FRED series IDs for consumer-related indicators
    SERIES_IDS = {
        "consumer_sentiment": "UMCSENT",  # University of Michigan Consumer Sentiment
        "consumer_confidence": "CSCICP03USM665S",  # OECD Consumer Confidence Index
        "retail_sales": "RSXFS",  # Retail Sales (excluding food services)
        "retail_sales_total": "RSAFS",  # Retail and Food Services Sales
        "pce": "PCE",  # Personal Consumption Expenditures
        "pce_real": "PCEC96",  # Real PCE
        "disposable_income": "DPI",  # Disposable Personal Income
        "real_disposable_income": "DSPIC96",  # Real Disposable Personal Income
        "personal_saving_rate": "PSAVERT",  # Personal Saving Rate
        "consumer_credit": "TOTALSL",  # Total Consumer Credit Outstanding
    }

    def __init__(self, api_key: Optional[str] = None):
        """
        Initialize ConsumerMetrics.

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

    def get_consumer_sentiment(
        self,
        start_date: Optional[str] = None,
        end_date: Optional[str] = None,
    ) -> pd.DataFrame:
        """
        Fetch University of Michigan Consumer Sentiment Index.

        Args:
            start_date: Start date in YYYY-MM-DD format
            end_date: End date in YYYY-MM-DD format

        Returns:
            DataFrame with consumer sentiment data (monthly)
        """
        return self._fetch_series(
            self.SERIES_IDS["consumer_sentiment"], start_date, end_date
        )

    def get_consumer_confidence(
        self,
        start_date: Optional[str] = None,
        end_date: Optional[str] = None,
    ) -> pd.DataFrame:
        """
        Fetch OECD Consumer Confidence Index for the US.

        Args:
            start_date: Start date in YYYY-MM-DD format
            end_date: End date in YYYY-MM-DD format

        Returns:
            DataFrame with consumer confidence data (monthly)
        """
        return self._fetch_series(
            self.SERIES_IDS["consumer_confidence"], start_date, end_date
        )

    def get_retail_sales(
        self,
        start_date: Optional[str] = None,
        end_date: Optional[str] = None,
        include_food_services: bool = False,
    ) -> pd.DataFrame:
        """
        Fetch retail sales data.

        Args:
            start_date: Start date in YYYY-MM-DD format
            end_date: End date in YYYY-MM-DD format
            include_food_services: If True, include food services sales

        Returns:
            DataFrame with retail sales data (monthly, millions of dollars)
        """
        series_key = "retail_sales_total" if include_food_services else "retail_sales"
        return self._fetch_series(self.SERIES_IDS[series_key], start_date, end_date)

    def get_retail_sales_growth(
        self,
        start_date: Optional[str] = None,
        end_date: Optional[str] = None,
        include_food_services: bool = False,
    ) -> pd.DataFrame:
        """
        Calculate year-over-year retail sales growth rate.

        Args:
            start_date: Start date in YYYY-MM-DD format
            end_date: End date in YYYY-MM-DD format
            include_food_services: If True, include food services sales

        Returns:
            DataFrame with retail sales growth rate (%)
        """
        sales = self.get_retail_sales(start_date, end_date, include_food_services)
        series_key = "retail_sales_total" if include_food_services else "retail_sales"
        series_id = self.SERIES_IDS[series_key]

        growth = sales[series_id].pct_change(periods=12) * 100
        return pd.DataFrame({"retail_sales_growth": growth})

    def get_pce(
        self,
        start_date: Optional[str] = None,
        end_date: Optional[str] = None,
        real: bool = False,
    ) -> pd.DataFrame:
        """
        Fetch Personal Consumption Expenditures data.

        Args:
            start_date: Start date in YYYY-MM-DD format
            end_date: End date in YYYY-MM-DD format
            real: If True, fetch real (inflation-adjusted) PCE

        Returns:
            DataFrame with PCE data (monthly)
        """
        series_key = "pce_real" if real else "pce"
        return self._fetch_series(self.SERIES_IDS[series_key], start_date, end_date)

    def get_disposable_income(
        self,
        start_date: Optional[str] = None,
        end_date: Optional[str] = None,
        real: bool = False,
    ) -> pd.DataFrame:
        """
        Fetch Disposable Personal Income data.

        Args:
            start_date: Start date in YYYY-MM-DD format
            end_date: End date in YYYY-MM-DD format
            real: If True, fetch real (inflation-adjusted) disposable income

        Returns:
            DataFrame with disposable income data (monthly)
        """
        series_key = "real_disposable_income" if real else "disposable_income"
        return self._fetch_series(self.SERIES_IDS[series_key], start_date, end_date)

    def get_personal_saving_rate(
        self,
        start_date: Optional[str] = None,
        end_date: Optional[str] = None,
    ) -> pd.DataFrame:
        """
        Fetch Personal Saving Rate.

        Args:
            start_date: Start date in YYYY-MM-DD format
            end_date: End date in YYYY-MM-DD format

        Returns:
            DataFrame with personal saving rate (monthly, %)
        """
        return self._fetch_series(
            self.SERIES_IDS["personal_saving_rate"], start_date, end_date
        )

    def get_consumer_credit(
        self,
        start_date: Optional[str] = None,
        end_date: Optional[str] = None,
    ) -> pd.DataFrame:
        """
        Fetch total consumer credit outstanding.

        Args:
            start_date: Start date in YYYY-MM-DD format
            end_date: End date in YYYY-MM-DD format

        Returns:
            DataFrame with consumer credit data (monthly, billions of dollars)
        """
        return self._fetch_series(
            self.SERIES_IDS["consumer_credit"], start_date, end_date
        )

    def get_multiple_metrics(
        self,
        metrics: list[str],
        start_date: Optional[str] = None,
        end_date: Optional[str] = None,
    ) -> pd.DataFrame:
        """
        Fetch multiple consumer metrics at once.

        Args:
            metrics: List of metric names (keys from SERIES_IDS)
            start_date: Start date in YYYY-MM-DD format
            end_date: End date in YYYY-MM-DD format

        Returns:
            DataFrame with multiple consumer metrics
        """
        dfs = []
        for metric in metrics:
            if metric not in self.SERIES_IDS:
                raise ValueError(
                    f"Unknown metric: {metric}. Available: {list(self.SERIES_IDS.keys())}"
                )
            data = self._fetch_series(self.SERIES_IDS[metric], start_date, end_date)
            dfs.append(data)

        return pd.concat(dfs, axis=1)
