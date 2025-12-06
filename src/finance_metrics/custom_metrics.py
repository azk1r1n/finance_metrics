"""
Custom Metrics

Custom financial metrics and technical indicators for retail demand forecasting.

This module contains 6 MeiTou custom metrics designed for weekly retail forecasting:
1. QQQ 200 Days Deviation Index - Nasdaq-100 trend strength
2. Market Breadth Index - Market participation and health
3. VIX Fear & Greed Index - Market volatility sentiment
4. Sector Rotation Index - Economic sector momentum
5. Volume Momentum Index - Trading volume trends
6. Multi-Timeframe Momentum - Cross-timeframe trend analysis
"""

from typing import Optional, Tuple

import pandas as pd
import yfinance as yf


class CustomMetrics:
    """Calculate custom financial metrics and technical indicators."""

    def __init__(self):
        """Initialize CustomMetrics."""
        pass

    # ============================================================================
    # COMMON UTILITY METHODS
    # ============================================================================

    def _fetch_ticker_data(
        self,
        ticker: str,
        start_date: Optional[str] = None,
        end_date: Optional[str] = None,
    ) -> pd.DataFrame:
        """
        Fetch ticker data from yfinance with standard error handling.

        Args:
            ticker: Ticker symbol
            start_date: Start date in YYYY-MM-DD format
            end_date: End date in YYYY-MM-DD format

        Returns:
            DataFrame with OHLCV data
        """
        data = yf.download(
            ticker,
            start=start_date,
            end=end_date,
            progress=False,
            auto_adjust=True,
        )

        # Handle MultiIndex columns
        if isinstance(data.columns, pd.MultiIndex):
            data.columns = data.columns.get_level_values(0)

        return data

    def _normalize_to_scale(
        self,
        values: pd.Series,
        calibration_data: pd.Series,
        lower_percentile: float = 1.0,
        upper_percentile: float = 99.0,
        use_percentiles: bool = True,
    ) -> pd.Series:
        """
        Normalize values to 0-100 scale using historical calibration data.

        Args:
            values: Series to normalize
            calibration_data: Historical data for establishing bounds
            lower_percentile: Lower percentile for normalization
            upper_percentile: Upper percentile for normalization
            use_percentiles: Use percentiles vs raw min/max

        Returns:
            Normalized series (0-100 scale)
        """
        valid_calibration = calibration_data.dropna()

        if use_percentiles:
            lower_bound = valid_calibration.quantile(lower_percentile / 100)
            upper_bound = valid_calibration.quantile(upper_percentile / 100)
        else:
            lower_bound = valid_calibration.min()
            upper_bound = valid_calibration.max()

        # Normalize
        normalized = (values - lower_bound) / (upper_bound - lower_bound) * 100

        # Clip to 0-100 range
        return normalized.clip(0, 100)

    def _generate_signal(
        self,
        values: pd.Series,
        thresholds: Tuple[float, float, float, float],
    ) -> pd.Series:
        """
        Generate trading signals based on threshold values.

        Args:
            values: Values to generate signals for
            thresholds: (strong_bearish, bearish, bullish, strong_bullish) thresholds

        Returns:
            Series with signal labels
        """
        strong_bearish, bearish, bullish, strong_bullish = thresholds

        def get_signal(value):
            if pd.isna(value):
                return "Insufficient Data"
            elif value >= strong_bullish:
                return "Strong Bullish"
            elif value >= bullish:
                return "Bullish"
            elif value <= strong_bearish:
                return "Strong Bearish"
            else:
                return "Bearish"

        return values.apply(get_signal)

    def _calculate_stats(self, data: pd.Series) -> dict:
        """
        Calculate statistical summary for a metric.

        Args:
            data: Series to calculate stats for

        Returns:
            Dictionary with statistical metrics
        """
        valid_data = data.dropna()

        if len(valid_data) == 0:
            return {
                "mean": None,
                "median": None,
                "std": None,
                "min": None,
                "max": None,
                "current": None,
            }

        return {
            "mean": valid_data.mean(),
            "median": valid_data.median(),
            "std": valid_data.std(),
            "min": valid_data.min(),
            "max": valid_data.max(),
            "current": valid_data.iloc[-1],
        }

    # ============================================================================
    # METRIC 1: QQQ 200 DAYS DEVIATION INDEX
    # ============================================================================

    def get_meitou_qqq_deviation(
        self,
        start_date: Optional[str] = None,
        end_date: Optional[str] = None,
        sma_period: int = 200,
    ) -> pd.DataFrame:
        """
        Calculate MeiTou QQQ 200 Days Deviation Index.

        Measures how far QQQ (Nasdaq-100 ETF) is trading from its 200-day SMA.

        Formula:
            Deviation = (QQQ price - SMA_200) / SMA_200

        Args:
            start_date: Start date in YYYY-MM-DD format
            end_date: End date in YYYY-MM-DD format
            sma_period: Period for simple moving average (default: 200 days)

        Returns:
            DataFrame with columns: Close, SMA_200, Deviation, Signal
        """
        qqq = self._fetch_ticker_data("QQQ", start_date, end_date)

        # Calculate SMA
        sma_col = f"SMA_{sma_period}"
        qqq[sma_col] = qqq["Close"].rolling(window=sma_period).mean()

        # Calculate deviation
        qqq["Deviation"] = (qqq["Close"] - qqq[sma_col]) / qqq[sma_col]

        # Generate signals (thresholds: -5%, 0%, 0%, 5%)
        qqq["Signal"] = self._generate_signal(qqq["Deviation"], (-0.05, 0, 0, 0.05))

        return qqq[["Close", sma_col, "Deviation", "Signal"]].copy()

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

        Uses historical data since 2015-01 to establish normalization bounds.

        Args:
            start_date: Start date for output
            end_date: End date for output
            sma_period: SMA period
            calibration_start: Start date for calibration (default: 2015-01-01)
            use_percentiles: Use percentiles vs min/max
            lower_percentile: Lower percentile (default: 1.0)
            upper_percentile: Upper percentile (default: 99.0)

        Returns:
            DataFrame with normalized deviation (0-100 scale)
        """
        # Get calibration data
        calibration_data = self.get_meitou_qqq_deviation(
            calibration_start, end_date, sma_period
        )

        # Get output data
        result = self.get_meitou_qqq_deviation(start_date, end_date, sma_period)

        # Normalize
        result["Deviation_Normalized"] = self._normalize_to_scale(
            result["Deviation"],
            calibration_data["Deviation"],
            lower_percentile,
            upper_percentile,
            use_percentiles,
        )

        # Update signals based on normalized values
        result["Signal"] = self._generate_signal(
            result["Deviation_Normalized"], (30, 50, 50, 70)
        )

        return result

    def get_meitou_qqq_deviation_weekly(
        self,
        start_date: Optional[str] = None,
        end_date: Optional[str] = None,
        sma_period: int = 200,
    ) -> pd.DataFrame:
        """
        Calculate weekly aggregated QQQ Deviation Index.

        Args:
            start_date: Start date
            end_date: End date
            sma_period: SMA period

        Returns:
            Weekly aggregated DataFrame
        """
        daily = self.get_meitou_qqq_deviation(start_date, end_date, sma_period)

        weekly = daily.resample("W").agg(
            {
                "Close": "last",
                f"SMA_{sma_period}": "last",
                "Deviation": "last",
            }
        )

        weekly["Signal"] = self._generate_signal(
            weekly["Deviation"], (-0.05, 0, 0, 0.05)
        )

        return weekly

    # ============================================================================
    # METRIC 2: MEITOU PUT/CALL RATIO INDEX
    # ============================================================================

    def get_put_call_ratio(
        self,
        start_date: Optional[str] = None,
        end_date: Optional[str] = None,
        ticker: str = "^CPCE",
    ) -> pd.DataFrame:
        """
        Calculate Put/Call Ratio as a market sentiment indicator.

        The Put/Call Ratio measures the ratio of put option volume to call option
        volume. It's a contrarian indicator:
        - High ratio (>1.0): Bearish sentiment → Potentially bullish signal (oversold)
        - Low ratio (<0.7): Bullish sentiment → Potentially bearish signal (overbought)

        Uses CBOE Equity Put/Call Ratio (^CPCE) by default.

        Formula:
            Ratio = Put Volume / Call Volume

        Args:
            start_date: Start date in YYYY-MM-DD format
            end_date: End date in YYYY-MM-DD format
            ticker: Put/Call ratio ticker (default: ^CPCE = CBOE Equity Put/Call)

        Returns:
            DataFrame with columns: PutCallRatio, Signal
        """
        data = self._fetch_ticker_data(ticker, start_date, end_date)

        # Rename Close to PutCallRatio for clarity
        result = pd.DataFrame({"PutCallRatio": data["Close"]})

        # Generate signals (contrarian interpretation)
        # Thresholds: (<0.5: Strong Bearish, 0.5-0.7: Bearish, 0.9-1.2: Bullish, >1.2: Strong Bullish)
        result["Signal"] = self._generate_signal(
            result["PutCallRatio"], (0.5, 0.7, 0.9, 1.2)
        )

        return result

    def get_put_call_ratio_normalized(
        self,
        start_date: Optional[str] = None,
        end_date: Optional[str] = None,
        ticker: str = "^CPCE",
        calibration_start: str = "2015-01-01",
        use_percentiles: bool = True,
        lower_percentile: float = 1.0,
        upper_percentile: float = 99.0,
    ) -> pd.DataFrame:
        """
        Calculate normalized Put/Call Ratio (0-100 scale).

        Uses historical data since 2015-01 to establish normalization bounds.
        Higher normalized values indicate higher put/call ratio (more bearish sentiment).

        Args:
            start_date: Start date for output
            end_date: End date for output
            ticker: Put/Call ratio ticker (default: ^CPCE)
            calibration_start: Start date for calibration (default: 2015-01-01)
            use_percentiles: Use percentiles vs min/max
            lower_percentile: Lower percentile (default: 1.0)
            upper_percentile: Upper percentile (default: 99.0)

        Returns:
            DataFrame with normalized Put/Call ratio (0-100 scale)
        """
        # Get calibration data
        calibration_data = self.get_put_call_ratio(calibration_start, end_date, ticker)

        # Get output data
        result = self.get_put_call_ratio(start_date, end_date, ticker)

        # Normalize
        result["PutCallRatio_Normalized"] = self._normalize_to_scale(
            result["PutCallRatio"],
            calibration_data["PutCallRatio"],
            lower_percentile,
            upper_percentile,
            use_percentiles,
        )

        # Update signals based on normalized values
        # Higher normalized values = higher put/call ratio = more bearish sentiment = bullish signal (contrarian)
        result["Signal"] = self._generate_signal(
            result["PutCallRatio_Normalized"], (30, 40, 60, 70)
        )

        return result

    def get_put_call_ratio_weekly(
        self,
        start_date: Optional[str] = None,
        end_date: Optional[str] = None,
        ticker: str = "^CPCE",
    ) -> pd.DataFrame:
        """
        Calculate weekly aggregated Put/Call Ratio.

        Uses mean aggregation for weekly values as the ratio should be averaged
        across the week rather than taking last value.

        Args:
            start_date: Start date
            end_date: End date
            ticker: Put/Call ratio ticker (default: ^CPCE)

        Returns:
            Weekly aggregated DataFrame
        """
        daily = self.get_put_call_ratio(start_date, end_date, ticker)

        weekly = daily.resample("W").agg({"PutCallRatio": "mean"})

        weekly["Signal"] = self._generate_signal(
            weekly["PutCallRatio"], (0.5, 0.7, 0.9, 1.2)
        )

        return weekly

    # ============================================================================
    # METRIC 3: VIX FEAR & GREED INDEX (PLACEHOLDER)
    # ============================================================================

    def get_vix_fear_greed_index(
        self,
        start_date: Optional[str] = None,
        end_date: Optional[str] = None,
    ) -> pd.DataFrame:
        """
        Calculate VIX-based Fear & Greed Index.

        Combines VIX levels with VIX term structure to gauge market sentiment.

        TODO: Implement VIX sentiment analysis
        - VIX spot level
        - VIX term structure (contango/backwardation)
        - VIX percentile ranking

        Args:
            start_date: Start date
            end_date: End date

        Returns:
            DataFrame with VIX sentiment metrics
        """
        raise NotImplementedError(
            "VIX Fear & Greed Index not yet implemented. "
            "Will measure market volatility and sentiment."
        )

    # ============================================================================
    # METRIC 4: SECTOR ROTATION INDEX (PLACEHOLDER)
    # ============================================================================

    def get_sector_rotation_index(
        self,
        start_date: Optional[str] = None,
        end_date: Optional[str] = None,
    ) -> pd.DataFrame:
        """
        Calculate Sector Rotation Index.

        Tracks momentum across economic sectors to identify leadership changes.

        TODO: Implement sector rotation analysis
        - 11 GICS sectors performance
        - Relative strength vs S&P 500
        - Sector momentum rankings

        Args:
            start_date: Start date
            end_date: End date

        Returns:
            DataFrame with sector rotation metrics
        """
        raise NotImplementedError(
            "Sector Rotation Index not yet implemented. "
            "Will track economic sector momentum and rotation."
        )

    # ============================================================================
    # METRIC 5: VOLUME MOMENTUM INDEX (PLACEHOLDER)
    # ============================================================================

    def get_volume_momentum_index(
        self,
        start_date: Optional[str] = None,
        end_date: Optional[str] = None,
    ) -> pd.DataFrame:
        """
        Calculate Volume Momentum Index.

        Analyzes trading volume patterns to confirm price trends.

        TODO: Implement volume analysis
        - On-balance volume (OBV)
        - Volume-weighted trends
        - Volume breakouts

        Args:
            start_date: Start date
            end_date: End date

        Returns:
            DataFrame with volume momentum metrics
        """
        raise NotImplementedError(
            "Volume Momentum Index not yet implemented. "
            "Will analyze trading volume trends."
        )

    # ============================================================================
    # METRIC 6: MULTI-TIMEFRAME MOMENTUM (PLACEHOLDER)
    # ============================================================================

    def get_multi_timeframe_momentum(
        self,
        start_date: Optional[str] = None,
        end_date: Optional[str] = None,
    ) -> pd.DataFrame:
        """
        Calculate Multi-Timeframe Momentum Index.

        Combines momentum signals across multiple timeframes (short/medium/long).

        TODO: Implement multi-timeframe analysis
        - 50-day, 100-day, 200-day trends
        - Cross-timeframe alignment
        - Momentum convergence/divergence

        Args:
            start_date: Start date
            end_date: End date

        Returns:
            DataFrame with multi-timeframe momentum metrics
        """
        raise NotImplementedError(
            "Multi-Timeframe Momentum Index not yet implemented. "
            "Will analyze trends across multiple timeframes."
        )

    # ============================================================================
    # STATISTICS AND UTILITIES
    # ============================================================================

    def get_deviation_stats(
        self,
        start_date: Optional[str] = None,
        end_date: Optional[str] = None,
    ) -> dict:
        """
        Get statistical summary of the MeiTou QQQ Deviation Index.

        Args:
            start_date: Start date
            end_date: End date

        Returns:
            Dictionary with statistical metrics
        """
        data = self.get_meitou_qqq_deviation(start_date, end_date)
        stats = self._calculate_stats(data["Deviation"])

        # Add percentage analysis
        valid_deviations = data["Deviation"].dropna()
        stats["pct_bullish"] = (
            (valid_deviations > 0).sum() / len(valid_deviations) * 100
            if len(valid_deviations) > 0
            else 0
        )
        stats["pct_bearish"] = (
            (valid_deviations < 0).sum() / len(valid_deviations) * 100
            if len(valid_deviations) > 0
            else 0
        )

        return stats

    def get_put_call_ratio_stats(
        self,
        start_date: Optional[str] = None,
        end_date: Optional[str] = None,
        ticker: str = "^CPCE",
    ) -> dict:
        """
        Get statistical summary of the Put/Call Ratio.

        Args:
            start_date: Start date
            end_date: End date
            ticker: Put/Call ratio ticker (default: ^CPCE)

        Returns:
            Dictionary with statistical metrics
        """
        data = self.get_put_call_ratio(start_date, end_date, ticker)
        stats = self._calculate_stats(data["PutCallRatio"])

        # Add sentiment analysis
        valid_ratios = data["PutCallRatio"].dropna()
        stats["pct_bullish_signal"] = (
            (valid_ratios > 0.9).sum() / len(valid_ratios) * 100
            if len(valid_ratios) > 0
            else 0
        )
        stats["pct_bearish_signal"] = (
            (valid_ratios < 0.7).sum() / len(valid_ratios) * 100
            if len(valid_ratios) > 0
            else 0
        )
        stats["pct_neutral"] = (
            ((valid_ratios >= 0.7) & (valid_ratios <= 0.9)).sum()
            / len(valid_ratios)
            * 100
            if len(valid_ratios) > 0
            else 0
        )

        return stats
