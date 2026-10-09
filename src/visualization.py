from typing import Dict, Optional
import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns
import streamlit as st

sns.set_theme(style="whitegrid", palette="deep")


def plot_policy_status(policies_df: pd.DataFrame) -> plt.Figure:
    fig, ax = plt.subplots(figsize=(8, 4.5))
    order = policies_df['policy_status'].value_counts().index
    sns.countplot(
        data=policies_df,
        x='policy_status',
        hue='policy_status',
        legend=False,
        order=order,
        ax=ax,
        palette='crest'
    )
    ax.set_title("Portfolio Breakdown by Policy Status", fontsize=14, pad=12)
    ax.set_xlabel("Policy Status")
    ax.set_ylabel("Volume")
    for p in ax.patches:
        ax.annotate(
            f"{int(p.get_height()):,}",
            (p.get_x() + p.get_width() / 2.0, p.get_height()),
            ha='center',
            va='bottom',
            fontsize=9,
            xytext=(0, 3),
            textcoords='offset points'
        )
    plt.tight_layout()
    return fig


def plot_policy_type_distribution(policies_df: pd.DataFrame) -> plt.Figure:
    fig, ax = plt.subplots(figsize=(8, 4.5))
    counts = policies_df['policy_type'].value_counts()
    ax.pie(
        counts,
        labels=counts.index,
        autopct='%1.1f%%',
        startangle=140,
        colors=sns.color_palette("Set2")
    )
    ax.set_title("Distribution of Policy Types", fontsize=14, pad=12)
    plt.tight_layout()
    return fig


def plot_premium_by_policy_type(policies_df: pd.DataFrame) -> plt.Figure:
    fig, ax = plt.subplots(figsize=(8, 4.5))
    agg = policies_df.groupby('policy_type')['premium_amount'].sum() / 1e6
    agg = agg.sort_values(ascending=False)
    sns.barplot(
        x=agg.index,
        y=agg.values,
        hue=agg.index,
        legend=False,
        ax=ax,
        palette='viridis'
    )
    ax.set_title("Gross Written Premium by Policy Type (M INR)", fontsize=14, pad=12)
    ax.set_xlabel("Policy Type")
    ax.set_ylabel("Premium (Million INR)")
    for p in ax.patches:
        ax.annotate(
            f"₹{p.get_height():.1f}M",
            (p.get_x() + p.get_width() / 2.0, p.get_height()),
            ha='center',
            va='bottom',
            fontsize=9,
            xytext=(0, 3),
            textcoords='offset points'
        )
    plt.tight_layout()
    return fig


def plot_monthly_claims(claims_df: pd.DataFrame) -> plt.Figure:
    fig, ax = plt.subplots(figsize=(10, 4.5))
    claims_temp = claims_df.copy()
    claims_temp['claim_period'] = claims_temp['claim_date'].dt.to_period('M')
    ts = claims_temp.groupby('claim_period').size()
    ts.index = ts.index.astype(str)
    sns.lineplot(x=ts.index, y=ts.values, marker='o', ax=ax, color='#1f77b4', linewidth=2)
    ax.set_title("Monthly Claim Registration Trend", fontsize=14, pad=12)
    ax.set_xlabel("Year-Month")
    ax.set_ylabel("Claim Count")
    plt.xticks(rotation=45)
    plt.tight_layout()
    return fig


def plot_claim_status(claims_df: pd.DataFrame) -> plt.Figure:
    fig, ax = plt.subplots(figsize=(8, 4.5))
    sns.countplot(
        data=claims_df,
        x='claim_status',
        hue='claim_status',
        legend=False,
        ax=ax,
        palette='Spectral'
    )
    ax.set_title("Claims Workflow Status", fontsize=14, pad=12)
    ax.set_xlabel("Claim Status")
    ax.set_ylabel("Count")
    plt.tight_layout()
    return fig


def plot_claim_type_distribution(claims_df: pd.DataFrame) -> plt.Figure:
    fig, ax = plt.subplots(figsize=(8, 4.5))
    order = claims_df['claim_type'].value_counts().index
    sns.countplot(
        data=claims_df,
        y='claim_type',
        hue='claim_type',
        legend=False,
        ax=ax,
        order=order,
        palette='viridis'
    )
    ax.set_title("Distribution of Incident/Claim Types", fontsize=14, pad=12)
    ax.set_xlabel("Number of Incidents")
    ax.set_ylabel("Claim Type")
    plt.tight_layout()
    return fig


