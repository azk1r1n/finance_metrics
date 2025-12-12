"""
Example: Integrating VIX Sentiment into CustomMetrics

This shows how to add VIX sentiment as a MeiTou custom metric
alongside your existing QQQ 200 Days Deviation Index.

Copy the relevant methods to your custom_metrics.py file.
"""

from typing import Optional
import pandas as pd
from vix_sentiment import VIXSentiment


class CustomMetricsExample:
    """
    Example integration of VIX sentiment with existing CustomMetrics architecture.

    This demonstrates how VIX sentiment fits into your existing pattern:
    - Daily version (base)
    - Normalized version (0-100 scale)
    - Weekly version (for retail forecasting)
    """

    def __init__(self):
        """Initialize custom metrics."""
        self.vix_calculator = VIXSentiment()

    # ========================================================================
    # EXISTING UTILITY METHODS (from your custom_metrics.py)
    # ========================================================================

    def _generate_signal(
        self,
        values: pd.Series,
        thresholds: tuple,
    ) -> pd.Series:
        """
        Generate trading signals based on threshold levels.

        (This is a simplified version - use your actual implementation)
        """
        signals = pd.Series(index=values.index, dtype=str)

        t1, t2, t3, t4 = thresholds

        signals[values <= t1] = "Strong Bearish"
        signals[(values > t1) & (values <= t2)] = "Bearish"
        signals[(values > t2) & (values <= t3)] = "Bullish"
        signals[(values > t3) & (values <= t4)] = "Strong Bullish"
        signals[values > t4] = "Strong Bullish"

        return signals

    # ========================================================================
    # NEW: VIX SENTIMENT METHODS
    # ========================================================================

    def get_vix_sentiment(
        self,
        start_date: Optional[str] = None,
        end_date: Optional[str] = None,
    ) -> pd.DataFrame:
        """
        Calculate VIX-based market sentiment indicator.

        VIX serves as a free proxy for put/call ratios. High VIX indicates
        fear (bearish), similar to high put/call ratios. Low VIX indicates
        complacency (bullish), similar to low put/call ratios.

        Formula: VIX closing levels with sentiment interpretation

        Args:
            start_date: Start date in YYYY-MM-DD format
            end_date: End date in YYYY-MM-DD format

        Returns:
            DataFrame with VIX levels, sentiment scores, and signals

        Example:
            >>> metrics = CustomMetrics()
            >>> vix = metrics.get_vix_sentiment("2024-01-01", "2024-12-31")
            >>> print(vix.tail())
        """
        df = self.vix_calculator.calculate_sentiment(start_date, end_date)

        # Generate trading signals using threshold method
        # VIX thresholds: <12 (complacent), 12-15 (low), 15-20 (neutral),
        # 20-30 (fear), >30 (extreme fear)
        df["Signal"] = self._generate_signal(
            df["VIX"],
            thresholds=(12, 15, 20, 30)
        )

        return df[["VIX", "Sentiment", "SentimentScore", "VIX_Percentile", "Signal"]]

    def get_vix_sentiment_normalized(
        self,
        start_date: Optional[str] = None,
        end_date: Optional[str] = None,
        calibration_start: str = "2015-01-01",
    ) -> pd.DataFrame:
        """
        Calculate VIX sentiment with normalized 0-100 scale.

        Normalizes VIX to 0-100 scale for easier interpretation and comparison
        with other metrics. Lower values = bullish (low fear), higher values =
        bearish (high fear).

        Args:
            start_date: Start date in YYYY-MM-DD format
            end_date: End date in YYYY-MM-DD format
            calibration_start: Start of calibration period (default: 2015-01-01)

        Returns:
            DataFrame with normalized VIX sentiment (0-100 scale)

        Example:
            >>> metrics = CustomMetrics()
            >>> vix = metrics.get_vix_sentiment_normalized("2024-01-01")
            >>> # VIX_Normalized: 0=very low fear, 100=extreme fear
        """
        # Get calibration data
        calibration_data = self.vix_calculator.get_vix_data(
            start_date=calibration_start,
            end_date=end_date
        )

        # Get actual data
        result = self.get_vix_sentiment(start_date, end_date)

        # Normalize VIX to 0-100 scale using percentile-based normalization
        # Use the existing VIX_Percentile column which is already 0-100
        result["VIX_Normalized"] = result["VIX_Percentile"]

        # Update signals based on normalized values
        # 0-30: Low fear (bullish)
        # 30-50: Below average fear
        # 50-70: Above average fear
        # 70-100: High fear (bearish)
        result["Signal"] = self._generate_signal(
            result["VIX_Normalized"],
            thresholds=(30, 50, 70, 85)
        )

        return result

    def get_vix_sentiment_weekly(
        self,
        start_date: Optional[str] = None,
        end_date: Optional[str] = None,
    ) -> pd.DataFrame:
        """
        Calculate weekly VIX sentiment for retail forecasting.

        Aggregates daily VIX to weekly intervals, matching your retail
        forecasting cadence. Uses average VIX for the week.

        Args:
            start_date: Start date in YYYY-MM-DD format
            end_date: End date in YYYY-MM-DD format

        Returns:
            DataFrame with weekly VIX sentiment

        Example:
            >>> metrics = CustomMetrics()
            >>> weekly_vix = metrics.get_vix_sentiment_weekly("2024-01-01")
            >>> # Perfect for merging with weekly retail sales data
        """
        daily = self.get_vix_sentiment(start_date, end_date)

        # Aggregate to weekly (Sunday week-ending)
        weekly = daily.resample("W").agg({
            "VIX": "mean",                  # Average VIX for the week
            "SentimentScore": "mean",       # Average sentiment
            "VIX_Percentile": "last",       # Last available percentile
        })

        # Recalculate sentiment from weekly average
        weekly["Sentiment"] = weekly["VIX"].apply(
            self.vix_calculator._vix_to_sentiment
        )

        # Generate signals
        weekly["Signal"] = self._generate_signal(
            weekly["VIX"],
            thresholds=(12, 15, 20, 30)
        )

        return weekly

    # ========================================================================
    # EXAMPLE: COMBINED METRICS
    # ========================================================================

    def get_combined_sentiment_score(
        self,
        start_date: Optional[str] = None,
        end_date: Optional[str] = None,
    ) -> pd.DataFrame:
        """
        Combine VIX sentiment with other metrics for composite sentiment.

        Example of how to combine VIX with your existing QQQ deviation
        or other custom metrics.

        Returns:
            DataFrame with multiple sentiment indicators
        """
        # Get VIX sentiment
        vix = self.get_vix_sentiment(start_date, end_date)

        # You could add other metrics here, e.g.:
        # qqq_deviation = self.get_qqq_200_deviation(start_date, end_date)
        # market_breadth = self.get_market_breadth(start_date, end_date)

        # Create composite DataFrame
        composite = pd.DataFrame(index=vix.index)
        composite["VIX"] = vix["VIX"]
        composite["VIX_Score"] = vix["SentimentScore"]
        composite["VIX_Signal"] = vix["Signal"]

        # You could calculate a weighted composite sentiment
        # composite["CompositeScore"] = (
        #     0.40 * vix["SentimentScore"] +
        #     0.30 * qqq_normalized_score +
        #     0.30 * market_breadth_score
        # )

        return composite


