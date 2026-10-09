import pytest
import pandas as pd
from src.validation import validate_customers, validate_policies, validate_claims, validate_relationships

@pytest.fixture
def mock_clean_data():
    customers = pd.DataFrame({
        'customer_id': ['C001', 'C002'],
        'customer_name': ['Alice', 'Bob'],
        'gender': ['F', 'M'],
        'date_of_birth': ['1990-01-01', '1985-05-12'],
        'age': [34, 39],
        'city': ['Mumbai', 'Delhi'],
        'state': ['Maharashtra', 'Delhi'],
        'occupation': ['Engineer', 'Doctor']
    })
    vehicles = pd.DataFrame({
        'vehicle_id': ['V001', 'V002'],
        'customer_id': ['C001', 'C002'],
        'vehicle_type': ['Sedan', 'SUV'],
        'vehicle_make': ['Toyota', 'Hyundai'],
        'vehicle_model': ['Corolla', 'Creta'],
        'vehicle_year': [2018, 2020],
        'fuel_type': ['Petrol', 'Diesel'],
        'vehicle_value': [800000, 1200000]
    })
    policies = pd.DataFrame({
        'policy_id': ['P001', 'P002'],
        'customer_id': ['C001', 'C002'],
        'vehicle_id': ['V001', 'V002'],
        'policy_start_date': ['2023-01-01', '2023-06-01'],
        'policy_end_date': ['2024-01-01', '2024-06-01'],
        'policy_type': ['Comprehensive', 'Third Party'],
        'premium_amount': [25000.0, 15000.0],
        'coverage_amount': [500000.0, 300000.0],
        'policy_status': ['Active', 'Expired'],
        'payment_frequency': ['Annual', 'Annual']
    })
    claims = pd.DataFrame({
        'claim_id': ['CLM001'],
        'policy_id': ['P001'],
        'customer_id': ['C001'],
        'claim_date': ['2023-04-10'],
        'accident_date': ['2023-04-09'],
        'claim_type': ['Accident'],
        'accident_location': ['Mumbai'],
        'claim_amount': [45000.0],
        'claim_status': ['Settled'],
        'approval_date': ['2023-04-12'],
        'settlement_date': ['2023-04-18'],
        'damage_severity': ['Medium']
    })
    payments = pd.DataFrame({
        'payment_id': ['PAY001'],
        'claim_id': ['CLM001'],
        'policy_id': ['P001'],
        'payment_date': ['2023-04-18'],
        'payment_amount': [45000.0],
        'payment_status': ['Completed'],
        'payment_method': ['Bank Transfer']
    })
    return {
        'customers': customers,
        'vehicles': vehicles,
        'policies': policies,
        'claims': claims,
        'payments': payments
    }

def test_validate_customers(mock_clean_data):
    assert validate_customers(mock_clean_data['customers']) is True
    corrupt = mock_clean_data['customers'].copy()
    corrupt.loc[0, 'age'] = -5
    with pytest.raises(ValueError):
        validate_customers(corrupt)

def test_validate_policies(mock_clean_data):
    assert validate_policies(mock_clean_data['policies']) is True
    corrupt = mock_clean_data['policies'].copy()
    corrupt.loc[0, 'policy_status'] = 'UnknownStatus'
    with pytest.raises(ValueError):
        validate_policies(corrupt)

def test_validate_claims(mock_clean_data):
    assert validate_claims(mock_clean_data['claims']) is True
    corrupt = mock_clean_data['claims'].copy()
    corrupt.loc[0, 'damage_severity'] = 'Critical'
    with pytest.raises(ValueError):
        validate_claims(corrupt)

def test_validate_relationships(mock_clean_data):
    assert validate_relationships(mock_clean_data) is True
    corrupt = {k: v.copy() for k, v in mock_clean_data.items()}
    corrupt['claims'].loc[0, 'policy_id'] = 'P9999'  # Non-existent policy
    with pytest.raises(ValueError):
        validate_relationships(corrupt)