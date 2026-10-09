import os
import streamlit as st
import pandas as pd
import numpy as np

from src.data_loader import load_table
from src.insurance_analysis import (
    calculate_total_customers, calculate_total_policies, calculate_active_policies,
    calculate_total_premium, calculate_average_premium, calculate_average_coverage,
    calculate_total_claims, calculate_approved_claims, calculate_rejected_claims,
    calculate_pending_claims, calculate_total_claim_amount, calculate_average_claim_amount,
    calculate_claim_approval_rate, calculate_claim_rejection_rate,
    calculate_average_claim_settlement_days, calculate_average_claim_processing_days,
    calculate_total_payment_amount, calculate_claim_to_premium_ratio,
    calculate_claim_to_coverage_ratio, calculate_paid_claim_ratio
)
from src.visualization import (
    plot_policy_status, plot_policy_type_distribution, plot_premium_by_policy_type,
    plot_monthly_claims, plot_claim_status, plot_claim_type_distribution,
    plot_claim_amount_distribution, plot_claim_amount_by_vehicle_type,
    plot_claims_by_region, plot_claim_severity_by_region, plot_average_settlement_time,
    plot_claim_to_premium_by_policy_type, plot_vehicle_age_vs_claim_amount,
    plot_customer_age_vs_claim_amount, plot_vehicle_type_claim_performance,
    plot_damage_severity_distribution, plot_payment_status, plot_monthly_premium_trend
)
from src.insights import (
    generate_portfolio_insights, generate_claim_insights, generate_premium_insights,
    generate_customer_insights, generate_vehicle_insights, generate_risk_patterns,
    generate_business_recommendations
)

st.set_page_config(
    page_title="Motor Insurance Analytics Portal",
    page_icon="🚗",
    layout="wide",
    initial_sidebar_state="expanded"
)

@st.cache_data
def load_dashboard_data():
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    clean_dir = os.path.join(base_dir, "data", "cleaned")
    raw_dir = os.path.join(base_dir, "data", "raw")
    target_dir = clean_dir if os.path.exists(os.path.join(clean_dir, "policies_cleaned.csv")) else raw_dir
    prefix = "_cleaned.csv" if target_dir == clean_dir else ".csv"

    customers = load_table(os.path.join(target_dir, f"customers{prefix}"))
    vehicles = load_table(os.path.join(target_dir, f"vehicles{prefix}"))
    policies = load_table(os.path.join(target_dir, f"policies{prefix}"))
    claims = load_table(os.path.join(target_dir, f"claims{prefix}"))
    payments = load_table(os.path.join(target_dir, f"payments{prefix}"))

    # Parse dates if not already parsed
    policies['policy_start_date'] = pd.to_datetime(policies['policy_start_date'])
    policies['policy_end_date'] = pd.to_datetime(policies['policy_end_date'])
    claims['claim_date'] = pd.to_datetime(claims['claim_date'])
    if 'approval_date' in claims.columns:
        claims['approval_date'] = pd.to_datetime(claims['approval_date'])
    if 'settlement_date' in claims.columns:
        claims['settlement_date'] = pd.to_datetime(claims['settlement_date'])
    payments['payment_date'] = pd.to_datetime(payments['payment_date'])

    return {
        'customers': customers,
        'vehicles': vehicles,
        'policies': policies,
        'claims': claims,
        'payments': payments
    }

