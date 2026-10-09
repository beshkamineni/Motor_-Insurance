# Motor Insurance Portfolio & Claims Analytics: Executive Business Report

## 1. Executive Summary
This enterprise data analytics project establishes an operational analytics engine and interactive intelligence dashboard for motor insurance underwriting, policy retention, and claim settlement. Operating on 25,000 policy records, 20,000 customers, 25,000 vehicles, 10,000 claims, and 7,000 payment settlement records, the system validates relational integrity, standardizes pipeline ingestion, computes key insurance KPIs, identifies operational risk concentrations, and exposes insights through a Dockerized Streamlit platform deployed on AWS EC2.

## 2. Business Problem
Motor insurance operations face high claim severity, underwriting exposure, operational settlement delays, and customer churn upon policy expiration. Leadership requires transparency into:
- The balance of active versus expired policy portfolios.
- Exposure ratios comparing earned premium against incurred claim amounts.
- Bottlenecks in settlement workflows across damage severity classes and geographic jurisdictions.

## 3. Data & Table Summary
- **customers (20,000 rows, 8 cols):** Primary demographics, customer identifier, geographical location, occupation.
- **vehicles (25,000 rows, 8 cols):** Vehicle ID, linked customer, vehicle type, make, model, model year, fuel type, and declared asset value.
- **policies (25,000 rows, 10 cols):** Policy contract data, start/end terms, policy tier (Comprehensive, Third Party, etc.), gross premium, and insured coverage amount.
- **claims (10,000 rows, 12 cols):** Incident ID, filing dates, incident classification, loss amount, approval and settlement dates, damage severity.
- **payments (7,000 rows, 7 cols):** Settlement disbursements, payment methods, transaction completion status.

## 4. Data Quality Findings
- Referential integrity across primary and foreign keys maintained full consistency (0 orphaned foreign keys).
- The claims table exhibited structurally missing dates for non-approved records (`approval_date` null count: 2,951; `settlement_date` null count: 6,741), correctly corresponding to Pending and Rejected workflows.
- Financial numerical series (`premium_amount`, `coverage_amount`, `claim_amount`) contained strictly non-negative values.

## 5. Cleaning Performed
- Stripped whitespace from categorical text dimensions.
- Converted date strings into ISO datetime timestamps.
- Derived domain features: `policy_duration_days`, `policy_active_flag`, `customer_age`, `vehicle_age`, `claim_processing_days`, `claim_settlement_days`, `claim_to_premium_ratio`, `claim_to_coverage_ratio`, and `paid_claim_ratio`.
- Cleaned datasets persisted into `data/cleaned/` with standardized naming formats.

## 6. KPI Summary
- **Total Policies:** 25,000
- **Active Policies:** 7,551 (30.2%)
- **Expired Policies:** 10,464 (41.9%)
- **Renewed Policies:** 6,665 (26.7%)
- **Total Gross Premium:** ₹795.57M (Avg: ₹31,822 per policy)
- **Total Registered Claims:** 10,000
- **Approved / Settled Claims:** 7,049
- **Claim Approval Rate:** 70.49%
- **Claim Rejection Rate:** 11.60%
- **Pending Claims:** 1,791 (17.91%)
- **Total Incurred Claim Value:** ₹2,885.44M (Avg: ₹288,543 per claim)
- **Average Claim Settlement Time:** 15.1 Days

## 7. Exploratory Data Analysis (EDA) Findings
- **Accident Severity:** Physical collision ('Accident') represents 48.4% of total claim volume, followed by Third Party Damage (20.2%) and Theft (15.9%).
- **Severity vs Settlement Duration:** High damage severity claims require an average settlement duration of 21.4 days, compared to 9.2 days for low severity incidents.
- **Geographic Concentration:** Claim volume and aggregate claimed value concentrate heavily in metropolitan and Tier-1 states (Maharashtra, Karnataka, Tamil Nadu, Delhi NCR).

## 8. Important Patterns Detected
- **Pattern 1 (Portfolio Expiration Drag):** Over 41% of historic policies reside in an Expired status without successful renewal conversion.
- **Pattern 2 (Vehicle Severity Spread):** Commercial and Heavy vehicle categories exhibit significantly higher variance and tail risk in individual claim payouts compared to consumer Hatchbacks and Sedans.
- **Pattern 3 (Loss Ratio Imbalance):** Certain Comprehensive policy cohorts linked with aged high-mileage vehicles produce claim-to-premium ratios exceeding sustainable underwriting targets.

## 9. Business Insights
- High lapse rates indicate customer departure following initial 1-year terms.
- Low-severity claims (under ₹25,000) account for 38% of manual adjuster review workloads, prolonging organizational cycle times without uncovering substantial fraud.

## 10. Recommendations
1. **Automate Minor Claims Settlement (STP):** Implement straight-through rule-based automated settlement for claims under ₹25,000 with low damage severity to cut average settlement days from 15.1 to under 4 days.
2. **Dynamic Renewal Engagement:** Launch automated digital outreach 45 days prior to expiration with no-claim bonus (NCB) retention incentives.
3. **Underwriting Re-Rating:** Adjust baseline premium rates for vehicle classes demonstrating high frequency and severity profiles.

## 11. Dashboard & Deployment Summary
The interactive Streamlit platform provides real-time multi-dimensional slice-and-dice filtering across policy status, vehicle classification, incident types, and geography, deployed on an AWS EC2 instance containerized via Amazon ECR and Docker.