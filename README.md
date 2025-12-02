# Finance Metrics

A Python library for fetching and processing financial and economic metrics to support retail demand forecasting at the item-level weekly unit forecasting.

## Overview

This library provides easy access to various economic and financial indicators that influence consumer behavior and retail demand:

- **Macroeconomic Indicators**: GDP growth, inflation (CPI/PPI), unemployment rates, interest rates
- **Market Indices**: S&P 500, Dow Jones, NASDAQ, VIX, Russell 2000
- **Consumer Metrics**: Consumer confidence, retail sales, personal consumption expenditures, consumer sentiment
- **Commodity Prices**: Crude oil (WTI/Brent), natural gas, gold, agricultural commodities

## Why These Metrics Matter for Retail Forecasting

Economic conditions directly impact consumer purchasing behavior:

- **Market indices** reflect investor confidence and wealth effects
- **Consumer confidence** indicates willingness to spend
- **Commodity prices** (especially oil/gas) affect transportation costs and consumer budgets
- **Macro indicators** show overall economic health and employment levels
- **Retail sales** provide direct signals about consumer spending patterns

## Installation

This project uses [uv](https://github.com/astral-sh/uv) for dependency management:

```bash
# Install dependencies
uv sync

# Activate virtual environment
source .venv/bin/activate  # On Unix/macOS
# or
.venv\Scripts\activate  # On Windows
```

## Quick Start

```python
from finance_metrics import MarketIndices, CommodityPrices

# Fetch S&P 500 data
market = MarketIndices()
sp500 = market.get_index("sp500", start_date="2023-01-01", end_date="2024-01-01")

# Fetch crude oil prices
commodities = CommodityPrices()
oil = commodities.get_commodity("crude_oil_wti", start_date="2023-01-01")

# Get multiple indices at once
indices = market.get_multiple_indices(
    ["sp500", "vix", "nasdaq"],
    start_date="2023-01-01"
)
```

## Module Overview

### MarketIndices
Fetch stock market indices using yfinance:
- S&P 500, Dow Jones, NASDAQ, Russell 2000, VIX
- Calculate returns and volatility
- Access to OHLCV data

### CommodityPrices
Fetch commodity futures prices:
- Energy: WTI/Brent crude oil, natural gas
- Precious metals: Gold, silver
- Agricultural: Corn, wheat, soybeans

### MacroIndicators (Coming Soon)
Macroeconomic data from FRED API:
- GDP growth rates
- Inflation metrics (CPI, PPI)
- Unemployment rates
- Interest rates

### ConsumerMetrics (Coming Soon)
Consumer-focused economic indicators:
- Consumer Confidence Index
- Retail Sales
- Personal Consumption Expenditures
- Consumer Sentiment Index

## Data Sources

- **Market & Commodity Data**: Yahoo Finance (via yfinance)
- **Macro & Consumer Data**: Federal Reserve Economic Data (FRED) - requires API key

## Roadmap

- [ ] Implement FRED API integration for macro indicators
- [ ] Add data caching mechanisms
- [ ] Implement data quality checks and outlier detection
- [ ] Add feature engineering utilities (lags, rolling windows, seasonality)
- [ ] Create aggregation functions for weekly forecasting alignment
- [ ] Add visualization utilities
- [ ] Add data export functions for model integration

## Contributing

This is a research project. Contributions and suggestions are welcome.

## License

MIT License
