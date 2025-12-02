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
   - Fully implemented
   - Uses yfinance for data fetching
   - MeiTou QQQ 200 Days Deviation Index: `(QQQ price - SMA_200) / SMA_200`
   - Provides both daily and weekly aggregations
   - Includes trading signals (Strong Bullish/Bullish/Bearish/Strong Bearish) based on deviation thresholds

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

## Data Source Attribution

- Market & Commodity data: Yahoo Finance via `yfinance` library
- Macro & Consumer data: Federal Reserve Economic Data (FRED) via `fredapi` library
- Environment variables: Loaded via `python-dotenv`
