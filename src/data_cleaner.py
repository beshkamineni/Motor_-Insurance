import os
from typing import Dict
import pandas as pd
import numpy as np
from src.logger import setup_logger

logger = setup_logger("data_cleaner")

def handle_missing_values(data: Dict[str, pd.DataFrame]) -> Dict[str, pd.DataFrame]:
    """Handles missing operational values systematically across all dataframes."""
    cleaned = {k: v.copy() for k, v in data.items()}
    # Fill potential text nulls
    for name in ['customers', 'vehicles', 'policies']:
        for col in cleaned[name].select_dtypes(include='object').columns:
            cleaned[name][col] = cleaned[name][col].fillna('Unknown')
            
    # For claims: approval_date and settlement_date are logically null for pending/rejected
    cleaned['claims']['claim_status'] = cleaned['claims']['claim_status'].fillna('Pending')
    cleaned['claims']['damage_severity'] = cleaned['claims']['damage_severity'].fillna('Medium')
    return cleaned

def remove_duplicates(data: Dict[str, pd.DataFrame]) -> Dict[str, pd.DataFrame]:
    """Eliminates redundant records across operational tables."""
    cleaned = {k: v.drop_duplicates().copy() for k, v in data.items()}
    return cleaned

def clean_text_columns(data: Dict[str, pd.DataFrame]) -> Dict[str, pd.DataFrame]:
    """Standardizes string casing and strips trailing whitespace."""
    cleaned = {k: v.copy() for k, v in data.items()}
    for name, df in cleaned.items():
        for col in df.select_dtypes(include='object').columns:
            if 'date' not in col.lower():
                cleaned[name][col] = df[col].astype(str).str.strip()
    return cleaned

def clean_date_columns(data: Dict[str, pd.DataFrame]) -> Dict[str, pd.DataFrame]:
    """Converts temporal strings into standard datetime objects."""
    cleaned = {k: v.copy() for k, v in data.items()}
    cleaned['customers']['date_of_birth'] = pd.to_datetime(cleaned['customers']['date_of_birth'], errors='coerce')
    cleaned['policies']['policy_start_date'] = pd.to_datetime(cleaned['policies']['policy_start_date'], errors='coerce')
    cleaned['policies']['policy_end_date'] = pd.to_datetime(cleaned['policies']['policy_end_date'], errors='coerce')
    cleaned['claims']['claim_date'] = pd.to_datetime(cleaned['claims']['claim_date'], errors='coerce')
    cleaned['claims']['accident_date'] = pd.to_datetime(cleaned['claims']['accident_date'], errors='coerce')
    cleaned['claims']['approval_date'] = pd.to_datetime(cleaned['claims']['approval_date'], errors='coerce')
    cleaned['claims']['settlement_date'] = pd.to_datetime(cleaned['claims']['settlement_date'], errors='coerce')
    cleaned['payments']['payment_date'] = pd.to_datetime(cleaned['payments']['payment_date'], errors='coerce')
    return cleaned

def validate_numeric_columns(data: Dict[str, pd.DataFrame]) -> Dict[str, pd.DataFrame]:
    """Ensures numeric series match expected domain bounds."""
    cleaned = {k: v.copy() for k, v in data.items()}
    cleaned['policies']['premium_amount'] = cleaned['policies']['premium_amount'].clip(lower=0)
    cleaned['policies']['coverage_amount'] = cleaned['policies']['coverage_amount'].clip(lower=0)
    cleaned['claims']['claim_amount'] = cleaned['claims']['claim_amount'].clip(lower=0)
    cleaned['payments']['payment_amount'] = cleaned['payments']['payment_amount'].clip(lower=0)
    return cleaned

