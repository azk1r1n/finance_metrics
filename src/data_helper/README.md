# Massive Flat Files Data Helper

Helper utilities for accessing historical market data from Massive.com (formerly Polygon.io) flat files via S3.

## Quick Start

```python
from data_helper import MassiveFlatFiles

# Initialize helper (reads credentials from .env)
helper = MassiveFlatFiles()

# Calculate put/call ratio for SPY
ratio = helper.calculate_put_call_ratio_from_file(
    date="2024-11-05",
    underlying_symbol="SPY"
)

print(f"SPY P/C Ratio: {ratio['put_call_ratio']:.2f}")
```

## Available Data Types

The helper provides access to:

| Data Type | Prefix Key | Description |
|-----------|------------|-------------|
| **Stocks** | | |
| Trades | `stocks_trades` | Trade-level stock data |
| Quotes | `stocks_quotes` | Bid/ask quote data |
| Minute Aggs | `stocks_minute_agg` | 1-minute OHLCV bars |
| Daily Aggs | `stocks_daily_agg` | Daily OHLCV bars |
| **Options** | | |
| Trades | `options_trades` | Trade-level options data (2016+) |
| Quotes | `options_quotes` | Bid/ask options quotes (2022+) |
| Minute Aggs | `options_minute_agg` | 1-minute OHLCV bars |
| Daily Aggs | `options_daily_agg` | Daily OHLCV bars ⭐ **Best for P/C ratio** |
| **Other** | | |
| Indices | `indices_minute_agg`, `indices_daily_agg` | Index data |
| Forex | `forex_trades`, `forex_quotes` | Currency pairs |
| Crypto | `crypto_trades`, `crypto_quotes` | Cryptocurrency |

## Put/Call Ratio Calculation

### Recommended: Using Daily Aggregates

**Daily aggregates are the best data source for put/call ratios** because:
- ✅ Pre-calculated volume for each contract
- ✅ Faster to download and process (smaller files)
- ✅ Contains contract type (put/call) classification
- ✅ Available from ~11 AM ET next day

```python
# Single symbol (e.g., SPY)
spy_ratio = helper.calculate_put_call_ratio_from_file(
    date="2024-11-05",
    underlying_symbol="SPY",
    use_trades=False  # Use daily aggregates (recommended)
)

# Market-wide (all symbols)
market_ratio = helper.calculate_put_call_ratio_from_file(
    date="2024-11-05",
    underlying_symbol=None,  # All underlyings
    use_trades=False
)
```

### Alternative: Using Trade-Level Data

More granular but slower:

```python
ratio = helper.calculate_put_call_ratio_from_file(
    date="2024-11-05",
    underlying_symbol="SPY",
    use_trades=True  # Use trade-level data
)
```

## Historical Data Coverage

| Data Type | Start Date | Update Frequency |
|-----------|------------|------------------|
| Options Trades | 2016 | Daily (11 AM ET next day) |
| Options Quotes | 2022 | Daily (11 AM ET next day) |
| Options Aggregates | Varies | Daily (11 AM ET next day) |
| Stocks | Extensive history | Daily |

## Common Methods

### List Available Files

```python
# List recent options files
files = helper.list_files(
    "options_daily_agg",
    date_filter="2024-11",  # November 2024
    max_results=10
)
```

### Download a File

```python
# Download and decompress
local_path = helper.download_file(
    "us_options_opra/day_aggs_v1/2024/11/2024-11-05.csv.gz",
    local_path="./data/options_2024-11-05.csv",
    decompress=True
)
```

### Load into DataFrame

```python
# Load options daily aggregates
df = helper.get_options_daily_agg_for_date("2024-11-05")

# Load specific underlying only
spy_options = df[df['underlying_symbol'] == 'SPY']

# Calculate custom metrics
puts = spy_options[spy_options['contract_type'] == 'put']['volume'].sum()
calls = spy_options[spy_options['contract_type'] == 'call']['volume'].sum()
```

### Explore File Structure

```python
# See what's available
helper.explore_file_structure("us_options_opra", max_results=20)
```

## Expected CSV Columns

### Options Daily Aggregates

Common columns include:
- `underlying_symbol` - Underlying ticker (e.g., "SPY")
- `contract_type` or `option_type` - "put" or "call"
- `strike_price` - Strike price
- `expiration_date` - Expiration date
- `volume` - Total volume for the day
- `open`, `high`, `low`, `close` - OHLC prices
- `transactions` - Number of trades
- `open_interest` - Open interest

**Note**: Exact column names may vary. Use `df.columns.tolist()` to inspect.

## Use Cases for Put/Call Ratio

### 1. Market Sentiment Indicator

```python
# Track SPY sentiment over time
dates = ["2024-11-01", "2024-11-04", "2024-11-05", "2024-11-06", "2024-11-07"]

ratios = []
for date in dates:
    try:
        r = helper.calculate_put_call_ratio_from_file(date, "SPY")
        ratios.append(r)
    except Exception as e:
        print(f"Skipping {date}: {e}")

# Convert to DataFrame for analysis
import pandas as pd
df = pd.DataFrame(ratios)
print(df)
```

### 2. Custom Metric for Retail Forecasting

Add to your `CustomMetrics` class:

```python
def get_put_call_ratio_historical(
    self,
    symbol: str = "SPY",
    start_date: str = "2024-01-01",
    end_date: str = "2024-11-30",
) -> pd.DataFrame:
    """Calculate historical put/call ratios using Massive flat files."""
    from data_helper import MassiveFlatFiles
    from datetime import datetime, timedelta

    helper = MassiveFlatFiles()

    # Generate date range
    start = datetime.strptime(start_date, "%Y-%m-%d")
    end = datetime.strptime(end_date, "%Y-%m-%d")

    results = []
    current = start
    while current <= end:
        date_str = current.strftime("%Y-%m-%d")
        try:
            ratio = helper.calculate_put_call_ratio_from_file(date_str, symbol)
            results.append(ratio)
        except Exception:
            pass  # Skip non-trading days or missing data
        current += timedelta(days=1)

    df = pd.DataFrame(results)
    df['date'] = pd.to_datetime(df['date'])
    df.set_index('date', inplace=True)

    return df
```

## Error Handling

Common issues:

1. **File not found**: Date may be non-trading day or data not yet available
2. **Column name mismatch**: Inspect `df.columns` to find actual column names
3. **API credentials**: Ensure `.env` has valid `MASSIVE_ACCESS_KEY_ID` and `MASSIVE_SECRET_ACCESS_KEY`

## Running Examples

```bash
cd src/data_helper
python example_usage.py
```

## File Naming Convention

Files follow this pattern:
```
{asset_class}_{data_type}_v{version}/{year}/{month}/{date}.csv.gz
```

Example:
```
us_options_opra/day_aggs_v1/2024/11/2024-11-05.csv.gz
```

## Best Practices

1. **Use daily aggregates** for put/call ratios (faster, cleaner)
2. **Preview with `nrows`** parameter before loading full files
3. **Handle missing data** gracefully (weekends, holidays)
4. **Cache downloaded files** to avoid re-downloading
5. **Delete temp files** after loading to DataFrame
