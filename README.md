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

## Setup

1. **Install dependencies:**
```bash
uv sync
```

2. **Set up FRED API key:**

Create a `.env` file in the project root with your FRED API key:
```bash
FRED_API_KEY=your_api_key_here
```

Get a free API key from: https://fred.stlouisfed.org/docs/api/api_key.html

## Quick Start

```python
from finance_metrics import MarketIndices, CommodityPrices, MacroIndicators, ConsumerMetrics, CustomMetrics

# Fetch S&P 500 data
market = MarketIndices()
sp500 = market.get_index("sp500", start_date="2023-01-01", end_date="2024-01-01")

# Fetch crude oil prices
commodities = CommodityPrices()
oil = commodities.get_commodity("crude_oil_wti", start_date="2023-01-01")

# Fetch macroeconomic data
macro = MacroIndicators()
unemployment = macro.get_unemployment_rate(start_date="2023-01-01")
inflation = macro.get_inflation_rate(start_date="2023-01-01")

# Fetch consumer metrics
consumer = ConsumerMetrics()
sentiment = consumer.get_consumer_sentiment(start_date="2023-01-01")
retail_sales = consumer.get_retail_sales(start_date="2023-01-01")

# Calculate custom metrics
custom = CustomMetrics()
qqq_deviation = custom.get_meitou_qqq_deviation(start_date="2023-01-01")
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

### MacroIndicators
Macroeconomic data from FRED API:
- GDP and GDP growth rates
- Inflation metrics (CPI, PPI) with year-over-year calculations
- Unemployment rates
- Interest rates (Federal Funds, 10-Year Treasury)
- Housing starts

### ConsumerMetrics
Consumer-focused economic indicators from FRED API:
- Consumer Sentiment (University of Michigan)
- Consumer Confidence (OECD)
- Retail Sales with growth calculations
- Personal Consumption Expenditures (PCE)
- Disposable Personal Income
- Personal Saving Rate
- Consumer Credit

### CustomMetrics
Custom financial metrics and technical indicators:
- **MeiTou QQQ 200 Days Deviation Index**: Measures how far QQQ (Nasdaq-100 ETF) is trading from its 200-day simple moving average
  - Formula: `(QQQ price - SMA_200) / SMA_200`
  - Provides trading signals (Strong Bullish/Bullish/Bearish/Strong Bearish)
  - Available in both daily and weekly formats for forecasting alignment

## Data Sources

- **Market & Commodity Data**: Yahoo Finance (via yfinance)
- **Macro & Consumer Data**: Federal Reserve Economic Data (FRED) - requires API key

## Features

✅ **Implemented:**
- Market indices and commodity prices (daily/weekly data via yfinance)
- Macroeconomic indicators (monthly/quarterly data via FRED)
- Consumer metrics (monthly data via FRED)
- Weekly data aggregation from mixed frequencies
- Year-over-year growth calculations
- Multi-indicator fetching

**Roadmap:**
- [ ] Add data caching mechanisms
- [ ] Implement data quality checks and outlier detection
- [ ] Add feature engineering utilities (lags, rolling windows, seasonality)
- [ ] Add visualization utilities
- [ ] Build correlation analysis tools
- [ ] Add data export functions for model integration

## Contributing

This is a research project. Contributions and suggestions are welcome.

## License

MIT License
