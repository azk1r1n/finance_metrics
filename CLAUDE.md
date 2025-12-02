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
jupyter notebook demo.ipynb

# Run main.py (if needed)
uv run python main.py

# Run tests (when implemented)
uv run pytest
```

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

3. **MacroIndicators** (`macro_indicators.py`) - Economic indicators
   - NOT YET IMPLEMENTED (stub methods raise NotImplementedError)
   - Intended to use FRED API (requires API key)
   - Planned: GDP, CPI, unemployment, interest rates

4. **ConsumerMetrics** (`consumer_metrics.py`) - Consumer economic data
   - NOT YET IMPLEMENTED (stub methods raise NotImplementedError)
   - Intended to use FRED API (requires API key)
   - Planned: consumer confidence, retail sales, PCE, sentiment

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

### Ticker Mappings
Both `MarketIndices` and `CommodityPrices` use internal dictionaries mapping user-friendly names to Yahoo Finance tickers:
- `MarketIndices.INDICES` (e.g., "sp500" → "^GSPC")
- `CommodityPrices.COMMODITIES` (e.g., "crude_oil_wti" → "CL=F")

## Implementation Notes for FRED API

When implementing MacroIndicators and ConsumerMetrics:
1. Add `fredapi` dependency: `uv add fredapi`
2. FRED requires API key from https://fred.stlouisfed.org/docs/api/api_key.html
3. Use environment variable or config file (not hardcoded)
4. FRED series IDs needed (examples):
   - GDP: "GDP"
   - CPI: "CPIAUCSL"
   - Unemployment: "UNRATE"
   - Consumer Confidence: "UMCSENT"

## Data Source Attribution

- Market & Commodity data: Yahoo Finance via `yfinance` library
- Macro & Consumer data (when implemented): Federal Reserve Economic Data (FRED)
