import pandas as pd
import json, os, sys
from pathlib import Path
from dotenv import load_dotenv

import logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

# Constants
REQUIRED_COLUMNS = ["c", "t"]

def create_dataframe(vars: dict) -> pd.DataFrame:
    """Loads data from JSON file and creates a DataFrame.
    
    Args:
        vars: Dictionary with configured variables
    
    Returns:
        pd.DataFrame: DataFrame with loaded data
    
    Raises:
        json.JSONDecodeError: If JSON is invalid
    """
    logging.info("Creating DataFrame from JSON file...")
    raw_data_path = vars["RAW_DATA_PATH"]
    
    try:
        with open(raw_data_path, "r") as f:
            data = json.load(f)
            logging.info(f"Data loaded successfully: {len(data)} records")
            return pd.json_normalize(data)
    except json.JSONDecodeError as e:
        logging.error(f"Error parsing JSON: {e}")
        raise

def select_columns(df: pd.DataFrame) -> pd.DataFrame:
    """Selects only the required columns.
    
    Args:
        df: Original DataFrame
    
    Returns:
        pd.DataFrame: DataFrame with selected columns
    """
    logging.info("Selecting required columns...")
    
    # Validate if columns exist
    missing_cols = [col for col in REQUIRED_COLUMNS if col not in df.columns]
    if missing_cols:
        logging.error(f"Missing columns: {missing_cols}")
        raise ValueError(f"Missing columns in DataFrame: {missing_cols}")
    
    return df[REQUIRED_COLUMNS]

def rename_columns(df: pd.DataFrame) -> pd.DataFrame:
    """Renames columns to more descriptive names.
    
    Args:
        df: DataFrame with original columns
    
    Returns:
        pd.DataFrame: DataFrame with renamed columns
    """
    logging.info("Renaming columns...")
    return df.rename(columns={
        "c": "current_price",
        "t": "timestamp"
    })

def to_time_format(df: pd.DataFrame, vars: dict) -> pd.DataFrame:
    """Converts timestamp column to datetime format.
    
    Args:
        df: DataFrame with timestamp in Unix format
        vars: Dictionary with configured variables
    
    Returns:
        pd.DataFrame: DataFrame with converted timestamp
    """
    logging.info("Converting timestamp to datetime format...")
    timezone = vars["TIMEZONE"]
    
    try:
        df["timestamp"] = pd.to_datetime(df["timestamp"], unit="s", utc=True).dt.tz_convert(timezone)
        logging.info(f"Timestamp converted to timezone: {timezone}")
    except Exception as e:
        logging.error(f"Error converting timestamp: {e}")
        raise
    return df

def transform_data(vars: dict) -> pd.DataFrame:
    """Executes the complete data transformation pipeline.
    
    Returns:
        pd.DataFrame: Transformed DataFrame
    """
    logging.info("Starting data transformation pipeline...")
    
    df = create_dataframe(vars)
    df = select_columns(df)
    df = rename_columns(df)
    df = to_time_format(df, vars)
    print(df)
    logging.info(f"Transformation completed: {len(df)} records processed")
    return df

if __name__ == "__main__":
    df = transform_data()
    print(df)