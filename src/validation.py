from typing import Dict, List
import pandas as pd
from src.logger import setup_logger, log_error

logger = setup_logger("validation")

def _check_columns(df: pd.DataFrame, required: List[str], table_name: str) -> bool:
    missing = [c for c in required if c not in df.columns]
    if missing:
        msg = f"Table '{table_name}' missing columns: {missing}"
        log_error(msg)
        raise ValueError(msg)
    return True

def validate_customers(df: pd.DataFrame) -> bool:
    """Validates customers table schema, primary keys, and ranges."""
    req = ['customer_id', 'customer_name', 'gender', 'date_of_birth', 'age', 'city', 'state', 'occupation']
    _check_columns(df, req, 'customers')
    if df['customer_id'].isnull().any():
        raise ValueError("Missing customer_id detected.")
    if df['customer_id'].duplicated().any():
        raise ValueError("Duplicate customer_id detected.")
    if (df['age'] < 16).any() or (df['age'] > 120).any():
        raise ValueError("Unrealistic age boundaries detected in customers.")
    return True

def validate_vehicles(df: pd.DataFrame) -> bool:
    """Validates vehicles table schema, identifiers, and valuations."""
    req = ['vehicle_id', 'customer_id', 'vehicle_type', 'vehicle_make', 'vehicle_model', 'vehicle_year', 'fuel_type', 'vehicle_value']
    _check_columns(df, req, 'vehicles')
    if df['vehicle_id'].isnull().any():
        raise ValueError("Missing vehicle_id detected.")
    if df['vehicle_id'].duplicated().any():
        raise ValueError("Duplicate vehicle_id detected.")
    if (df['vehicle_value'] <= 0).any():
        raise ValueError("Non-positive vehicle_value detected.")
    return True

def validate_policies(df: pd.DataFrame) -> bool:
    """Validates policies table structure, financial bounds, and valid statuses."""
    req = ['policy_id', 'customer_id', 'vehicle_id', 'policy_start_date', 'policy_end_date',
           'policy_type', 'premium_amount', 'coverage_amount', 'policy_status', 'payment_frequency']
    _check_columns(df, req, 'policies')
    if df['policy_id'].isnull().any():
        raise ValueError("Missing policy_id detected.")
    if df['policy_id'].duplicated().any():
        raise ValueError("Duplicate policy_id detected.")
    if (df['premium_amount'] < 0).any() or (df['coverage_amount'] <= 0).any():
        raise ValueError("Invalid financial values detected in policies.")
    valid_statuses = {'Active', 'Expired', 'Cancelled', 'Renewed'}
    if not set(df['policy_status'].unique()).issubset(valid_statuses):
        raise ValueError("Unknown policy_status value encountered.")
    return True

def validate_claims(df: pd.DataFrame) -> bool:
    """Validates claims table structure, foreign keys, and severity levels."""
    req = ['claim_id', 'policy_id', 'customer_id', 'claim_date', 'accident_date',
           'claim_type', 'accident_location', 'claim_amount', 'claim_status',
           'approval_date', 'settlement_date', 'damage_severity']
    _check_columns(df, req, 'claims')
    if df['claim_id'].isnull().any():
        raise ValueError("Missing claim_id detected.")
    if df['claim_id'].duplicated().any():
        raise ValueError("Duplicate claim_id detected.")
    if (df['claim_amount'] < 0).any():
        raise ValueError("Negative claim_amount detected.")
    valid_statuses = {'Pending', 'Approved', 'Rejected', 'Settled'}
    if not set(df['claim_status'].unique()).issubset(valid_statuses):
        raise ValueError("Unknown claim_status value encountered.")
    valid_severity = {'Low', 'Medium', 'High'}
    if not set(df['damage_severity'].unique()).issubset(valid_severity):
        raise ValueError("Unknown damage_severity value encountered.")
    return True

def validate_payments(df: pd.DataFrame) -> bool:
    """Validates payments schema and non-negative settlement transactions."""
    req = ['payment_id', 'claim_id', 'policy_id', 'payment_date', 'payment_amount', 'payment_status', 'payment_method']
    _check_columns(df, req, 'payments')
    if df['payment_id'].isnull().any():
        raise ValueError("Missing payment_id detected.")
    if df['payment_id'].duplicated().any():
        raise ValueError("Duplicate payment_id detected.")
    if (df['payment_amount'] < 0).any():
        raise ValueError("Negative payment_amount detected.")
    return True

def validate_relationships(data: Dict[str, pd.DataFrame]) -> bool:
    """Validates referential integrity across all operational entities."""
    cust_ids = set(data['customers']['customer_id'])
    veh_ids = set(data['vehicles']['vehicle_id'])
    pol_ids = set(data['policies']['policy_id'])
    clm_ids = set(data['claims']['claim_id'])

    # Vehicles -> Customers
    if not set(data['vehicles']['customer_id']).issubset(cust_ids):
        raise ValueError("Referential integrity failed: vehicles.customer_id missing in customers.")
    # Policies -> Customers
    if not set(data['policies']['customer_id']).issubset(cust_ids):
        raise ValueError("Referential integrity failed: policies.customer_id missing in customers.")
    # Policies -> Vehicles
    if not set(data['policies']['vehicle_id']).issubset(veh_ids):
        raise ValueError("Referential integrity failed: policies.vehicle_id missing in vehicles.")
    # Claims -> Policies
    if not set(data['claims']['policy_id']).issubset(pol_ids):
        raise ValueError("Referential integrity failed: claims.policy_id missing in policies.")
    # Payments -> Claims
    if not set(data['payments']['claim_id']).issubset(clm_ids):
        raise ValueError("Referential integrity failed: payments.claim_id missing in claims.")
    return True

def validate_all_tables(data: Dict[str, pd.DataFrame]) -> bool:
    """Executes table-level and relational integrity validations."""
    logger.info("Starting schema and relational integrity validation.")
    validate_customers(data['customers'])
    validate_vehicles(data['vehicles'])
    validate_policies(data['policies'])
    validate_claims(data['claims'])
    validate_payments(data['payments'])
    validate_relationships(data)
    logger.info("All table and relational checks passed successfully.")
    return True