def show_sidebar_filters(data):
    st.sidebar.header("🔍 Global Operational Filters")
    
    # Filter 1: Policy Type
    pol_types = ["All"] + sorted(list(data['policies']['policy_type'].dropna().unique()))
    sel_pol_type = st.sidebar.selectbox("Policy Type", pol_types)
    
    # Filter 2: Policy Status
    pol_statuses = ["All"] + sorted(list(data['policies']['policy_status'].dropna().unique()))
    sel_pol_status = st.sidebar.selectbox("Policy Status", pol_statuses)
    
    # Filter 3: Claim Status
    claim_statuses = ["All"] + sorted(list(data['claims']['claim_status'].dropna().unique()))
    sel_claim_status = st.sidebar.selectbox("Claim Status", claim_statuses)
    
    # Filter 4: Claim Type
    claim_types = ["All"] + sorted(list(data['claims']['claim_type'].dropna().unique()))
    sel_claim_type = st.sidebar.selectbox("Claim Incident Type", claim_types)
    
    # Filter 5: Vehicle Type
    veh_types = ["All"] + sorted(list(data['vehicles']['vehicle_type'].dropna().unique()))
    sel_veh_type = st.sidebar.selectbox("Vehicle Class", veh_types)

    # Filter 6: Vehicle Make
    veh_makes = ["All"] + sorted(list(data['vehicles']['vehicle_make'].dropna().unique()))
    sel_veh_make = st.sidebar.selectbox("Vehicle Manufacturer", veh_makes)

    # Filter 7: State
    states = ["All"] + sorted(list(data['customers']['state'].dropna().unique()))
    sel_state = st.sidebar.selectbox("Customer Geography (State)", states)

    # Filter 8: Damage Severity
    severities = ["All"] + sorted(list(data['claims']['damage_severity'].dropna().unique()))
    sel_severity = st.sidebar.selectbox("Damage Severity", severities)

    # Apply Filters
    filtered_pol = data['policies'].copy()
    if sel_pol_type != "All":
        filtered_pol = filtered_pol[filtered_pol['policy_type'] == sel_pol_type]
    if sel_pol_status != "All":
        filtered_pol = filtered_pol[filtered_pol['policy_status'] == sel_pol_status]

    filtered_claims = data['claims'].copy()
    if sel_claim_status != "All":
        filtered_claims = filtered_claims[filtered_claims['claim_status'] == sel_claim_status]
    if sel_claim_type != "All":
        filtered_claims = filtered_claims[filtered_claims['claim_type'] == sel_claim_type]
    if sel_severity != "All":
        filtered_claims = filtered_claims[filtered_claims['damage_severity'] == sel_severity]

    filtered_veh = data['vehicles'].copy()
    if sel_veh_type != "All":
        filtered_veh = filtered_veh[filtered_veh['vehicle_type'] == sel_veh_type]
    if sel_veh_make != "All":
        filtered_veh = filtered_veh[filtered_veh['vehicle_make'] == sel_veh_make]

    filtered_cust = data['customers'].copy()
    if sel_state != "All":
        filtered_cust = filtered_cust[filtered_cust['state'] == sel_state]

    # Inter-table synchronization via relational keys
    valid_cust = set(filtered_cust['customer_id'])
    valid_veh = set(filtered_veh['vehicle_id'])
    filtered_pol = filtered_pol[filtered_pol['customer_id'].isin(valid_cust) & filtered_pol['vehicle_id'].isin(valid_veh)]

    valid_pol = set(filtered_pol['policy_id'])
    filtered_claims = filtered_claims[filtered_claims['policy_id'].isin(valid_pol)]

    valid_clm = set(filtered_claims['claim_id'])
    filtered_pay = data['payments'][data['payments']['claim_id'].isin(valid_clm)]

    return {
        'customers': filtered_cust,
        'vehicles': filtered_veh,
        'policies': filtered_pol,
        'claims': filtered_claims,
        'payments': filtered_pay
    }

def render_insight_cards(cards):
    for c in cards:
        with st.container():
            st.markdown(f"""
            <div style="background-color: #f8f9fa; border-left: 5px solid #1f77b4; padding: 15px; margin-bottom: 12px; border-radius: 4px;">
                <h4 style="margin: 0 0 8px 0; color: #1f77b4;">PATTERN: {c['PATTERN']}</h4>
                <p style="margin: 0 0 6px 0;"><strong>EVIDENCE:</strong> {c['EVIDENCE']}</p>
                <p style="margin: 0 0 6px 0;"><strong>BUSINESS MEANING:</strong> {c['BUSINESS MEANING']}</p>
                <p style="margin: 0; color: #2e7d32;"><strong>RECOMMENDATION:</strong> {c['RECOMMENDATION']}</p>
            </div>
            """, unsafe_allow_html=True)

def show_overview(data):
    st.header("Executive Overview")
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Total Policies", f"{calculate_total_policies(data['policies']):,}")
    c2.metric("Active Policies", f"{calculate_active_policies(data['policies']):,}")
    c3.metric("Gross Premium", f"₹{calculate_total_premium(data['policies'])/1e6:.1f}M")
    c4.metric("Avg Premium", f"₹{calculate_average_premium(data['policies']):,.0f}")

    c5, c6, c7, c8 = st.columns(4)
    c5.metric("Total Claims", f"{calculate_total_claims(data['claims']):,}")
    c6.metric("Gross Claim Cost", f"₹{calculate_total_claim_amount(data['claims'])/1e6:.1f}M")
    c7.metric("Approval Rate", f"{calculate_claim_approval_rate(data['claims'])}%")
    c8.metric("Avg Settlement Time", f"{calculate_average_claim_settlement_days(data['claims'])} Days")

    st.markdown("---")
    col_a, col_b = st.columns(2)
    with col_a:
        st.pyplot(plot_policy_status(data['policies']))
    with col_b:
        st.pyplot(plot_claim_status(data['claims']))

