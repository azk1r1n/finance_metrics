"""
Massive Flat Files Data Helper

Helper module for accessing historical market data from Massive.com (formerly Polygon.io)
flat files using S3. Supports stocks, options, indices, forex, and crypto data.

Flat files provide:
- Historical data going back to 2016 (trades) and 2022 (quotes) for options
- Daily updates after market close (available ~11 AM ET next day)
- CSV format with standardized headers
- Data from all 17 U.S. options exchanges (OPRA)
"""

import gzip
import os
from datetime import datetime
from pathlib import Path
from typing import List, Optional

import boto3
import pandas as pd
from botocore.config import Config
from dotenv import load_dotenv


class MassiveFlatFiles:
    """
    Access Massive.com flat files via S3 for historical market data.

    Supports:
    - US Stocks (SIP): trades, quotes, minute/daily aggregates
    - US Options (OPRA): trades, quotes, minute/daily aggregates
    - US Indices: minute/daily aggregates
    - Forex: trades, quotes, minute/daily aggregates
    - Crypto: trades, quotes, minute/daily aggregates
    """

    # Available prefixes (data types)
    PREFIXES = {
        "stocks_trades": "us_stocks_sip/trades_v1",
        "stocks_quotes": "us_stocks_sip/quotes_v1",
        "stocks_minute_agg": "us_stocks_sip/minute_aggs_v1",
        "stocks_daily_agg": "us_stocks_sip/day_aggs_v1",
        "options_trades": "us_options_opra/trades_v1",
        "options_quotes": "us_options_opra/quotes_v1",
        "options_minute_agg": "us_options_opra/minute_aggs_v1",
        "options_daily_agg": "us_options_opra/day_aggs_v1",
        "indices_minute_agg": "us_indices_sip/minute_aggs_v1",
        "indices_daily_agg": "us_indices_sip/day_aggs_v1",
        "forex_trades": "forex/trades_v1",
        "forex_quotes": "forex/quotes_v1",
        "crypto_trades": "crypto/trades_v1",
        "crypto_quotes": "crypto/quotes_v1",
    }

    def __init__(self):
        """Initialize Massive S3 client using credentials from .env file."""
        load_dotenv()

        # Load credentials
        self.access_key_id = os.getenv("MASSIVE_ACCESS_KEY_ID")
        self.secret_access_key = os.getenv("MASSIVE_SECRET_ACCESS_KEY")
        self.endpoint = os.getenv("MASSIVE_S3_ENDPOINT", "https://files.massive.com")
        self.bucket = os.getenv("MASSIVE_BUCKET", "flatfiles")

        if not self.access_key_id or not self.secret_access_key:
            raise ValueError(
                "MASSIVE_ACCESS_KEY_ID and MASSIVE_SECRET_ACCESS_KEY must be set in .env"
            )

        # Initialize S3 client
        session = boto3.Session(
            aws_access_key_id=self.access_key_id,
            aws_secret_access_key=self.secret_access_key,
        )

        self.s3 = session.client(
            "s3",
            endpoint_url=self.endpoint,
            config=Config(signature_version="s3v4"),
        )

    def list_files(
        self,
        prefix: str,
        max_results: int = 100,
        date_filter: Optional[str] = None,
    ) -> List[str]:
        """
        List available files for a given data type prefix.

        Args:
            prefix: Data type prefix (use PREFIXES dict or custom path)
            max_results: Maximum number of files to return
            date_filter: Optional date filter (YYYY-MM-DD format)

        Returns:
            List of S3 object keys (file paths)

        Example:
            >>> helper = MassiveFlatFiles()
            >>> files = helper.list_files("options_trades", date_filter="2024-11")
        """
        # Resolve prefix from PREFIXES dict if it's a key
        if prefix in self.PREFIXES:
            prefix = self.PREFIXES[prefix]

        # Add date filter to prefix if provided
        if date_filter:
            # Convert YYYY-MM-DD to path format YYYY/MM/
            date_parts = date_filter.split("-")
            if len(date_parts) >= 2:
                prefix = f"{prefix}/{date_parts[0]}/{date_parts[1]}"

        files = []
        paginator = self.s3.get_paginator("list_objects_v2")

        for page in paginator.paginate(
            Bucket=self.bucket,
            Prefix=prefix,
            PaginationConfig={"MaxItems": max_results},
        ):
            if "Contents" in page:
                for obj in page["Contents"]:
                    files.append(obj["Key"])

        return files

    def download_file(
        self,
        object_key: str,
        local_path: Optional[str] = None,
        decompress: bool = True,
    ) -> str:
        """
        Download a file from S3.

        Args:
            object_key: S3 object key (file path)
            local_path: Local file path (defaults to filename in current dir)
            decompress: If True, decompress .gz files after download

        Returns:
            Path to downloaded file

        Example:
            >>> helper = MassiveFlatFiles()
            >>> file_path = helper.download_file(
            ...     "us_options_opra/trades_v1/2024/11/2024-11-05.csv.gz"
            ... )
        """
        # Default local path is just the filename
        if local_path is None:
            local_path = object_key.split("/")[-1]

        # Create directory if needed
        Path(local_path).parent.mkdir(parents=True, exist_ok=True)

        # Download file
        self.s3.download_file(self.bucket, object_key, local_path)
        print(f"Downloaded: {local_path}")

        # Decompress if needed
        if decompress and local_path.endswith(".gz"):
            decompressed_path = local_path[:-3]  # Remove .gz extension
            with gzip.open(local_path, "rb") as f_in:
                with open(decompressed_path, "wb") as f_out:
                    f_out.write(f_in.read())
            print(f"Decompressed: {decompressed_path}")
            os.remove(local_path)  # Remove compressed file
            return decompressed_path

        return local_path

    def load_file_to_dataframe(
        self,
        object_key: str,
        nrows: Optional[int] = None,
    ) -> pd.DataFrame:
        """
        Download and load a CSV file directly into a pandas DataFrame.

        Args:
            object_key: S3 object key (file path)
            nrows: Optional limit on number of rows to read

        Returns:
            pandas DataFrame with the data

        Example:
            >>> helper = MassiveFlatFiles()
            >>> df = helper.load_file_to_dataframe(
            ...     "us_options_opra/trades_v1/2024/11/2024-11-05.csv.gz",
            ...     nrows=10000
            ... )
        """
        # Download to temp file
        local_path = self.download_file(object_key, decompress=True)

        # Load into DataFrame
        df = pd.read_csv(local_path, nrows=nrows)

        # Clean up temp file
        os.remove(local_path)

        return df

    def get_options_trades_for_date(
        self,
        date: str,
        nrows: Optional[int] = None,
    ) -> pd.DataFrame:
        """
        Get options trades data for a specific date.

        This is useful for calculating put/call ratios by analyzing
        volume for put vs call options.

        Args:
            date: Date in YYYY-MM-DD format
            nrows: Optional limit on number of rows

        Returns:
            DataFrame with options trade data

        Example:
            >>> helper = MassiveFlatFiles()
            >>> trades = helper.get_options_trades_for_date("2024-11-05")
            >>> # Filter for a specific underlying (e.g., SPY)
            >>> spy_trades = trades[trades['underlying_symbol'] == 'SPY']
        """
        # Convert date to file path
        dt = datetime.strptime(date, "%Y-%m-%d")
        object_key = (
            f"us_options_opra/trades_v1/{dt.year}/"
            f"{dt.month:02d}/{date}.csv.gz"
        )

        return self.load_file_to_dataframe(object_key, nrows=nrows)

    def get_options_daily_agg_for_date(
        self,
        date: str,
        nrows: Optional[int] = None,
    ) -> pd.DataFrame:
        """
        Get options daily aggregates (OHLCV) for a specific date.

        Daily aggregates are pre-calculated and include volume,
        which is useful for put/call ratio calculations.

        Args:
            date: Date in YYYY-MM-DD format
            nrows: Optional limit on number of rows

        Returns:
            DataFrame with options daily aggregate data

        Example:
            >>> helper = MassiveFlatFiles()
            >>> agg = helper.get_options_daily_agg_for_date("2024-11-05")
            >>> # Calculate put/call ratio
            >>> puts = agg[agg['contract_type'] == 'put']['volume'].sum()
            >>> calls = agg[agg['contract_type'] == 'call']['volume'].sum()
            >>> pc_ratio = puts / calls
        """
        # Convert date to file path
        dt = datetime.strptime(date, "%Y-%m-%d")
        object_key = (
            f"us_options_opra/day_aggs_v1/{dt.year}/"
            f"{dt.month:02d}/{date}.csv.gz"
        )

        return self.load_file_to_dataframe(object_key, nrows=nrows)

    def calculate_put_call_ratio_from_file(
        self,
        date: str,
        underlying_symbol: Optional[str] = None,
        use_trades: bool = False,
    ) -> dict:
        """
        Calculate put/call ratio for a specific date from flat files.

        Args:
            date: Date in YYYY-MM-DD format
            underlying_symbol: Filter by underlying (e.g., "SPY", "QQQ")
            use_trades: If True, use trade-level data; else use daily aggregates

        Returns:
            Dictionary with put_volume, call_volume, and put_call_ratio

        Example:
            >>> helper = MassiveFlatFiles()
            >>> ratio = helper.calculate_put_call_ratio_from_file(
            ...     "2024-11-05",
            ...     underlying_symbol="SPY"
            ... )
            >>> print(f"SPY Put/Call Ratio: {ratio['put_call_ratio']:.2f}")
        """
        # Get data
        if use_trades:
            df = self.get_options_trades_for_date(date)
            volume_col = "size"  # Trades use "size" column
        else:
            df = self.get_options_daily_agg_for_date(date)
            volume_col = "volume"  # Aggregates use "volume" column

        # Filter by underlying if specified
        if underlying_symbol:
            if "underlying_symbol" in df.columns:
                df = df[df["underlying_symbol"] == underlying_symbol]
            else:
                print(
                    f"Warning: 'underlying_symbol' column not found. "
                    f"Available columns: {df.columns.tolist()}"
                )

        # Calculate volumes (need to check actual column names)
        # Common column names: contract_type, option_type, put_call
        contract_type_col = None
        for col in ["contract_type", "option_type", "put_call"]:
            if col in df.columns:
                contract_type_col = col
                break

        if contract_type_col is None:
            raise ValueError(
                f"Cannot find contract type column. Available: {df.columns.tolist()}"
            )

        # Calculate put and call volumes
        put_volume = df[df[contract_type_col].str.lower() == "put"][volume_col].sum()
        call_volume = df[df[contract_type_col].str.lower() == "call"][volume_col].sum()

        # Calculate ratio
        if call_volume == 0:
            put_call_ratio = None
        else:
            put_call_ratio = put_volume / call_volume

        return {
            "date": date,
            "underlying_symbol": underlying_symbol or "ALL",
            "put_volume": put_volume,
            "call_volume": call_volume,
            "put_call_ratio": put_call_ratio,
        }

    def explore_file_structure(
        self,
        prefix: str = "",
        max_results: int = 20,
    ) -> None:
        """
        Explore the file structure to understand what's available.

        Args:
            prefix: Starting prefix (empty for root)
            max_results: Max files to show

        Example:
            >>> helper = MassiveFlatFiles()
            >>> helper.explore_file_structure("us_options_opra")
        """
        files = self.list_files(prefix, max_results=max_results)

        print(f"\n=== Files in '{prefix or 'root'}' ===")
        print(f"Showing up to {max_results} files:\n")

        for file in files:
            print(f"  {file}")

        print(f"\nTotal files shown: {len(files)}")
