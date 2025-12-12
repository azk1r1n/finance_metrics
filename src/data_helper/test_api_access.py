#!/usr/bin/env python3
"""
Test what API endpoints are accessible with current API key.

This script tests different endpoints to see what's available with your
current subscription tier.
"""

import os
from dotenv import load_dotenv

try:
    from polygon import RESTClient
except ImportError:
    print("Installing polygon-api-client...")
    import subprocess
    subprocess.run(["uv", "add", "polygon-api-client"])
    from polygon import RESTClient


def test_api_access():
    """Test various API endpoints to see what's accessible."""
    load_dotenv()
    api_key = os.getenv("MASSIVE_API_KEY") or os.getenv("POLYGON_API_KEY")

    if not api_key:
        print("ERROR: No API key found in .env")
        return

    client = RESTClient(api_key)

    print("\n" + "="*70)
    print(" Testing Massive.com API Access")
    print("="*70)

    # Test 1: Stock ticker details (should work on free tier)
    print("\n[Test 1] Stock ticker details (reference data)...")
    try:
        ticker_details = client.get_ticker_details("AAPL")
        print(f"✓ SUCCESS - Got AAPL ticker details")
        print(f"  Company: {ticker_details.name if hasattr(ticker_details, 'name') else 'N/A'}")
        print(f"  Market: {ticker_details.market if hasattr(ticker_details, 'market') else 'N/A'}")
    except Exception as e:
        print(f"✗ FAILED - {e}")

    # Test 2: Stock aggregates (should work on free tier - end of day)
    print("\n[Test 2] Stock aggregates (end of day data)...")
    try:
        aggs = client.get_aggs("AAPL", 1, "day", "2024-01-01", "2024-01-05")
        count = len(list(aggs)) if aggs else 0
        print(f"✓ SUCCESS - Got {count} daily bars for AAPL")
    except Exception as e:
        print(f"✗ FAILED - {e}")

    # Test 3: Options contract details (reference data - might work?)
    print("\n[Test 3] Options contract details (reference data)...")
    try:
        # Try to get details for a specific option contract
        # Format: O:SPY241220C00450000 (ticker, exp date, C/P, strike price)
        contract_ticker = "O:SPY241220C00450000"
        contract_details = client.get_ticker_details(contract_ticker)
        print(f"✓ SUCCESS - Got option contract details")
        print(f"  Ticker: {contract_details.ticker if hasattr(contract_details, 'ticker') else 'N/A'}")
    except Exception as e:
        print(f"✗ FAILED - {e}")

    # Test 4: Options snapshot (market data - likely won't work)
    print("\n[Test 4] Options chain snapshot (market data)...")
    try:
        snapshot = client.list_snapshot_options_chain("SPY", params={"limit": 5})
        count = len(list(snapshot)) if snapshot else 0
        print(f"✓ SUCCESS - Got {count} option contracts")
    except Exception as e:
        print(f"✗ FAILED - {e}")

    # Test 5: Try the OPTIONS CONTRACTS endpoint (list all contracts)
    print("\n[Test 5] List options contracts (reference data)...")
    try:
        contracts = client.list_options_contracts(
            underlying_ticker="SPY",
            limit=5
        )
        count = len(list(contracts)) if contracts else 0
        print(f"✓ SUCCESS - Got {count} option contracts")
        if count > 0:
            print("  Note: This is reference data only, not market data")
    except Exception as e:
        print(f"✗ FAILED - {e}")

    print("\n" + "="*70)
    print(" Summary")
    print("="*70)
    print("\nBased on these tests:")
    print("- If Test 1-2 pass: Your API key works for stocks data")
    print("- If Test 3 passes: You have options REFERENCE data")
    print("- If Test 4 passes: You have options MARKET data (snapshot)")
    print("- If Test 5 passes: You can list option contracts")
    print("\nFor put/call ratios, we need Test 4 to pass (market data).")
    print("="*70 + "\n")


if __name__ == "__main__":
    test_api_access()
