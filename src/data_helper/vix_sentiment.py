"""
VIX-based Market Sentiment Indicator

Free alternative to put/call ratio using VIX (volatility index).
VIX correlates strongly with put/call ratios:
- High VIX (>25) = High fear = Similar to high put/call ratio
- Low VIX (<15) = Low fear = Similar to low put/call ratio

Works with free data from Yahoo Finance (yfinance).
"""

from datetime import datetime, timedelta
from typing import Optional

import pandas as pd
import yfinance as yf


class VIXSentiment:
    """
    Calculate market sentiment using VIX (CBOE Volatility Index).

    VIX is known as the "fear gauge" and moves inversely with market sentiment.
    Free alternative to put/call ratios with similar predictive power.
    """

    # VIX interpretation thresholds
    VIX_THRESHOLDS = {
        "extreme_fear": 30,     # VIX > 30 = Extreme fear
        "fear": 20,             # VIX 20-30 = Fear/concern
        "neutral": 15,          # VIX 15-20 = Neutral
        "complacency": 12,      # VIX 12-15 = Low concern
        # VIX < 12 = Extreme complacency
    }

    def __init__(self):
        """Initialize VIX sentiment calculator."""
        pass

    def get_vix_data(
        self,
        start_date: Optional[str] = None,
        end_date: Optional[str] = None,
        interval: str = "1d",
    ) -> pd.DataFrame:
        """
        Fetch VIX data from Yahoo Finance.

        Args:
            start_date: Start date (YYYY-MM-DD), defaults to 1 year ago
            end_date: End date (YYYY-MM-DD), defaults to today
            interval: Data interval ("1d", "1wk", "1mo")

        Returns:
            DataFrame with VIX OHLCV data

        Example:
            >>> vix = VIXSentiment()
            >>> data = vix.get_vix_data(start_date="2024-01-01")
        """
        if start_date is None:
            start_date = (datetime.now() - timedelta(days=365)).strftime("%Y-%m-%d")
        if end_date is None:
            end_date = datetime.now().strftime("%Y-%m-%d")

        # Fetch VIX from Yahoo Finance (^VIX)
        vix = yf.download(
            "^VIX",
            start=start_date,
            end=end_date,
            interval=interval,
            progress=False,
            auto_adjust=True,
        )

        # Handle MultiIndex columns
        if isinstance(vix.columns, pd.MultiIndex):
            vix.columns = vix.columns.get_level_values(0)

        return vix

    def calculate_sentiment(
        self,
        start_date: Optional[str] = None,
        end_date: Optional[str] = None,
    ) -> pd.DataFrame:
        """
        Calculate market sentiment based on VIX levels.

        Args:
            start_date: Start date (YYYY-MM-DD)
            end_date: End date (YYYY-MM-DD)

        Returns:
            DataFrame with VIX, sentiment signal, and interpretation

        Example:
            >>> vix = VIXSentiment()
            >>> sentiment = vix.calculate_sentiment("2024-01-01")
            >>> print(sentiment.tail())
        """
        vix_data = self.get_vix_data(start_date, end_date)

        df = pd.DataFrame(index=vix_data.index)
        df["VIX"] = vix_data["Close"]

        # Calculate sentiment signal
        df["Sentiment"] = df["VIX"].apply(self._vix_to_sentiment)

        # Calculate numeric sentiment score (-2 to +2)
        # Negative = Bearish, Positive = Bullish
        df["SentimentScore"] = df["VIX"].apply(self._vix_to_score)

        # Calculate VIX percentile (0-100)
        # Higher percentile = higher current VIX relative to history
        df["VIX_Percentile"] = (
            df["VIX"].rank(pct=True) * 100
        ).round(1)

        return df

    def _vix_to_sentiment(self, vix_value: float) -> str:
        """Convert VIX level to sentiment label."""
        if pd.isna(vix_value):
            return "Unknown"
        elif vix_value > self.VIX_THRESHOLDS["extreme_fear"]:
            return "Extreme Fear"
        elif vix_value > self.VIX_THRESHOLDS["fear"]:
            return "Fear"
        elif vix_value > self.VIX_THRESHOLDS["neutral"]:
            return "Neutral"
        elif vix_value > self.VIX_THRESHOLDS["complacency"]:
            return "Complacent"
        else:
            return "Extreme Complacency"

    def _vix_to_score(self, vix_value: float) -> float:
        """
        Convert VIX to numeric sentiment score.

        Returns:
            -2 to +2 scale
            -2 = Extreme fear (very bearish)
            0 = Neutral
            +2 = Extreme complacency (very bullish, contrarian bearish)
        """
        if pd.isna(vix_value):
            return 0

        # Invert VIX so higher VIX = more negative sentiment
        if vix_value > 30:
            return -2.0
        elif vix_value > 20:
            return -1.0
        elif vix_value > 15:
            return 0.0
        elif vix_value > 12:
            return 1.0
        else:
            return 2.0

    def get_current_sentiment(self) -> dict:
        """
        Get current VIX-based market sentiment.

        Returns:
            Dictionary with current VIX, sentiment, and interpretation

        Example:
            >>> vix = VIXSentiment()
            >>> current = vix.get_current_sentiment()
            >>> print(f"Current sentiment: {current['sentiment']}")
        """
        vix_data = self.get_vix_data()

        if len(vix_data) == 0:
            return {"error": "No VIX data available"}

        latest = vix_data.iloc[-1]
        vix_value = latest["Close"]

        result = {
            "date": vix_data.index[-1].strftime("%Y-%m-%d"),
            "vix": round(vix_value, 2),
            "sentiment": self._vix_to_sentiment(vix_value),
            "sentiment_score": self._vix_to_score(vix_value),
        }

        # Add interpretation
        if vix_value > 30:
            result["interpretation"] = (
                "Extreme fear - Market expects high volatility. "
                "Similar to very high put/call ratio (>1.5)."
            )
        elif vix_value > 20:
            result["interpretation"] = (
                "Elevated fear - Market concerned. "
                "Similar to high put/call ratio (1.0-1.5)."
            )
        elif vix_value > 15:
            result["interpretation"] = (
                "Neutral - Normal market conditions. "
                "Similar to balanced put/call ratio (0.8-1.0)."
            )
        else:
            result["interpretation"] = (
                "Complacency - Low volatility expectations. "
                "Similar to low put/call ratio (<0.7)."
            )

        return result

    def compare_with_market(
        self,
        market_symbol: str = "SPY",
        start_date: Optional[str] = None,
        end_date: Optional[str] = None,
    ) -> pd.DataFrame:
        """
        Compare VIX sentiment with market performance.

        Args:
            market_symbol: Market index symbol (default: SPY)
            start_date: Start date
            end_date: End date

        Returns:
            DataFrame with VIX, market prices, and sentiment

        Example:
            >>> vix = VIXSentiment()
            >>> comparison = vix.compare_with_market("SPY", "2024-01-01")
        """
        # Get VIX sentiment
        sentiment = self.calculate_sentiment(start_date, end_date)

        # Get market data
        market_data = yf.download(
            market_symbol,
            start=start_date or (datetime.now() - timedelta(days=365)).strftime("%Y-%m-%d"),
            end=end_date or datetime.now().strftime("%Y-%m-%d"),
            progress=False,
            auto_adjust=True,
        )

        # Handle MultiIndex
        if isinstance(market_data.columns, pd.MultiIndex):
            market_data.columns = market_data.columns.get_level_values(0)

        # Combine
        df = sentiment.copy()
        df[f"{market_symbol}_Close"] = market_data["Close"]
        df[f"{market_symbol}_Return"] = df[f"{market_symbol}_Close"].pct_change() * 100

        return df


