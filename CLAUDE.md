# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Purpose

This library fetches financial and economic metrics to support **retail demand forecasting** at the item-level weekly unit forecasting. The goal is to provide economic indicators that influence consumer purchasing behavior.

## Development Environment

This project uses `uv` for package management (not pip/poetry):

```bash
# Install dependencies
uv sync

# Install with dev dependencies (includes jupyter, matplotlib, pytest)
uv sync --all-extras

# Add new dependency
uv add <package-name>

# Add dev dependency
uv add --dev <package-name>
```

## Running Code

```bash
# Run the demo notebook
jupyter notebook src/notebooks/demo.ipynb

# Run main.py (if needed)
uv run python main.py

# Run tests (when implemented)
uv run pytest
```

## Environment Setup

Create a `.env` file in the project root with your FRED API key:
```bash
FRED_API_KEY=your_fred_api_key_here
```

Get a free API key from: https://fred.stlouisfed.org/docs/api/api_key.html

The `.env` file is already in `.gitignore` to prevent committing secrets.

## Architecture

The library is organized into four metric categories, each as a separate module in `src/finance_metrics/`:

1. **MarketIndices** (`market_indices.py`) - Stock market data via yfinance
   - Fully implemented
   - Uses Yahoo Finance ticker symbols (e.g., "^GSPC" for S&P 500)
   - Returns pandas DataFrames with OHLCV data

2. **CommodityPrices** (`commodity_prices.py`) - Commodity futures via yfinance
   - Fully implemented
   - Uses futures ticker symbols (e.g., "CL=F" for WTI crude oil)
   - Returns pandas DataFrames with price data

3. **MacroIndicators** (`macro_indicators.py`) - Economic indicators via FRED
   - Fully implemented
   - Uses FRED API (requires FRED_API_KEY in .env)
   - Provides: GDP, GDP growth, CPI, inflation rate, PPI, unemployment, interest rates, housing starts
   - Uses SERIES_IDS dictionary mapping user-friendly names to FRED series codes

4. **ConsumerMetrics** (`consumer_metrics.py`) - Consumer economic data via FRED
   - Fully implemented
   - Uses FRED API (requires FRED_API_KEY in .env)
   - Provides: consumer sentiment, consumer confidence, retail sales, retail sales growth, PCE, disposable income, saving rate, consumer credit
   - Uses SERIES_IDS dictionary mapping user-friendly names to FRED series codes

5. **CustomMetrics** (`custom_metrics.py`) - Custom financial metrics and technical indicators
   - Designed to support 6 MeiTou custom metrics for retail forecasting
   - Uses extensible architecture with common utility methods
   - **Metric 1: QQQ 200 Days Deviation Index** ✅ Implemented
     - Formula: `(QQQ price - SMA_200) / SMA_200`
     - Provides daily, weekly, and normalized (0-100 scale) versions
     - Includes trading signals based on deviation thresholds
   - **Metric 2: Market Breadth Index** 🚧 Placeholder (advance/decline ratios, stocks above 200-day MA)
   - **Metric 3: VIX Fear & Greed Index** 🚧 Placeholder (VIX levels, term structure analysis)
   - **Metric 4: Sector Rotation Index** 🚧 Placeholder (11 GICS sectors, relative performance)
   - **Metric 5: Volume Momentum Index** 🚧 Placeholder (on-balance volume, volume trends)
   - **Metric 6: Multi-Timeframe Momentum** 🚧 Placeholder (50/100/200-day trend alignment)

## Key Design Patterns

### Weekly Aggregation
The target application is **weekly forecasting**, so data often needs aggregation from daily to weekly:

```python
# Example from demo.ipynb
daily_data = market.get_index("sp500", start_date="2023-01-01")
weekly_data = daily_data['Close'].resample('W').last()  # Week ending Sunday
```

### Data Source Abstraction
Each module class provides a consistent interface:
- Methods accept `start_date` and `end_date` as strings (YYYY-MM-DD)
- All return pandas DataFrames
- yfinance methods accept `interval` parameter ("1d", "1wk", "1mo")

### Series ID Mappings
All modules use internal dictionaries mapping user-friendly names to data source identifiers:
- `MarketIndices.INDICES` - Yahoo Finance ticker symbols (e.g., "sp500" → "^GSPC")
- `CommodityPrices.COMMODITIES` - Yahoo Finance futures symbols (e.g., "crude_oil_wti" → "CL=F")
- `MacroIndicators.SERIES_IDS` - FRED series codes (e.g., "unemployment" → "UNRATE")
- `ConsumerMetrics.SERIES_IDS` - FRED series codes (e.g., "consumer_sentiment" → "UMCSENT")