def plot_claim_amount_distribution(claims_df: pd.DataFrame) -> plt.Figure:
    fig, ax = plt.subplots(figsize=(8, 4.5))
    sns.histplot(claims_df['claim_amount'] / 1e3, kde=True, ax=ax, color='crimson', bins=30)
    ax.set_title("Claim Amount Distribution (Thousands INR)", fontsize=14, pad=12)
    ax.set_xlabel("Claim Value (K INR)")
    ax.set_ylabel("Frequency")
    plt.tight_layout()
    return fig


def plot_claim_amount_by_vehicle_type(data: Dict[str, pd.DataFrame]) -> plt.Figure:
    fig, ax = plt.subplots(figsize=(8, 4.5))
    m = data['claims'].merge(data['policies'], on='policy_id', how='left')
    m = m.merge(data['vehicles'], on='vehicle_id', how='left')
    agg = m.groupby('vehicle_type')['claim_amount'].mean().sort_values(ascending=False)
    sns.barplot(
        x=agg.index,
        y=agg.values,
        hue=agg.index,
        legend=False,
        ax=ax,
        palette='flare'
    )
    ax.set_title("Average Severity by Vehicle Class", fontsize=14, pad=12)
    ax.set_xlabel("Vehicle Type")
    ax.set_ylabel("Average Claim (INR)")
    plt.tight_layout()
    return fig


def plot_claims_by_region(data: Dict[str, pd.DataFrame]) -> plt.Figure:
    fig, ax = plt.subplots(figsize=(10, 4.5))
    m = data['claims'].merge(data['customers'], on='customer_id', how='left')
    top_states = m['state'].value_counts().nlargest(10)
    sns.barplot(
        x=top_states.index,
        y=top_states.values,
        hue=top_states.index,
        legend=False,
        ax=ax,
        palette='rocket'
    )
    ax.set_title("Top 10 States by Claim Volume", fontsize=14, pad=12)
    ax.set_xlabel("State")
    ax.set_ylabel("Claim Count")
    plt.xticks(rotation=45)
    plt.tight_layout()
    return fig


def plot_claim_severity_by_region(data: Dict[str, pd.DataFrame]) -> plt.Figure:
    fig, ax = plt.subplots(figsize=(10, 4.5))
    m = data['claims'].merge(data['customers'], on='customer_id', how='left')
    top_sev = m.groupby('state')['claim_amount'].mean().nlargest(10)
    sns.barplot(
        x=top_sev.index,
        y=top_sev.values,
        hue=top_sev.index,
        legend=False,
        ax=ax,
        palette='crest'
    )
    ax.set_title("Top 10 States by Average Claim Severity", fontsize=14, pad=12)
    ax.set_xlabel("State")
    ax.set_ylabel("Average Claim Amount (INR)")
    plt.xticks(rotation=45)
    plt.tight_layout()
    return fig


def plot_average_settlement_time(claims_df: pd.DataFrame) -> plt.Figure:
    fig, ax = plt.subplots(figsize=(8, 4.5))
    valid = claims_df.dropna(subset=['claim_settlement_days'])
    agg = valid.groupby('claim_type')['claim_settlement_days'].mean().sort_values(ascending=False)
    sns.barplot(
        x=agg.index,
        y=agg.values,
        hue=agg.index,
        legend=False,
        ax=ax,
        palette='cubehelix'
    )
    ax.set_title("Average Settlement Duration (Days) by Claim Type", fontsize=14, pad=12)
    ax.set_xlabel("Claim Type")
    ax.set_ylabel("Settlement Days")
    plt.xticks(rotation=30)
    plt.tight_layout()
    return fig


def plot_claim_to_premium_by_policy_type(data: Dict[str, pd.DataFrame]) -> plt.Figure:
    fig, ax = plt.subplots(figsize=(8, 4.5))
    m = data['claims'].merge(data['policies'], on='policy_id', how='left')
    agg = m.groupby('policy_type')['claim_to_premium_ratio'].mean().sort_values(ascending=False)
    sns.barplot(
        x=agg.index,
        y=agg.values,
        hue=agg.index,
        legend=False,
        ax=ax,
        palette='magma'
    )
    ax.set_title("Claim-to-Premium Ratio by Policy Type", fontsize=14, pad=12)
    ax.set_xlabel("Policy Type")
    ax.set_ylabel("Claim / Premium Ratio")
    plt.tight_layout()
    return fig


