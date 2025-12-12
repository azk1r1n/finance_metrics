"""
Put/Call Ratio Calculator using Massive.com REST API

Calculate put/call ratios for any underlying symbol using the Options Chain
Snapshot API. Works with free and paid tiers (15-minute delay for free tier).

Note: This uses the REST API which has different access levels than flat files.
Most free tiers support delayed options data.
"""

import os
from datetime import datetime
from typing import Dict, Optional

from dotenv import load_dotenv

# Try new import first, fallback to old
try:
    from massive import RESTClient
except ImportError:
    try:
        from polygon import RESTClient
    except ImportError:
        raise ImportError(
            "Please install polygon-api-client: uv add polygon-api-client"
        )


class PutCallRatioAPI:
    """
    Calculate put/call ratios using Massive.com (formerly Polygon.io) REST API.

    This uses the Options Chain Snapshot endpoint to fetch current options data
    and calculate volume-based and open interest-based put/call ratios.
    """

    def __init__(self, api_key: Optional[str] = None):
        """
        Initialize API client.

        Args:
            api_key: Massive/Polygon API key (reads from .env if not provided)
        """
        if api_key is None:
            load_dotenv()
            api_key = os.getenv("MASSIVE_API_KEY") or os.getenv("POLYGON_API_KEY")

        if not api_key:
            raise ValueError(
                "API key not found. Provide api_key parameter or set "
                "MASSIVE_API_KEY/POLYGON_API_KEY in .env"
            )

        self.client = RESTClient(api_key)

    def get_put_call_ratio(
        self,
        symbol: str,
        expiration_date: Optional[str] = None,
        use_open_interest: bool = False,
    ) -> Dict:
        """
        Calculate put/call ratio for a symbol.

        Args:
            symbol: Underlying ticker symbol (e.g., "SPY", "AAPL")
            expiration_date: Optional expiration date filter (YYYY-MM-DD)
            use_open_interest: If True, use open interest instead of volume

        Returns:
            Dictionary with put/call ratio data:
            {
                'symbol': str,
                'timestamp': str,
                'put_volume': int,
                'call_volume': int,
                'put_call_ratio_volume': float,
                'put_open_interest': int,
                'call_open_interest': int,
                'put_call_ratio_oi': float,
                'total_contracts': int,
                'expiration_filter': str or None
            }

        Example:
            >>> calc = PutCallRatioAPI()
            >>> ratio = calc.get_put_call_ratio("SPY")
            >>> print(f"SPY P/C Ratio: {ratio['put_call_ratio_volume']:.2f}")
        """
        print(f"\nFetching options chain for {symbol}...")

        # Fetch all options contracts
        # Note: API has limit of 250 per request, may need pagination
        params = {
            "limit": 250,  # Max allowed per request
        }

        if expiration_date:
            params["expiration_date"] = expiration_date

        # Get options chain snapshot
        try:
            response = self.client.list_snapshot_options_chain(
                underlying_asset=symbol,
                params=params,
            )
        except Exception as e:
            raise Exception(
                f"Failed to fetch options data for {symbol}. "
                f"Error: {e}\n"
                f"Note: Options data may require a paid plan or have a delay."
            )

        # Initialize counters
        put_volume = 0
        call_volume = 0
        put_oi = 0
        call_oi = 0
        total_contracts = 0

        # Process results
        contracts_processed = 0
        for contract in response:
            contracts_processed += 1

            # Get contract type
            contract_type = None
            if hasattr(contract, "details") and hasattr(contract.details, "contract_type"):
                contract_type = contract.details.contract_type.lower()

            # Get volume (from day data)
            volume = 0
            if hasattr(contract, "day") and hasattr(contract.day, "volume"):
                volume = contract.day.volume or 0

            # Get open interest
            oi = 0
            if hasattr(contract, "open_interest"):
                oi = contract.open_interest or 0

            # Accumulate by contract type
            if contract_type == "put":
                put_volume += volume
                put_oi += oi
            elif contract_type == "call":
                call_volume += volume
                call_oi += oi

            total_contracts += 1

        # Calculate ratios
        if call_volume > 0:
            pc_ratio_volume = put_volume / call_volume
        else:
            pc_ratio_volume = None

        if call_oi > 0:
            pc_ratio_oi = put_oi / call_oi
        else:
            pc_ratio_oi = None

        # Prepare result
        result = {
            "symbol": symbol,
            "timestamp": datetime.now().isoformat(),
            "put_volume": put_volume,
            "call_volume": call_volume,
            "put_call_ratio_volume": pc_ratio_volume,
            "put_open_interest": put_oi,
            "call_open_interest": call_oi,
            "put_call_ratio_oi": pc_ratio_oi,
            "total_contracts": total_contracts,
            "expiration_filter": expiration_date,
            "contracts_processed": contracts_processed,
        }

        # Print summary
        print(f"\n{'='*60}")
        print(f"Put/Call Ratio for {symbol}")
        print(f"{'='*60}")
        print(f"Timestamp:            {result['timestamp']}")
        print(f"Contracts processed:  {contracts_processed}")
        if expiration_date:
            print(f"Expiration filter:    {expiration_date}")
        print(f"\n--- Volume-Based ---")
        print(f"Put Volume:           {put_volume:,}")
        print(f"Call Volume:          {call_volume:,}")
        if pc_ratio_volume is not None:
            print(f"P/C Ratio (Volume):   {pc_ratio_volume:.3f}")
            self._interpret_ratio(pc_ratio_volume)
        else:
            print(f"P/C Ratio (Volume):   N/A (no call volume)")

        print(f"\n--- Open Interest-Based ---")
        print(f"Put OI:               {put_oi:,}")
        print(f"Call OI:              {call_oi:,}")
        if pc_ratio_oi is not None:
            print(f"P/C Ratio (OI):       {pc_ratio_oi:.3f}")
            self._interpret_ratio(pc_ratio_oi)
        else:
            print(f"P/C Ratio (OI):       N/A (no call OI)")
        print(f"{'='*60}\n")

        return result

    def _interpret_ratio(self, ratio: float) -> None:
        """Print interpretation of put/call ratio."""
        if ratio > 1.3:
            sentiment = "Very Bearish"
        elif ratio > 1.0:
            sentiment = "Bearish"
        elif ratio > 0.7:
            sentiment = "Neutral"
        elif ratio > 0.5:
            sentiment = "Bullish"
        else:
            sentiment = "Very Bullish"

        print(f"Sentiment:            {sentiment}")

    def get_multiple_symbols(
        self,
        symbols: list,
        expiration_date: Optional[str] = None,
    ) -> Dict:
        """
        Calculate put/call ratios for multiple symbols.

        Args:
            symbols: List of ticker symbols
            expiration_date: Optional expiration date filter

        Returns:
            Dictionary mapping symbols to their ratio data

        Example:
            >>> calc = PutCallRatioAPI()
            >>> ratios = calc.get_multiple_symbols(["SPY", "QQQ", "IWM"])
        """
        results = {}

        for symbol in symbols:
            try:
                ratio = self.get_put_call_ratio(symbol, expiration_date)
                results[symbol] = ratio
            except Exception as e:
                print(f"Error processing {symbol}: {e}")
                results[symbol] = {"error": str(e)}

        return results

    def compare_symbols(
        self,
        symbols: list,
        expiration_date: Optional[str] = None,
    ) -> None:
        """
        Compare put/call ratios across multiple symbols.

        Args:
            symbols: List of ticker symbols
            expiration_date: Optional expiration date filter

        Example:
            >>> calc = PutCallRatioAPI()
            >>> calc.compare_symbols(["SPY", "QQQ", "IWM"])
        """
        results = self.get_multiple_symbols(symbols, expiration_date)

        print(f"\n{'='*80}")
        print(f"Put/Call Ratio Comparison")
        print(f"{'='*80}")
        print(f"{'Symbol':<10} {'P/C (Vol)':<12} {'P/C (OI)':<12} {'Sentiment':<20}")
        print(f"{'-'*80}")

        for symbol, data in results.items():
            if "error" in data:
                print(f"{symbol:<10} {'ERROR':<12} {'ERROR':<12} {data['error'][:20]}")
                continue

            pc_vol = data.get("put_call_ratio_volume")
            pc_oi = data.get("put_call_ratio_oi")

            pc_vol_str = f"{pc_vol:.3f}" if pc_vol is not None else "N/A"
            pc_oi_str = f"{pc_oi:.3f}" if pc_oi is not None else "N/A"

            # Determine sentiment from volume ratio
            if pc_vol is not None:
                if pc_vol > 1.3:
                    sentiment = "Very Bearish"
                elif pc_vol > 1.0:
                    sentiment = "Bearish"
                elif pc_vol > 0.7:
                    sentiment = "Neutral"
                elif pc_vol > 0.5:
                    sentiment = "Bullish"
                else:
                    sentiment = "Very Bullish"
            else:
                sentiment = "Unknown"

            print(f"{symbol:<10} {pc_vol_str:<12} {pc_oi_str:<12} {sentiment:<20}")

        print(f"{'='*80}\n")


