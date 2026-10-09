import os
import pytest
import pandas as pd
from src.data_loader import load_all_data
from src.data_cleaner import remove_duplicates, create_derived_columns, clean_data, save_cleaned_data

@pytest.fixture
def sample_dataset(tmp_path):
    d = tmp_path / "raw"
    d.mkdir()
    cust = pd.DataFrame({
        'customer_id': ['C1', 'C2'], 'customer_name': ['A', 'B'], 'gender': ['F', 'M'],
        'date_of_birth': ['1990-01-01', '1985-01-01'], 'age': [34, 39], 'city': ['C1', 'C2'],
        'state': ['S1', 'S2'], 'occupation': ['O1', 'O2']
    })
    veh = pd.DataFrame({
        'vehicle_id': ['V1', 'V2'], 'customer_id': ['C1', 'C2'], 'vehicle_type': ['Sedan', 'SUV'],
        'vehicle_make': ['MakeA', 'MakeB'], 'vehicle_model': ['ModA', 'ModB'], 'vehicle_year': [2020, 2021],
        'fuel_type': ['Petrol', 'Diesel'], 'vehicle_value': [500000, 700000]
    })
    pol = pd.DataFrame({
        'policy_id': ['P1', 'P2'], 'customer_id': ['C1', 'C2'], 'vehicle_id': ['V1', 'V2'],
        'policy_start_date': ['2023-01-01', '2023-02-01'], 'policy_end_date': ['2024-01-01', '2024-02-01'],
        'policy_type': ['Comprehensive', 'Third Party'], 'premium_amount': [10000.0, 8000.0],
        'coverage_amount': [200000.0, 150000.0], 'policy_status': ['Active', 'Expired'],
        'payment_frequency': ['Annual', 'Annual']
    })
    clm = pd.DataFrame({
        'claim_id': ['CLM1'], 'policy_id': ['P1'], 'customer_id': ['C1'], 'claim_date': ['2023-05-01'],
        'accident_date': ['2023-04-30'], 'claim_type': ['Accident'], 'accident_location': ['Loc1'],
        'claim_amount': [20000.0], 'claim_status': ['Approved'], 'approval_date': ['2023-05-05'],
        'settlement_date': ['2023-05-10'], 'damage_severity': ['Low']
    })
    pay = pd.DataFrame({
        'payment_id': ['PAY1'], 'claim_id': ['CLM1'], 'policy_id': ['P1'],
        'payment_date': ['2023-05-10'], 'payment_amount': [20000.0], 'payment_status': ['Completed'],
        'payment_method': ['UPI']
    })
    cust.to_csv(d / "customers.csv", index=False)
    veh.to_csv(d / "vehicles.csv", index=False)
    pol.to_csv(d / "policies.csv", index=False)
    clm.to_csv(d / "claims.csv", index=False)
    pay.to_csv(d / "payments.csv", index=False)
    return str(d)

def test_load_all_data(sample_dataset):
    loaded = load_all_data(sample_dataset)
    assert set(loaded.keys()) == {"customers", "vehicles", "policies", "claims", "payments"}
    assert len(loaded['customers']) == 2

def test_remove_duplicates():
    df = pd.DataFrame({'a': [1, 1, 2], 'b': [3, 3, 4]})
    res = remove_duplicates({'t': df})
    assert len(res['t']) == 2

def test_create_derived_columns(sample_dataset):
    loaded = load_all_data(sample_dataset)
    cleaned = clean_data(loaded)
    pol = cleaned['policies']
    assert 'policy_duration_days' in pol.columns
    assert 'policy_active_flag' in pol.columns
    assert pol.loc[0, 'policy_active_flag'] == 1
    assert pol.loc[1, 'policy_active_flag'] == 0

def test_clean_data(sample_dataset):
    loaded = load_all_data(sample_dataset)
    res = clean_data(loaded)
    assert 'vehicle_age' in res['vehicles'].columns

def test_save_cleaned_data(sample_dataset, tmp_path):
    loaded = load_all_data(sample_dataset)
    cleaned = clean_data(loaded)
    out_dir = tmp_path / "cleaned"
    save_cleaned_data(cleaned, str(out_dir))
    assert os.path.exists(out_dir / "policies_cleaned.csv")