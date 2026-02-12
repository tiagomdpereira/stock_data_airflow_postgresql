import os, requests, json, sys
from dotenv import load_dotenv
from pathlib import Path

import logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

# Constants
REQUEST_TIMEOUT = 30  # seconds
HTTP_OK = 200

def extract_data(url: str, vars: dict) -> dict:
    """Extracts data from API and saves to JSON file.
    
    Args:
        url: API endpoint URL
        vars: Dictionary with configured variables
    
    Returns:
        dict: Extracted data from API
    
    Raises:
        requests.RequestException: If API request fails
        ValueError: If no data is returned
    """
    logging.info(f"Fetching data from API...")

    raw_data_path = vars["RAW_DATA_PATH"]
    raw_data_dir = raw_data_path.parent
    
    # Create output directory if it doesn't exist
    raw_data_dir.mkdir(parents=True, exist_ok=True)
    logging.info(f"Output directory ready: {raw_data_dir}")

    # Make API request
    try:
        response = requests.get(url, timeout=REQUEST_TIMEOUT)
        response.raise_for_status()
    except requests.Timeout:
        logging.error(f"Request timeout after {REQUEST_TIMEOUT} seconds")
        raise
    except requests.RequestException as e:
        logging.error(f"Error fetching data from API: {e}")
        raise
    
    if response.status_code != HTTP_OK:
        logging.error(f"Unexpected status code: {response.status_code}")
        raise ValueError(f"API returned status code {response.status_code}")
    
    logging.info(f"API response received successfully (status: {response.status_code})")

    # Parse JSON response
    try:
        data = response.json()
    except json.JSONDecodeError as e:
        logging.error(f"Error parsing JSON response: {e}")
        raise
    
    if not data:
        logging.warning("No data returned from API")
        raise ValueError("API returned empty data")
    
    logging.info(f"Data extracted successfully: {len(data)} fields")

    # Save data to file
    try:
        with open(raw_data_path, "w") as f:
            json.dump(data, f, indent=4)
        logging.info(f"File saved successfully: {raw_data_path}")
    except IOError as e:
        logging.error(f"Error writing file: {e}")
        raise
    
    return data