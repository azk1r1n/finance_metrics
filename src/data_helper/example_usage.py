"""
Example usage of MassiveFlatFiles helper for accessing historical options data
and calculating put/call ratios.
"""

from massive_flatfiles import MassiveFlatFiles


def example_basic_usage():
    """Basic usage examples for exploring flat files."""
    print("\n=== Basic Usage Examples ===\n")

    # Initialize helper
    helper = MassiveFlatFiles()

    # 1. Explore available data types
    print("1. Available data type prefixes:")
    for key, value in helper.PREFIXES.items():
        print(f"   {key:25} -> {value}")

    # 2. List recent options trade files
    print("\n2. Recent options trade files (Nov 2024):")
    files = helper.list_files("options_trades", date_filter="2024-11", max_results=5)
    for file in files:
        print(f"   {file}")

    # 3. Explore file structure
    print("\n3. Exploring options data structure:")
    helper.explore_file_structure("us_options_opra", max_results=10)


def example_put_call_ratio():
    """Calculate put/call ratio from flat file data."""
    print("\n=== Put/Call Ratio Calculation ===\n")

    helper = MassiveFlatFiles()

    # Calculate put/call ratio for SPY on a specific date
    # NOTE: Update this date to a recent trading day
    date = "2024-11-05"

    print(f"Calculating put/call ratio for {date}...")

    # Method 1: Using daily aggregates (faster, recommended)
    try:
        ratio_data = helper.calculate_put_call_ratio_from_file(
            date=date,
            underlying_symbol="SPY",
            use_trades=False,  # Use daily aggregates
        )

        print(f"\nSPY Put/Call Ratio on {date}:")
        print(f"  Put Volume:    {ratio_data['put_volume']:,}")
        print(f"  Call Volume:   {ratio_data['call_volume']:,}")
        print(f"  P/C Ratio:     {ratio_data['put_call_ratio']:.2f}")

    except Exception as e:
        print(f"Error: {e}")
        print("\nTip: Make sure the date is a recent trading day with available data")

    # Method 2: Calculate for entire market (all underlyings)
    try:
        market_ratio = helper.calculate_put_call_ratio_from_file(
            date=date,
            underlying_symbol=None,  # All underlyings
            use_trades=False,
        )

        print(f"\n\nMarket-Wide Put/Call Ratio on {date}:")
        print(f"  Put Volume:    {market_ratio['put_volume']:,}")
        print(f"  Call Volume:   {market_ratio['call_volume']:,}")
        print(f"  P/C Ratio:     {market_ratio['put_call_ratio']:.2f}")

    except Exception as e:
        print(f"Error: {e}")


def example_load_and_analyze():
    """Load options data and perform custom analysis."""
    print("\n=== Custom Analysis Example ===\n")

    helper = MassiveFlatFiles()

    # Load a sample of daily aggregates
    date = "2024-11-05"
    print(f"Loading options data for {date}...")

    try:
        # Load first 1000 rows to preview
        df = helper.get_options_daily_agg_for_date(date, nrows=1000)

        print(f"\nLoaded {len(df)} rows")
        print("\nColumns available:")
        print(df.columns.tolist())

        print("\nFirst few rows:")
        print(df.head())

        print("\nData types:")
        print(df.dtypes)

    except Exception as e:
        print(f"Error: {e}")
        print("\nTip: Update the date to a recent trading day")


def example_download_file():
    """Download a specific file for offline analysis."""
    print("\n=== Download File Example ===\n")

    helper = MassiveFlatFiles()

    # First, list available files to find what you want
    print("Finding available options files for November 2024...")
    files = helper.list_files("options_daily_agg", date_filter="2024-11", max_results=5)

    if files:
        print(f"\nFound {len(files)} files. First file:")
        print(f"  {files[0]}")

        # Download the first file
        print("\nDownloading file...")
        try:
            local_path = helper.download_file(files[0], local_path="./data/downloaded.csv")
            print(f"Success! File saved to: {local_path}")
        except Exception as e:
            print(f"Error: {e}")
    else:
        print("No files found. Try a different date range.")


def main():
    """Run all examples."""
    print("\n" + "=" * 70)
    print(" Massive Flat Files - Example Usage")
    print("=" * 70)

    # Run examples
    example_basic_usage()
    example_put_call_ratio()
    example_load_and_analyze()
    example_download_file()

    print("\n" + "=" * 70)
    print(" Examples Complete!")
    print("=" * 70 + "\n")


if __name__ == "__main__":
    main()