def demonstration():
    """Demonstrate the VIX sentiment integration."""
    print("\n" + "="*70)
    print(" VIX Sentiment Integration Demo")
    print("="*70)

    metrics = CustomMetricsExample()

    # Example 1: Daily VIX sentiment
    print("\n[1] Daily VIX Sentiment (last 10 days)")
    daily = metrics.get_vix_sentiment(start_date="2024-11-01")
    print(daily.tail(10))

    # Example 2: Normalized VIX
    print("\n[2] Normalized VIX (0-100 scale)")
    normalized = metrics.get_vix_sentiment_normalized(start_date="2024-11-01")
    print(normalized[["VIX", "VIX_Normalized", "Signal"]].tail(10))

    # Example 3: Weekly VIX for retail forecasting
    print("\n[3] Weekly VIX Sentiment (for retail forecasting)")
    weekly = metrics.get_vix_sentiment_weekly(start_date="2024-01-01")
    print(weekly.tail(10))

    # Example 4: Summary statistics
    print("\n[4] VIX Summary Statistics (2024)")
    print(f"Mean VIX:         {daily['VIX'].mean():.2f}")
    print(f"Median VIX:       {daily['VIX'].median():.2f}")
    print(f"Max VIX:          {daily['VIX'].max():.2f}")
    print(f"Min VIX:          {daily['VIX'].min():.2f}")
    print(f"\nSentiment Distribution:")
    print(daily['Sentiment'].value_counts())

    print("\n" + "="*70)
    print(" Integration Complete!")
    print("="*70)
    print("\nNext Steps:")
    print("1. Copy the get_vix_sentiment* methods to custom_metrics.py")
    print("2. Test with your existing retail sales data")
    print("3. Evaluate correlation with demand patterns")
    print("="*70 + "\n")


if __name__ == "__main__":
    demonstration()