### Mixed Frequency Data Alignment
Economic data comes at different frequencies:
- **Daily**: Market indices, commodities (yfinance)
- **Monthly**: CPI, unemployment, retail sales, consumer sentiment (FRED)
- **Quarterly**: GDP (FRED)

For weekly forecasting, use forward-fill to align monthly/quarterly data to weekly:
```python
monthly_data = macro.get_cpi(start_date="2023-01-01")
weekly_data = monthly_data.resample('W').ffill()
```

**Important Note on Commodities**: Futures contracts expire and roll over, so requesting weekly data directly often fails. Always fetch daily data first, then resample:
```python
# Correct approach for commodities
oil_daily = commodities.get_commodity("crude_oil_wti", start_date="2023-01-01")
oil_weekly = oil_daily['Close'].resample('W').last()

# Incorrect - will often fail with YFPricesMissingError
# oil_weekly = commodities.get_commodity("crude_oil_wti", interval="1wk")
```

### CustomMetrics Extensible Architecture

The `CustomMetrics` module uses a utility methods pattern to support multiple custom metrics efficiently:

#### Common Utility Methods

All located in the `custom_metrics.py` file (lines 32-159):

1. **`_fetch_ticker_data()`** - Standardized yfinance data fetching with error handling
   - Handles MultiIndex columns automatically
   - Applies auto_adjust=True for clean price data

2. **`_normalize_to_scale()`** - Robust 0-100 normalization
   - Uses percentile-based bounds (default: 1st-99th percentile)
   - Calibrates on historical data to establish stable bounds
   - Clips outliers to 0-100 range

3. **`_generate_signal()`** - Threshold-based trading signals
   - Maps values to: Strong Bearish / Bearish / Bullish / Strong Bullish
   - Accepts custom threshold tuples for each metric

4. **`_calculate_stats()`** - Statistical summaries
   - Returns: mean, median, std, min, max, current value

#### Implementing a New Custom Metric

When adding a new MeiTou metric, follow this pattern:

```python
def get_my_new_metric(
    self,
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
) -> pd.DataFrame:
    """
    Calculate My New Metric.

    [Description of what the metric measures and why it matters]

    Formula: [mathematical formula]

    Args:
        start_date: Start date in YYYY-MM-DD format
        end_date: End date in YYYY-MM-DD format

    Returns:
        DataFrame with metric columns
    """
    # 1. Fetch required data using _fetch_ticker_data()
    data = self._fetch_ticker_data("TICKER", start_date, end_date)

    # 2. Calculate your metric
    data["MyMetric"] = # your calculation here

    # 3. Generate signals using _generate_signal()
    data["Signal"] = self._generate_signal(
        data["MyMetric"],
        (threshold1, threshold2, threshold3, threshold4)
    )

    # 4. Return relevant columns
    return data[["Column1", "Column2", "MyMetric", "Signal"]].copy()

# Optional: Add normalized version
def get_my_new_metric_normalized(
    self,
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    calibration_start: str = "2015-01-01",
) -> pd.DataFrame:
    """Calculate normalized version (0-100 scale)."""
    calibration_data = self.get_my_new_metric(calibration_start, end_date)
    result = self.get_my_new_metric(start_date, end_date)

    result["MyMetric_Normalized"] = self._normalize_to_scale(
        result["MyMetric"],
        calibration_data["MyMetric"],
        lower_percentile=1.0,
        upper_percentile=99.0,
    )

    # Update signals based on normalized values
    result["Signal"] = self._generate_signal(
        result["MyMetric_Normalized"], (30, 50, 50, 70)
    )

    return result

# Optional: Add weekly version
def get_my_new_metric_weekly(
    self,
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
) -> pd.DataFrame:
    """Calculate weekly aggregated version."""
    daily = self.get_my_new_metric(start_date, end_date)

    weekly = daily.resample("W").agg({
        "Column1": "last",
        "MyMetric": "last",
    })

    weekly["Signal"] = self._generate_signal(
        weekly["MyMetric"], (threshold1, threshold2, threshold3, threshold4)
    )

    return weekly
```

**Key Principles:**
- Each metric should have 3 versions: daily (base), normalized (0-100), and weekly
- Use utility methods to avoid code duplication
- Include docstrings with formula and interpretation
- Signal thresholds should be meaningful for the specific metric
- Calibration period defaults to 2015-01-01 for consistency

## Data Source Attribution

- Market & Commodity data: Yahoo Finance via `yfinance` library
- Macro & Consumer data: Federal Reserve Economic Data (FRED) via `fredapi` library
- Environment variables: Loaded via `python-dotenv`