def main():
    """Example usage of VIX sentiment indicator."""
    print("\n" + "="*70)
    print(" VIX-Based Market Sentiment Indicator (FREE)")
    print("="*70)

    vix = VIXSentiment()

    # Example 1: Current sentiment
    print("\n[Example 1] Current market sentiment")
    current = vix.get_current_sentiment()
    print(f"\nDate:              {current['date']}")
    print(f"VIX Level:         {current['vix']:.2f}")
    print(f"Sentiment:         {current['sentiment']}")
    print(f"Sentiment Score:   {current['sentiment_score']}")
    print(f"\n{current['interpretation']}")

    # Example 2: Historical sentiment
    print("\n[Example 2] Historical sentiment (last 30 days)")
    sentiment_30d = vix.calculate_sentiment(
        start_date=(datetime.now() - timedelta(days=30)).strftime("%Y-%m-%d")
    )
    print(f"\nLast 10 days:")
    print(sentiment_30d[["VIX", "Sentiment", "SentimentScore"]].tail(10))

    # Example 3: Compare with SPY
    print("\n[Example 3] VIX vs SPY correlation (last 90 days)")
    comparison = vix.compare_with_market(
        "SPY",
        start_date=(datetime.now() - timedelta(days=90)).strftime("%Y-%m-%d")
    )

    # Calculate correlation
    corr = comparison["VIX"].corr(comparison["SPY_Return"])
    print(f"\nVIX vs SPY Daily Return Correlation: {corr:.3f}")
    print("(Negative correlation expected: VIX up → Market down)")

    print("\n" + "="*70)
    print(" Complete! VIX data is 100% FREE via yfinance")
    print("="*70 + "\n")


if __name__ == "__main__":
    main()
