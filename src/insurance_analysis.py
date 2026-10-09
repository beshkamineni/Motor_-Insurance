from typing import Dict
import pandas as pd

# Portfolio Metrics
def calculate_total_customers(customers_df: pd.DataFrame) -> int:
    return int(customers_df['customer_id'].nunique())

def calculate_total_policies(policies_df: pd.DataFrame) -> int:
    return int(policies_df['policy_id'].nunique())

def calculate_active_policies(policies_df: pd.DataFrame) -> int:
    return int((policies_df['policy_status'] == 'Active').sum())

def calculate_expired_policies(policies_df: pd.DataFrame) -> int:
    return int((policies_df['policy_status'] == 'Expired').sum())

def calculate_cancelled_policies(policies_df: pd.DataFrame) -> int:
    return int((policies_df['policy_status'] == 'Cancelled').sum())

def calculate_renewed_policies(policies_df: pd.DataFrame) -> int:
    return int((policies_df['policy_status'] == 'Renewed').sum())

# Premium Metrics
def calculate_total_premium(policies_df: pd.DataFrame) -> float:
    return float(policies_df['premium_amount'].sum())

def calculate_average_premium(policies_df: pd.DataFrame) -> float:
    return float(policies_df['premium_amount'].mean()) if len(policies_df) > 0 else 0.0

def calculate_average_coverage(policies_df: pd.DataFrame) -> float:
    return float(policies_df['coverage_amount'].mean()) if len(policies_df) > 0 else 0.0

def calculate_premium_by_policy_type(policies_df: pd.DataFrame) -> pd.Series:
    return policies_df.groupby('policy_type')['premium_amount'].sum()

# Claim Metrics
def calculate_total_claims(claims_df: pd.DataFrame) -> int:
    return int(claims_df['claim_id'].nunique())

def calculate_approved_claims(claims_df: pd.DataFrame) -> int:
    return int(claims_df['claim_status'].isin(['Approved', 'Settled']).sum())

def calculate_rejected_claims(claims_df: pd.DataFrame) -> int:
    return int((claims_df['claim_status'] == 'Rejected').sum())

def calculate_pending_claims(claims_df: pd.DataFrame) -> int:
    return int((claims_df['claim_status'] == 'Pending').sum())

def calculate_total_claim_amount(claims_df: pd.DataFrame) -> float:
    return float(claims_df['claim_amount'].sum())

def calculate_average_claim_amount(claims_df: pd.DataFrame) -> float:
    return float(claims_df['claim_amount'].mean()) if len(claims_df) > 0 else 0.0

def calculate_claim_approval_rate(claims_df: pd.DataFrame) -> float:
    total = calculate_total_claims(claims_df)
    return round((calculate_approved_claims(claims_df) / total) * 100, 2) if total > 0 else 0.0

def calculate_claim_rejection_rate(claims_df: pd.DataFrame) -> float:
    total = calculate_total_claims(claims_df)
    return round((calculate_rejected_claims(claims_df) / total) * 100, 2) if total > 0 else 0.0

# Settlement Metrics
def calculate_average_claim_processing_days(claims_df: pd.DataFrame) -> float:
    valid = claims_df['claim_processing_days'].dropna()
    return round(float(valid.mean()), 2) if len(valid) > 0 else 0.0

def calculate_average_claim_settlement_days(claims_df: pd.DataFrame) -> float:
    valid = claims_df['claim_settlement_days'].dropna()
    return round(float(valid.mean()), 2) if len(valid) > 0 else 0.0

def calculate_total_payment_amount(payments_df: pd.DataFrame) -> float:
    return float(payments_df['payment_amount'].sum())

def calculate_average_payment_amount(payments_df: pd.DataFrame) -> float:
    return float(payments_df['payment_amount'].mean()) if len(payments_df) > 0 else 0.0

# Risk / Ratios
def calculate_claim_to_premium_ratio(claims_df: pd.DataFrame, policies_df: pd.DataFrame) -> float:
    tot_prem = calculate_total_premium(policies_df)
    tot_claim = calculate_total_claim_amount(claims_df)
    return round((tot_claim / tot_prem), 4) if tot_prem > 0 else 0.0