def plot_vehicle_age_vs_claim_amount(data: Dict[str, pd.DataFrame]) -> plt.Figure:
    fig, ax = plt.subplots(figsize=(8, 4.5))
    m = data['claims'].merge(data['policies'], on='policy_id', how='left')
    m = m.merge(data['vehicles'], on='vehicle_id', how='left')
    sns.scatterplot(
        data=m.sample(min(1500, len(m))),
        x='vehicle_age',
        y='claim_amount',
        alpha=0.5,
        ax=ax,
        color='teal'
    )
    ax.set_title("Vehicle Age vs Claim Amount", fontsize=14, pad=12)
    ax.set_xlabel("Vehicle Age (Years)")
    ax.set_ylabel("Claim Amount (INR)")
    plt.tight_layout()
    return fig


def plot_customer_age_vs_claim_amount(data: Dict[str, pd.DataFrame]) -> plt.Figure:
    fig, ax = plt.subplots(figsize=(8, 4.5))
    m = data['claims'].merge(data['customers'], on='customer_id', how='left')
    sns.scatterplot(
        data=m.sample(min(1500, len(m))),
        x='customer_age',
        y='claim_amount',
        alpha=0.5,
        ax=ax,
        color='navy'
    )
    ax.set_title("Customer Age vs Claim Amount", fontsize=14, pad=12)
    ax.set_xlabel("Customer Age")
    ax.set_ylabel("Claim Amount (INR)")
    plt.tight_layout()
    return fig


def plot_vehicle_type_claim_performance(data: Dict[str, pd.DataFrame]) -> plt.Figure:
    fig, ax = plt.subplots(figsize=(9, 4.5))
    m = data['claims'].merge(data['policies'], on='policy_id', how='left')
    m = m.merge(data['vehicles'], on='vehicle_id', how='left')
    sns.boxplot(
        data=m,
        x='vehicle_type',
        y='claim_amount',
        hue='vehicle_type',
        legend=False,
        ax=ax,
        palette='coolwarm'
    )
    ax.set_title("Claim Value Spread Across Vehicle Classes", fontsize=14, pad=12)
    ax.set_xlabel("Vehicle Type")
    ax.set_ylabel("Claim Amount (INR)")
    plt.tight_layout()
    return fig


def plot_damage_severity_distribution(claims_df: pd.DataFrame) -> plt.Figure:
    fig, ax = plt.subplots(figsize=(8, 4.5))
    sns.countplot(
        data=claims_df,
        x='damage_severity',
        hue='damage_severity',
        legend=False,
        order=['Low', 'Medium', 'High'],
        ax=ax,
        palette='YlOrRd'
    )
    ax.set_title("Damage Severity Incident Count", fontsize=14, pad=12)
    ax.set_xlabel("Damage Severity")
    ax.set_ylabel("Count")
    plt.tight_layout()
    return fig


def plot_payment_status(payments_df: pd.DataFrame) -> plt.Figure:
    fig, ax = plt.subplots(figsize=(8, 4.5))
    sns.countplot(
        data=payments_df,
        x='payment_method',
        hue='payment_method',
        legend=False,
        ax=ax,
        palette='Pastel1'
    )
    ax.set_title("Settlement Method Utilization", fontsize=14, pad=12)
    ax.set_xlabel("Payment Method")
    ax.set_ylabel("Transaction Count")
    plt.tight_layout()
    return fig


def plot_monthly_premium_trend(policies_df: pd.DataFrame) -> plt.Figure:
    fig, ax = plt.subplots(figsize=(10, 4.5))
    candidate_cols = ['policy_start_date', 'policy_date', 'start_date', 'issue_date']
    date_col = next((col for col in candidate_cols if col in policies_df.columns), None)
    
    if date_col is None:
        raise ValueError(
            f"None of {candidate_cols} found in policies DataFrame. "
            f"Available columns: {list(policies_df.columns)}"
        )
    
    policies_temp = policies_df.copy()
    policies_temp[date_col] = pd.to_datetime(policies_temp[date_col])
    policies_temp['period'] = policies_temp[date_col].dt.to_period('M')
    
    ts = policies_temp.groupby('period')['premium_amount'].sum() / 1e6
    ts.index = ts.index.astype(str)
    
    sns.lineplot(x=ts.index, y=ts.values, marker='o', ax=ax, color='#2ca02c', linewidth=2)
    ax.set_title("Monthly Gross Written Premium Trend (M INR)", fontsize=14, pad=12)
    ax.set_xlabel("Year-Month")
    ax.set_ylabel("Total Premium (Million INR)")
    plt.xticks(rotation=45)
    plt.tight_layout()
    return fig