from typing import Dict, List, Any
import pandas as pd

def format_card(pattern: str, evidence: str, meaning: str, recommendation: str) -> Dict[str, str]:
    return {
        "PATTERN": pattern,
        "EVIDENCE": evidence,
        "BUSINESS MEANING": meaning,
        "RECOMMENDATION": recommendation
    }

def generate_portfolio_insights(data: Dict[str, pd.DataFrame]) -> List[Dict[str, str]]:
    pol = data['policies']
    tot = len(pol)
    exp = (pol['policy_status'] == 'Expired').sum()
    act = (pol['policy_status'] == 'Active').sum()
    exp_pct = round((exp / tot) * 100, 1) if tot > 0 else 0
    return [
        format_card(
            pattern="High Rate of Expired and Non-Renewed Policies",
            evidence=f"Expired policies represent {exp_pct}% ({exp:,} of {tot:,}) of the entire policy registry, with active policies at {act:,}.",
            meaning="Significant customer attrition or friction during renewal threatens lifetime portfolio value and overall premium inflow.",
            recommendation="Deploy automated renewal notification reminders 45 days prior to lapse and offer targeted renewal discounts to high-retention cohorts."
        )
    ]

def generate_claim_insights(data: Dict[str, pd.DataFrame]) -> List[Dict[str, str]]:
    clm = data['claims']
    top_type = clm['claim_type'].value_counts().index[0]
    top_cnt = clm['claim_type'].value_counts().iloc[0]
    pct = round((top_cnt / len(clm)) * 100, 1) if len(clm) > 0 else 0
    return [
        format_card(
            pattern=f"High Incident Concentration in {top_type} Claims",
            evidence=f"{top_type} accounts for {pct}% ({top_cnt:,} incidents) of all registered claims.",
            meaning="Physical collisions and accidents dominate claims processing volume, driving underwriting costs and workshop claim friction.",
            recommendation="Implement telematics/driver monitoring incentives and partner with preferred repair networks to cap average physical damage costs."
        )
    ]

def generate_premium_insights(data: Dict[str, pd.DataFrame]) -> List[Dict[str, str]]:
    pol = data['policies']
    prem_by_type = pol.groupby('policy_type')['premium_amount'].sum()
    top_prem = prem_by_type.index[0]
    share = round((prem_by_type.iloc[0] / pol['premium_amount'].sum()) * 100, 1)
    return [
        format_card(
            pattern=f"Revenue Dominated by {top_prem} Tier",
            evidence=f"{top_prem} policies contribute {share}% of total gross written premium collections.",
            meaning="Top-line underwriting cash flow is concentrated within a single tier, leaving revenue vulnerable to market share shifts in this category.",
            recommendation="Diversify product offerings by expanding comprehensive riders and tailored add-ons across under-indexed policy classes."
        )
    ]

def generate_customer_insights(data: Dict[str, pd.DataFrame]) -> List[Dict[str, str]]:
    m = data['claims'].merge(data['customers'], on='customer_id', how='left')
    top_occ = m.groupby('occupation')['claim_amount'].sum().nlargest(1)
    occ_name = top_occ.index[0]
    occ_sum = top_occ.iloc[0] / 1e6
    return [
        format_card(
            pattern=f"Elevated Claim Accumulation in '{occ_name}' Occupation Cohort",
            evidence=f"Customers categorized as {occ_name} have accumulated ₹{occ_sum:.2f}M in registered claim costs.",
            meaning="Certain demographic/vocational segments present higher operational exposure due to driving frequency, mileage, or vehicle class.",
            recommendation="Incorporate occupational risk weighting and historical frequency multipliers during underwriting and quoting."
        )
    ]

def generate_vehicle_insights(data: Dict[str, pd.DataFrame]) -> List[Dict[str, str]]:
    m = data['claims'].merge(data['policies'], on='policy_id', how='left')
    m = m.merge(data['vehicles'], on='vehicle_id', how='left')
    v_top = m.groupby('vehicle_type')['claim_amount'].sum().nlargest(1)
    v_name = v_top.index[0]
    v_sum = v_top.iloc[0] / 1e6
    return [
        format_card(
            pattern=f"Disproportionate Severity Concentrated in {v_name} Category",
            evidence=f"{v_name} vehicles account for ₹{v_sum:.2f}M in total registered claim liability.",
            meaning="Higher repair costs, expensive OEM parts, or heavier road exposure inflate overall severity in this vehicle segment.",
            recommendation="Enforce higher deductibles for high-severity vehicle tiers and mandate approved authorized OEM service facilities."
        )
    ]

def generate_risk_patterns(data: Dict[str, pd.DataFrame]) -> List[Dict[str, str]]:
    clm = data['claims']
    pol = data['policies']
    tot_prem = pol['premium_amount'].sum()
    tot_claim = clm['claim_amount'].sum()
    loss_ratio = round((tot_claim / tot_prem) * 100, 1) if tot_prem > 0 else 0
    return [
        format_card(
            pattern="Elevated Cumulative Loss Ratio Exposure",
            evidence=f"Aggregated claimed losses represent {loss_ratio}% of total annual gross written premium across the active and historic book.",
            meaning="Unchecked claim volume and rising incident costs threaten portfolio profitability and operational underwriting margins.",
            recommendation="Re-rate baseline premiums upwards by 8-12% for high-risk cohorts, tighten pre-approval documentation, and audit major claims."
        )
    ]

def generate_business_recommendations(data: Dict[str, pd.DataFrame]) -> List[Dict[str, str]]:
    clm = data['claims']
    valid_settle = clm['claim_settlement_days'].dropna()
    avg_settle = round(valid_settle.mean(), 1) if len(valid_settle) > 0 else 0
    return [
        format_card(
            pattern="Settlement Workflow Optimization Opportunity",
            evidence=f"Claims take an average of {avg_settle} days from registration to final settlement completion.",
            meaning="Longer settlement cycles raise customer dissatisfaction, operational handling overhead, and administrative review costs.",
            recommendation="Deploy straight-through digital processing (STP) for low-severity claims (under ₹25,000) to cut turnaround time by 50%."
        )
    ]