def main():
    """Example usage of PutCallRatioAPI."""
    print("\n" + "="*80)
    print(" Put/Call Ratio Calculator - REST API")
    print("="*80)

    try:
        # Initialize calculator
        calc = PutCallRatioAPI()

        # Example 1: Single symbol
        print("\n[Example 1] Calculate P/C ratio for SPY")
        spy_ratio = calc.get_put_call_ratio("SPY")

        # Example 2: With expiration filter (optional)
        # Uncomment and update date to use:
        # print("\n[Example 2] SPY with expiration filter")
        # spy_filtered = calc.get_put_call_ratio("SPY", expiration_date="2024-12-20")

        # Example 3: Compare multiple symbols
        print("\n[Example 3] Compare major indices")
        calc.compare_symbols(["SPY", "QQQ", "IWM", "DIA"])

    except Exception as e:
        print(f"\nError: {e}")
        print("\nTroubleshooting:")
        print("1. Check that POLYGON_API_KEY or MASSIVE_API_KEY is set in .env")
        print("2. Verify your API key has access to options data")
        print("3. Free tier may have 15-minute delay or limited access")
        print("4. Try a different symbol or expiration date")

    print("\n" + "="*80)
    print(" Complete!")
    print("="*80 + "\n")


if __name__ == "__main__":
    main()
