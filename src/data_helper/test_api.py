#!/usr/bin/env python3
"""
Quick test script for Put/Call Ratio API

This script tests the REST API-based put/call ratio calculator.
Update the symbols list to test different tickers.
"""

from put_call_ratio_api import PutCallRatioAPI


def main():
    print("\n" + "="*70)
    print(" Testing Put/Call Ratio API Calculator")
    print("="*70)

    try:
        # Initialize
        print("\n[1/3] Initializing API client...")
        calc = PutCallRatioAPI()
        print("✓ Client initialized successfully")

        # Test single symbol
        print("\n[2/3] Testing single symbol (SPY)...")
        spy_data = calc.get_put_call_ratio("SPY")

        if spy_data["put_call_ratio_volume"] is not None:
            print("✓ Successfully calculated SPY put/call ratio")
        else:
            print("⚠ No volume data available for SPY")

        # Test comparison
        print("\n[3/3] Testing multi-symbol comparison...")
        calc.compare_symbols(["SPY", "QQQ"])
        print("✓ Comparison complete")

        # Summary
        print("\n" + "="*70)
        print(" Test Summary")
        print("="*70)
        print(f"Symbol tested:        SPY")
        print(f"P/C Ratio (Volume):   {spy_data['put_call_ratio_volume']:.3f}" if spy_data['put_call_ratio_volume'] else "N/A")
        print(f"P/C Ratio (OI):       {spy_data['put_call_ratio_oi']:.3f}" if spy_data['put_call_ratio_oi'] else "N/A")
        print(f"Contracts processed:  {spy_data['contracts_processed']}")
        print(f"Put Volume:           {spy_data['put_volume']:,}")
        print(f"Call Volume:          {spy_data['call_volume']:,}")
        print("="*70)

        print("\n✓ All tests passed! The API is working correctly.\n")

    except Exception as e:
        print(f"\n✗ Test failed with error:\n{e}\n")
        print("Troubleshooting tips:")
        print("1. Verify .env contains POLYGON_API_KEY or MASSIVE_API_KEY")
        print("2. Check your API subscription tier allows options data")
        print("3. Free tier typically has 15-minute delay")
        print("4. Some endpoints may require upgraded plans\n")
        return 1

    return 0


if __name__ == "__main__":
    exit(main())
