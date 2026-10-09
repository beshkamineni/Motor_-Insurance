import os
from typing import Dict
import pandas as pd
from src.logger import setup_logger, log_error

logger = setup_logger("data_loader")

REQUIRED_TABLES = ["customers", "vehicles", "policies", "claims", "payments"]

def check_file_exists(file_path: str) -> bool:
    """Validates physical file existence on disk."""
    exists = os.path.isfile(file_path)
    if not exists:
        logger.warning(f"File not found: {file_path}")
    return exists

def load_table(file_path: str) -> pd.DataFrame:
    """Loads an individual CSV table into a pandas DataFrame."""
    if not check_file_exists(file_path):
        err = f"Target table file missing: {file_path}"
        log_error(err)
        raise FileNotFoundError(err)
    
    try:
        df = pd.read_csv(file_path)
        logger.info(f"Loaded {os.path.basename(file_path)}: {df.shape[0]} rows, {df.shape[1]} columns")
        return df
    except Exception as exc:
        log_error(f"Failed loading {file_path}: {exc}")
        raise exc

def load_all_data(data_dir: str) -> Dict[str, pd.DataFrame]:
    """Loads all mandatory operational tables from the specified directory."""
    logger.info(f"Starting bulk ingestion from: {data_dir}")
    data: Dict[str, pd.DataFrame] = {}
    for table in REQUIRED_TABLES:
        csv_file = os.path.join(data_dir, f"{table}.csv")
        data[table] = load_table(csv_file)
    logger.info("All 5 operational tables successfully ingested.")
    return data