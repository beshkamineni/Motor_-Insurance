import pytest
import pandas as pd
from src.insurance_analysis import (
    calculate_total_policies,
    calculate_active_policies,
    calculate_total_claims,
    calculate_total_premium,
    calculate_claim_approval_rate,
    calculate_average_claim_amount
)

@pytest.fixture
def sample_analysis_data():
    policies = pd.DataFrame({
        'policy_id': ['P1', 'P2', 'P3'],
        'policy_status': ['Active', 'Expired', 'Active'],
        'premium_amount': [1000.0, 2000.0, 3000.0]
    })
    claims = pd.DataFrame({
        'claim_id': ['C1', 'C2', 'C3', 'C4'],
        'claim_status': ['Approved', 'Settled', 'Rejected', 'Pending'],
        'claim_amount': [100.0, 200.0, 300.0, 400.0]
    })
    return policies, claims

def test_calculate_total_policies(sample_analysis_data):
    p, _ = sample_analysis_data
    assert calculate_total_policies(p) == 3

def test_calculate_active_policies(sample_analysis_data):
    p, _ = sample_analysis_data
    assert calculate_active_policies(p) == 2

def test_calculate_total_claims(sample_analysis_data):
    _, c = sample_analysis_data
    assert calculate_total_claims(c) == 4

def test_calculate_total_premium(sample_analysis_data):
    p, _ = sample_analysis_data
    assert calculate_total_premium(p) == 6000.0

def test_calculate_claim_approval_rate(sample_analysis_data):
    _, c = sample_analysis_data
    # Approved + Settled = 2 out of 4 = 50.0%
    assert calculate_claim_approval_rate(c) == 50.0

def test_calculate_average_claim_amount(sample_analysis_data):
    _, c = sample_analysis_data
    assert calculate_average_claim_amount(c) == 250.0