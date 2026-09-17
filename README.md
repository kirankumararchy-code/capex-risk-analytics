# CapEx Risk Analytics

**Predictive risk modeling for high-scale infrastructure capital programmes**

Monte Carlo simulation, Earned Value Management, and Diversity Factor
optimization engines applied to a €127M combined infrastructure portfolio.

## Portfolio Overview

| Model | Scope | Value | Tools |
|-------|-------|-------|-------|
| CapEx Procurement Intelligence | 20MW Liquid-Cooled Data Center, Amsterdam | €80.43M | Power BI, DAX, Star Schema |
| Grid Interconnection EVM | 80MW Hyperscale Campus, Central Europe | €47M | Power BI, EVM (ANSI/EIA-748) |
| Monte Carlo SRA | Schedule Risk Analysis, 10,000 iterations | €127M combined | Python, NumPy, SciPy |
| Diversity Factor Engine | Capacity optimization across 3 facility types | 100MW scenarios | Power BI, Scenario Modeling |

## Repository Structure
sql/ 
├── 01_evm_metrics.sql — CPI, SPI, EAC, TCPI calculations 
├── 02_procurement_risk_ranking.sql — Lead-time × cost exposure matrix 
└── 03_diversity_factor.sql — Stranded capital cascade

python/ 
└── monte_carlo_engine.py — 10,000 iteration PERT simulation

dashboards/ — Power BI dashboard screenshots
* ![Diversity Factor Engine Summary](P01%20DF.png)
* ![EVM Metrics Dashboard](RQ1.jpg)
* ![Monte Carlo SRA Dashboard](Monet%20RQ1.jpg)
* ![Procurement Intelligence Dashboard](executive%20summary%20Piv.jpg)

docs/ — Methodology documentation

## Standards & Methodology

- **AACE RP 57R-09** — Schedule Risk Analysis (Monte Carlo)
- **ANSI/EIA-748-D** — Earned Value Management
- **ICMS 3rd Edition** — International Construction Measurement Standard
- **NEC 210.20 / IEC 60364** — Continuous load derating (80%)
- **Uptime Institute / ASHRAE TC 9.9** — Diversity factor benchmarks

## Cross-Industry Application

This analytical framework applies to any industry managing
high-scale capital programmes:

- ⚡ Energy & Grid Infrastructure
- 🏭 Pharmaceutical & Manufacturing CapEx
- 🚛 Logistics Hub Development
- 🏦 Financial Services Operational Risk
- 🏗️ Industrial Construction & Engineering

## Author

**Kiran Kumar Srinivasan**
CapEx & Operations Data Analyst | SQL + Python + Power BI
Prague, Czech Republic

[![LinkedIn](https://img.shields.io/badge/LinkedIn-Connect-blue)](https://www.linkedin.com/in/kiran-kumar-srinivasan-704674234/ )