def validate_business_rules(data: Dict[str, pd.DataFrame]) -> Dict[str, pd.DataFrame]:
    """Enforces motor insurance domain rules across dates and amounts."""
    cleaned = {k: v.copy() for k, v in data.items()}
    # End date must be >= start date
    pol = cleaned['policies']
    invalid_dates = pol['policy_end_date'] < pol['policy_start_date']
    if invalid_dates.any():
        logger.warning(f"Fixing {invalid_dates.sum()} policies where end_date < start_date.")
        pol.loc[invalid_dates, 'policy_end_date'] = pol.loc[invalid_dates, 'policy_start_date']
    return cleaned

def create_derived_columns(data: Dict[str, pd.DataFrame]) -> Dict[str, pd.DataFrame]:
    """Computes all domain-specific derived attributes required by specifications."""
    cleaned = {k: v.copy() for k, v in data.items()}
    now_year = 2026

    # Customers: customer_age
    cust = cleaned['customers']
    dob_years = (pd.to_datetime('today') - cust['date_of_birth']).dt.days // 365.25
    cust['customer_age'] = dob_years.fillna(cust['age']).astype(int)

    # Vehicles: vehicle_age
    veh = cleaned['vehicles']
    veh['vehicle_age'] = (now_year - veh['vehicle_year']).clip(lower=0)

    # Policies: policy_duration_days, policy_active_flag
    pol = cleaned['policies']
    pol['policy_duration_days'] = (pol['policy_end_date'] - pol['policy_start_date']).dt.days.clip(lower=0)
    pol['policy_active_flag'] = (pol['policy_status'] == 'Active').astype(int)

    # Claims: claim_processing_days, claim_settlement_days
    clm = cleaned['claims']
    clm['claim_processing_days'] = (clm['approval_date'] - clm['claim_date']).dt.days
    clm['claim_settlement_days'] = (clm['settlement_date'] - clm['claim_date']).dt.days

    # Merged ratios: claim_to_premium_ratio, claim_to_coverage_ratio
    clm_pol_merged = clm[['claim_id', 'policy_id', 'claim_amount']].merge(
        pol[['policy_id', 'premium_amount', 'coverage_amount']],
        on='policy_id',
        how='left'
    )
    clm['claim_to_premium_ratio'] = np.where(
        clm_pol_merged['premium_amount'] > 0,
        clm_pol_merged['claim_amount'] / clm_pol_merged['premium_amount'],
        0.0
    )
    clm['claim_to_coverage_ratio'] = np.where(
        clm_pol_merged['coverage_amount'] > 0,
        clm_pol_merged['claim_amount'] / clm_pol_merged['coverage_amount'],
        0.0
    )

    # Payments: paid_claim_ratio
    pay = cleaned['payments']
    pay_clm_merged = pay[['payment_id', 'claim_id', 'payment_amount']].merge(
        clm[['claim_id', 'claim_amount']],
        on='claim_id',
        how='left'
    )
    pay['paid_claim_ratio'] = np.where(
        pay_clm_merged['claim_amount'] > 0,
        pay_clm_merged['payment_amount'] / pay_clm_merged['claim_amount'],
        0.0
    )

    return cleaned

def clean_data(data: Dict[str, pd.DataFrame]) -> Dict[str, pd.DataFrame]:
    """Executes the complete operational data cleaning and enrichment lifecycle."""
    logger.info("Executing clean_data pipeline sequence.")
    data = handle_missing_values(data)
    data = remove_duplicates(data)
    data = clean_text_columns(data)
    data = clean_date_columns(data)
    data = validate_numeric_columns(data)
    data = validate_business_rules(data)
    data = create_derived_columns(data)
    logger.info("Data cleaning and feature enrichment completed successfully.")
    return data

def save_cleaned_data(data: Dict[str, pd.DataFrame], output_dir: str) -> None:
    """Persists cleaned tables to CSV in the standardized directory."""
    os.makedirs(output_dir, exist_ok=True)
    for table_name, df in data.items():
        out_path = os.path.join(output_dir, f"{table_name}_cleaned.csv")
        df.to_csv(out_path, index=False)
        logger.info(f"Saved: {out_path} ({df.shape[0]} rows)")