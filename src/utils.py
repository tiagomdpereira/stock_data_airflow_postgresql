import logging, os
from pathlib import Path
from dotenv import load_dotenv

def get_variables() -> dict:
    """Loads and validates all required environment variables.
    
    Returns:
        dict: Dictionary with all configured variables
    
    Raises:
        FileNotFoundError: If .env file does not exist
        ValueError: If required environment variables are not defined
    """
    logging.info("Loading environment variables...")
    
    proj_path = Path(__file__).parent.parent
    env_file_path = proj_path / "config" / ".env"
    
    if not env_file_path.exists():
        logging.error(f".env file not found: {env_file_path}")
        raise FileNotFoundError(f".env file not found: {env_file_path}")
    
    load_dotenv(env_file_path)
    
    # Validate API_KEY
    api_key = os.getenv("API_KEY")
    if not api_key:
        logging.error("API_KEY variable not defined in .env")
        raise ValueError("API_KEY variable not defined in .env")
    
    # Validate TIMEZONE
    timezone = os.getenv("TIMEZONE")
    if not timezone:
        logging.error("TIMEZONE variable not defined in .env")
        raise ValueError("TIMEZONE variable not defined in .env")

    # Validate SYMBOL
    symbol = os.getenv("SYMBOL")
    if not symbol:
        logging.error("SYMBOL variable not defined in .env")
        raise ValueError("SYMBOL variable not defined in .env")
    
    # Validate RAW_DATA_PATH
    raw_data_path_str = os.getenv("RAW_DATA_PATH")
    if not raw_data_path_str:
        logging.error("RAW_DATA_PATH variable not defined in .env")
        raise ValueError("RAW_DATA_PATH variable not defined in .env")
    
    raw_data_path = proj_path / raw_data_path_str
    
    logging.info("Variables loaded successfully")
    
    return {
        "PROJ_PATH": proj_path,
        "API_KEY": api_key,
        "SYMBOL": symbol,
        "RAW_DATA_PATH": raw_data_path,
        "TIMEZONE": timezone
    }

def get_postgres_variables() -> dict:
    """Loads and validates postgres required environment variables.
    
    Returns:
        dict: Dictionary with postgres configured variables
    
    Raises:
        FileNotFoundError: If .env file does not exist
        ValueError: If required environment variables are not defined
    """

    logging.info("Loading environment variables...")
    
    proj_path = Path(__file__).parent.parent
    env_file_path = proj_path / "config" / ".env"
    
    if not env_file_path.exists():
        logging.error(f".env file not found: {env_file_path}")
        raise FileNotFoundError(f".env file not found: {env_file_path}")
    
    load_dotenv(env_file_path)

    user = os.getenv("USER")
    if not user:
        logging.error("USER variable not defined in .env")
        raise ValueError("USER variable not defined in .env")
    
    password = os.getenv("PASSWORD")
    if not password:
        logging.error("PASSWORD variable not defined in .env")
        raise ValueError("APASSWORDv")
    
    host = os.getenv("HOST")
    if not host:
        logging.error("HOST variable not defined in .env")
        raise ValueError("HOST variable not defined in .env")
    
    port = os.getenv("PORT")
    if not port:
        logging.error("PORT variable not defined in .env")
        raise ValueError("PORT variable not defined in .env")
    
    database = os.getenv("DATABASE")
    if not database:
        logging.error("DATABASE variable not defined in .env")
        raise ValueError("DATABASE variable not defined in .env")
    
    return {
        "USER": user,
        "PASSWORD": password,
        "HOST": host,
        "PORT": port,
        "DATABASE": database,
    }