def show_policy_analysis(data):
    st.header("Policy Portfolio & Inflow Analytics")
    col1, col2 = st.columns(2)
    with col1:
        st.pyplot(plot_policy_type_distribution(data['policies']))
    with col2:
        st.pyplot(plot_premium_by_policy_type(data['policies']))
    st.pyplot(plot_monthly_premium_trend(data['policies']))

def show_claim_analysis(data):
    st.header("Claim Volume, Severity & Settlement Performance")
    c1, c2 = st.columns(2)
    with c1:
        st.pyplot(plot_claim_type_distribution(data['claims']))
    with c2:
        st.pyplot(plot_damage_severity_distribution(data['claims']))
    
    c3, c4 = st.columns(2)
    with c3:
        st.pyplot(plot_claim_amount_distribution(data['claims']))
    with c4:
        st.pyplot(plot_average_settlement_time(data['claims']))
    st.pyplot(plot_monthly_claims(data['claims']))

def show_customer_analysis(data):
    st.header("Customer Demographics & Risk Profiling")
    col1, col2 = st.columns(2)
    with col1:
        st.pyplot(plot_claims_by_region(data))
    with col2:
        st.pyplot(plot_claim_severity_by_region(data))
    st.pyplot(plot_customer_age_vs_claim_amount(data))

def show_vehicle_analysis(data):
    st.header("Vehicle Class, Asset Value & Frequency Dynamics")
    col1, col2 = st.columns(2)
    with col1:
        st.pyplot(plot_claim_amount_by_vehicle_type(data))
    with col2:
        st.pyplot(plot_vehicle_type_claim_performance(data))
    st.pyplot(plot_vehicle_age_vs_claim_amount(data))

def show_premium_analysis(data):
    st.header("Premium Ratios, Coverage & Underwriting Exposure")
    col1, col2 = st.columns(2)
    with col1:
        st.metric("Claim-to-Premium Ratio", f"{calculate_claim_to_premium_ratio(data['claims'], data['policies']):.2f}")
        st.metric("Claim-to-Coverage Ratio", f"{calculate_claim_to_coverage_ratio(data['claims'], data['policies']):.4f}")
        st.pyplot(plot_claim_to_premium_by_policy_type(data))
    with col2:
        st.metric("Paid Claim Settlement Ratio", f"{calculate_paid_claim_ratio(data['payments'], data['claims']):.2f}")
        st.metric("Average Coverage per Policy", f"₹{calculate_average_coverage(data['policies']):,.0f}")
        st.pyplot(plot_payment_status(data['payments']))

def show_insights(data):
    st.header("Evidence-Based Business Insights & Strategic Recommendations")
    
    st.subheader("1. Portfolio & Retention Operations")
    render_insight_cards(generate_portfolio_insights(data))
    
    st.subheader("2. Claim Frequency & Friction")
    render_insight_cards(generate_claim_insights(data))
    
    st.subheader("3. Premium Concentration")
    render_insight_cards(generate_premium_insights(data))
    
    st.subheader("4. Customer Segment Exposure")
    render_insight_cards(generate_customer_insights(data))
    
    st.subheader("5. Vehicle Risk Patterns")
    render_insight_cards(generate_vehicle_insights(data))

    st.subheader("6. Aggregated Risk Patterns & Underwriting Loss Ratio")
    render_insight_cards(generate_risk_patterns(data))

    st.subheader("7. Executive Action Plan & Operational Recommendations")
    render_insight_cards(generate_business_recommendations(data))

def main():
    raw_data = load_dashboard_data()
    filtered_data = show_sidebar_filters(raw_data)

    pages = {
        "Executive Overview": show_overview,
        "Policy Analysis": show_policy_analysis,
        "Claims Analysis": show_claim_analysis,
        "Customer Analysis": show_customer_analysis,
        "Vehicle Analysis": show_vehicle_analysis,
        "Premium & Risk": show_premium_analysis,
        "Insights & Recommendations": show_insights
    }

    selected_page = st.sidebar.radio("Navigation Menu", list(pages.keys()))
    pages[selected_page](filtered_data)

if __name__ == "__main__":
    main()