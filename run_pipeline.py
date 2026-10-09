import os
import sys
from src.logger import setup_logger, log_pipeline_step, log_error
from src.data_loader import load_all_data
from src.validation import validate_all_tables
from src.data_cleaner import clean_data, save_cleaned_data

logger = setup_logger("run_pipeline")

def run_pipeline() -> None:
    """Entry point for standard loading, validation, cleaning, and persistence."""
    try:
        base_dir = os.path.dirname(os.path.abspath(__file__))
        raw_dir = os.path.join(base_dir, "data", "raw")
        cleaned_dir = os.path.join(base_dir, "data", "cleaned")
        
        log_pipeline_step(f"Starting Motor Insurance Pipeline from: {raw_dir}")
        data = load_all_data(raw_dir)
        
        log_pipeline_step("Initiating schema and referential integrity validation")
        validate_all_tables(data)
        
        log_pipeline_step("Executing data cleaning and feature engineering")
        cleaned_data = clean_data(data)
        
        log_pipeline_step(f"Saving cleaned tables to: {cleaned_dir}")
        save_cleaned_data(cleaned_data, cleaned_dir)
        
        log_pipeline_step("Pipeline execution successfully completed.")
    except Exception as exc:
        log_error(f"Pipeline crashed with exception: {exc}")
        sys.exit(1)

if __name__ == "__main__":
    run_pipeline()