"""
Custom Metrics

Custom financial metrics and technical indicators for retail demand forecasting:
- MeiTou QQQ 200 Days Deviation Index
- Additional custom metrics as needed
"""

from typing import Optional

import pandas as pd
import yfinance as yf


class CustomMetrics:
    """Calculate custom financial metrics and technical indicators."""

    def __init__(self):
        """Initialize CustomMetrics."""
        pass

    def get_meitou_qqq_deviation(
        self,
        start_date: Optional[str] = None,
        end_date: Optional[str] = None,
        sma_period: int = 200,
    ) -> pd.DataFrame:
        """
        Calculate MeiTou QQQ 200 Days Deviation Index.

        This metric measures how far QQQ (Nasdaq-100 ETF) is trading from its
        200-day simple moving average, normalized by the SMA value.

        Formula:
            Deviation = (QQQ price - SMA_200) / SMA_200

        Args:
            start_date: Start date in YYYY-MM-DD format
            end_date: End date in YYYY-MM-DD format
            sma_period: Period for simple moving average (default: 200 days)

        Returns:
            DataFrame with columns:
                - Close: QQQ closing price
                - SMA_{period}: Simple moving average
                - Deviation: Percentage deviation from SMA
                - Signal: Trading signal (Bullish/Bearish/Neutral)

        Interpretation:
            - Positive deviation: QQQ is above its trend (bullish momentum)
            - Negative deviation: QQQ is below its trend (bearish momentum)
            - Larger absolute values: stronger trend divergence
        """
        # Fetch QQQ data
        # Note: Need extra data for SMA calculation
        qqq = yf.download(
            "QQQ",
            start=start_date,
            end=end_date,
            progress=False,
            auto_adjust=True,
        )

        # Handle MultiIndex columns if they exist
        if isinstance(qqq.columns, pd.MultiIndex):
            qqq.columns = qqq.columns.get_level_values(0)

        # Calculate SMA
        sma_col = f"SMA_{sma_period}"
        qqq[sma_col] = qqq["Close"].rolling(window=sma_period).mean()

        # Calculate deviation (percentage)
        qqq["Deviation"] = (qqq["Close"] - qqq[sma_col]) / qqq[sma_col]

        # Add trading signal based on deviation
        def get_signal(deviation):
            if pd.isna(deviation):
                return "Insufficient Data"
            elif deviation > 0.05:  # > 5% above SMA
                return "Strong Bullish"
            elif deviation > 0:
                return "Bullish"
            elif deviation < -0.05:  # > 5% below SMA
                return "Strong Bearish"
            else:
                return "Bearish"

        qqq["Signal"] = qqq["Deviation"].apply(get_signal)

        # Select relevant columns
        result = qqq[["Close", sma_col, "Deviation", "Signal"]].copy()

        return result

    def get_meitou_qqq_deviation_weekly(
        self,
        start_date: Optional[str] = None,
        end_date: Optional[str] = None,
        sma_period: int = 200,
    ) -> pd.DataFrame:
        """
        Calculate MeiTou QQQ 200 Days Deviation Index with weekly aggregation.

        This is useful for aligning with weekly retail demand forecasting.

        Args:
            start_date: Start date in YYYY-MM-DD format
            end_date: End date in YYYY-MM-DD format
            sma_period: Period for simple moving average (default: 200 days)

        Returns:
            DataFrame with weekly aggregated deviation metrics
        """
        # Get daily deviation
        daily_deviation = self.get_meitou_qqq_deviation(
            start_date, end_date, sma_period
        )

        # Aggregate to weekly
        weekly = daily_deviation.resample("W").agg(
            {
                "Close": "last",
                f"SMA_{sma_period}": "last",
                "Deviation": "last",  # Use end-of-week value
            }
        )

        # Recalculate signal for weekly data
        def get_signal(deviation):
            if pd.isna(deviation):
                return "Insufficient Data"
            elif deviation > 0.05:
                return "Strong Bullish"
            elif deviation > 0:
                return "Bullish"
            elif deviation < -0.05:
                return "Strong Bearish"
            else:
                return "Bearish"

        weekly["Signal"] = weekly["Deviation"].apply(get_signal)

        return weekly

    def get_meitou_qqq_deviation_normalized(
        self,
        start_date: Optional[str] = None,
        end_date: Optional[str] = None,
        sma_period: int = 200,
        calibration_start: str = "2015-01-01",
        use_percentiles: bool = True,
        lower_percentile: float = 1.0,
        upper_percentile: float = 99.0,
    ) -> pd.DataFrame:
        """
        Calculate normalized MeiTou QQQ Deviation Index (0-100 scale).

        Uses historical data since 2015-01 to establish normalization bounds,
        then maps deviation to 0-100 scale.

        Formula:
            Normalized = (Deviation - Lower_Bound) / (Upper_Bound - Lower_Bound) * 100

        Args:
            start_date: Start date for output data in YYYY-MM-DD format
            end_date: End date for output data in YYYY-MM-DD format
            sma_period: Period for simple moving average (default: 200 days)
            calibration_start: Start date for calculating normalization bounds (default: 2015-01-01)
            use_percentiles: If True, use percentiles for bounds; if False, use raw min/max (default: True)
            lower_percentile: Lower percentile for normalization (default: 1.0)
            upper_percentile: Upper percentile for normalization (default: 99.0)

        Returns:
            DataFrame with columns:
                - Close: QQQ closing price
                - SMA_200: Simple moving average
                - Deviation: Raw percentage deviation
                - Deviation_Normalized: Normalized deviation (0-100 scale)
                - Signal: Trading signal

        Interpretation:
            - 0-30: Strong bearish territory
            - 30-50: Bearish/neutral territory
            - 50-70: Bullish/neutral territory
            - 70-100: Strong bullish territory
        """
        # Fetch calibration data to establish bounds
        calibration_data = self.get_meitou_qqq_deviation(
            start_date=calibration_start,
            end_date=end_date,
            sma_period=sma_period,
        )

        # Calculate bounds from historical data
        valid_deviations = calibration_data["Deviation"].dropna()

        if use_percentiles:
            lower_bound = valid_deviations.quantile(lower_percentile / 100)
            upper_bound = valid_deviations.quantile(upper_percentile / 100)
        else:
            lower_bound = valid_deviations.min()
            upper_bound = valid_deviations.max()

        # Fetch data for requested period
        result = self.get_meitou_qqq_deviation(
            start_date=start_date,
            end_date=end_date,
            sma_period=sma_period,
        )

        # Normalize to 0-100 scale
        result["Deviation_Normalized"] = (
            (result["Deviation"] - lower_bound) / (upper_bound - lower_bound) * 100
        )

        # Clip to 0-100 range (in case values exceed historical bounds)
        result["Deviation_Normalized"] = result["Deviation_Normalized"].clip(0, 100)

        # Update signal based on normalized values
        def get_signal_normalized(norm_value):
            if pd.isna(norm_value):
                return "Insufficient Data"
            elif norm_value >= 70:
                return "Strong Bullish"
            elif norm_value >= 50:
                return "Bullish"
            elif norm_value >= 30:
                return "Bearish"
            else:
                return "Strong Bearish"

        result["Signal"] = result["Deviation_Normalized"].apply(get_signal_normalized)

        return result

    def get_deviation_stats(
        self,
        start_date: Optional[str] = None,
        end_date: Optional[str] = None,
    ) -> dict:
        """
        Get statistical summary of the MeiTou QQQ Deviation Index.

        Args:
            start_date: Start date in YYYY-MM-DD format
            end_date: End date in YYYY-MM-DD format

        Returns:
            Dictionary with statistical metrics
        """
        deviation_data = self.get_meitou_qqq_deviation(start_date, end_date)

        # Filter out NaN values
        valid_deviations = deviation_data["Deviation"].dropna()

        stats = {
            "mean_deviation": valid_deviations.mean(),
            "median_deviation": valid_deviations.median(),
            "std_deviation": valid_deviations.std(),
            "min_deviation": valid_deviations.min(),
            "max_deviation": valid_deviations.max(),
            "current_deviation": valid_deviations.iloc[-1]
            if len(valid_deviations) > 0
            else None,
            "pct_bullish": (valid_deviations > 0).sum() / len(valid_deviations) * 100,
            "pct_bearish": (valid_deviations < 0).sum() / len(valid_deviations) * 100,
        }

        return stats
