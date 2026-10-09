# Motor Insurance Portfolio & Claims Analytics Platform

An enterprise-grade, standardized data analytics, business intelligence, and cloud-deployed reporting system for motor insurance policy portfolios and claim settlement operations.

## 1. Business Scenario & Objectives
Motor insurance carriers balance policy acquisition, premium inflow, claim settlement turnaround, and underwriting loss ratios. This project standardizes the end-to-end data lifecycle:
1. Ingesting raw relational data (`customers`, `vehicles`, `policies`, `claims`, `payments`).
2. Validating referential schemas, constraints, and business rules.
3. Cleaning and engineering derived risk/operational metrics.
4. Computing standardized insurance KPIs and statistical distributions.
5. Providing an interactive 7-page Streamlit analytical dashboard.
6. Containerizing via Docker and deploying on AWS EC2 using Amazon ECR.

## 2. Technology Stack
- **Core Analytics & Transformation:** Python 3.10+, Pandas, NumPy
- **Visualizations:** Matplotlib, Seaborn
- **Interactive Frontend:** Streamlit
- **Testing & Logging:** Pytest, Python standard `logging`
- **DevOps & Cloud:** Git, Docker, Amazon ECR, AWS IAM, AWS EC2

## 3. Data Model Relationships
```text
customers (1) ───< (N) vehicles (1) ───< (N) policies (1) ───< (N) claims (1) ───< (N) payments