def calculate_claim_to_coverage_ratio(claims_df: pd.DataFrame, policies_df: pd.DataFrame) -> float:
    tot_cov = policies_df['coverage_amount'].sum()
    tot_claim = calculate_total_claim_amount(claims_df)
    return round((tot_claim / tot_cov), 4) if tot_cov > 0 else 0.0

def calculate_paid_claim_ratio(payments_df: pd.DataFrame, claims_df: pd.DataFrame) -> float:
    tot_claim = calculate_total_claim_amount(claims_df)
    tot_pay = calculate_total_payment_amount(payments_df)
    return round((tot_pay / tot_claim), 4) if tot_claim > 0 else 0.0

# Segment Analysis
def analyze_customer_claims(data: Dict[str, pd.DataFrame]) -> pd.DataFrame:
    m = data['claims'].merge(data['customers'], on='customer_id', how='left')
    return m.groupby('occupation').agg(
        claim_count=('claim_id', 'count'),
        total_amount=('claim_amount', 'sum'),
        avg_amount=('claim_amount', 'mean')
    ).reset_index()

def analyze_customer_premium(data: Dict[str, pd.DataFrame]) -> pd.DataFrame:
    m = data['policies'].merge(data['customers'], on='customer_id', how='left')
    return m.groupby('occupation').agg(
        policy_count=('policy_id', 'count'),
        total_premium=('premium_amount', 'sum'),
        avg_premium=('premium_amount', 'mean')
    ).reset_index()

def analyze_vehicle_claims(data: Dict[str, pd.DataFrame]) -> pd.DataFrame:
    m = data['claims'].merge(data['policies'], on='policy_id', how='left')
    m = m.merge(data['vehicles'], on='vehicle_id', how='left')
    return m.groupby('vehicle_type').agg(
        claim_count=('claim_id', 'count'),
        total_claim_amount=('claim_amount', 'sum'),
        avg_claim_amount=('claim_amount', 'mean')
    ).reset_index()

def analyze_vehicle_risk_patterns(data: Dict[str, pd.DataFrame]) -> pd.DataFrame:
    m = data['claims'].merge(data['policies'], on='policy_id', how='left')
    m = m.merge(data['vehicles'], on='vehicle_id', how='left')
    return m.groupby(['vehicle_type', 'fuel_type']).agg(
        claim_count=('claim_id', 'count'),
        avg_claim_amount=('claim_amount', 'mean'),
        avg_claim_to_premium=('claim_to_premium_ratio', 'mean')
    ).reset_index()

def analyze_claim_type(claims_df: pd.DataFrame) -> pd.DataFrame:
    return claims_df.groupby('claim_type').agg(
        count=('claim_id', 'count'),
        total_amount=('claim_amount', 'sum'),
        avg_amount=('claim_amount', 'mean')
    ).reset_index()

def analyze_claim_status(claims_df: pd.DataFrame) -> pd.DataFrame:
    return claims_df.groupby('claim_status').agg(
        count=('claim_id', 'count'),
        total_amount=('claim_amount', 'sum')
    ).reset_index()

def analyze_policy_type(policies_df: pd.DataFrame) -> pd.DataFrame:
    return policies_df.groupby('policy_type').agg(
        policy_count=('policy_id', 'count'),
        total_premium=('premium_amount', 'sum'),
        avg_premium=('premium_amount', 'mean')
    ).reset_index()

def analyze_region(data: Dict[str, pd.DataFrame]) -> pd.DataFrame:
    m = data['claims'].merge(data['customers'], on='customer_id', how='left')
    return m.groupby('state').agg(
        claim_count=('claim_id', 'count'),
        total_claim_amount=('claim_amount', 'sum'),
        avg_claim_amount=('claim_amount', 'mean')
    ).reset_index()

def analyze_vehicle_type(vehicles_df: pd.DataFrame) -> pd.DataFrame:
    return vehicles_df.groupby('vehicle_type').agg(
        vehicle_count=('vehicle_id', 'count'),
        avg_vehicle_value=('vehicle_value', 'mean'),
        avg_vehicle_age=('vehicle_age', 'mean')
    ).reset_index()

def analyze_damage_severity(claims_df: pd.DataFrame) -> pd.DataFrame:
    return claims_df.groupby('damage_severity').agg(
        count=('claim_id', 'count'),
        avg_claim_amount=('claim_amount', 'mean')
    ).reset_index()