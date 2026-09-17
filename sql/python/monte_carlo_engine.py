"""
Monte Carlo Schedule Risk Analysis Engine
==========================================
10,000-iteration Beta-PERT simulation for infrastructure
capital programme schedule risk quantification.

Standard: AACE International Recommended Practice 57R-09
Distribution: Beta-PERT (Modified Beta) with λ=4
Applicable: Data Centers, Energy/BESS, Pharma, Logistics

Author: Kiran Kumar Srinivasan
"""

import numpy as np
import pandas as pd
from scipy import stats
from dataclasses import dataclass
from typing import List, Dict, Tuple


@dataclass
class WorkPackage:
    """Represents a single WBS activity with three-point estimate."""
    wbs_id: str
    name: str
    vendor: str
    min_weeks: float
    likely_weeks: float
    max_weeks: float
    cost_eur: float
    risk_score: int
    chain: str
    chain_order: int
    predecessor: str = None


def pert_sample(
    min_val: float,
    likely_val: float,
    max_val: float,
    n: int = 10000,
    lam: float = 4
) -> np.ndarray:
    """
    Generate n samples from a Beta-PERT distribution.

    The PERT distribution is the industry standard for schedule
    risk analysis (AACE RP 57R-09, Safran Risk, Oracle PRA).

    Parameters
    ----------
    min_val : Optimistic duration (best case)
    likely_val : Most likely duration (mode)
    max_val : Pessimistic duration (worst case)
    n : Number of Monte Carlo iterations
    lam : PERT shape parameter (standard = 4)

    Returns
    -------
    np.ndarray of n sampled durations
    """
    mean = (min_val + lam * likely_val + max_val) / (lam + 2)

    if max_val == min_val:
        return np.full(n, min_val)

    alpha = ((mean - min_val) * (2 * likely_val - min_val - max_val)) / \
            ((likely_val - mean) * (max_val - min_val))

    if alpha <= 0:
        alpha = 1.0 + (lam / 2) * ((mean - min_val) / (max_val - min_val))

    beta = alpha * (max_val - mean) / (mean - min_val)

    if beta <= 0:
        beta = 1.0

    samples = np.random.beta(alpha, beta, n)
    return min_val + samples * (max_val - min_val)


def run_simulation(
    packages: List[WorkPackage],
    n_iterations: int = 10000,
    dead_capital_monthly: float = 233000,
    seed: int = 2026
) -> pd.DataFrame:
    """
    Execute Monte Carlo schedule risk simulation.

    Simulates n_iterations of the project schedule using
    Beta-PERT distributions for each work package, then
    calculates chain logic, critical path, and financial impact.
    """
    np.random.seed(seed)

    # Sample durations for each package
    durations = {}
    for pkg in packages:
        durations[pkg.wbs_id] = pert_sample(
            pkg.min_weeks, pkg.likely_weeks, pkg.max_weeks, n_iterations
        )

    # Chain logic (configurable per project)
    # Chain A: Switchgear → UPS (with Generator SS+4wk lag)
    chain_a = (durations['ACT-2140'] +
               np.maximum(durations['ACT-2110'],
                         durations['ACT-2130'] + 4))

    # Chain B: HV Cable → Transformer
    chain_b = durations['ACT-2150'] + durations['ACT-2120']

    # Project finish = max of all chains
    project_finish = np.maximum(chain_a, chain_b)

    # Deterministic baseline
    baseline = max(
        42 + max(60, 52 + 4),   # Chain A likely
        36 + 182                  # Chain B likely
    )

    # Financial impact
    dead_capital_weekly = dead_capital_monthly / 4.33
    schedule_variance = project_finish - baseline
    cost_overrun = np.maximum(0, schedule_variance) * dead_capital_weekly

    # Build results DataFrame
    results = pd.DataFrame({
        'Iteration': range(1, n_iterations + 1),
        'Chain_A_Finish': np.round(chain_a, 1),
        'Chain_B_Finish': np.round(chain_b, 1),
        'Project_Finish': np.round(project_finish, 1),
        'Critical_Path': np.where(
            chain_a >= chain_b, 'Chain A', 'Chain B'
        ),
        'Baseline': baseline,
        'Schedule_Variance': np.round(schedule_variance, 1),
        'Cost_Overrun_EUR': np.round(cost_overrun, 0)
    })

    return results


def calculate_percentiles(results: pd.DataFrame) -> Dict:
    """Extract P-values and financial metrics."""
    fw = results['Project_Finish'].values
    baseline = results['Baseline'].iloc
    dcw = 233000 / 4.33

    p_values = {}
    for p in [10, 20, 30, 40, 50, 60, 70, 80, 90, 95]:
        p_values[f'P{p}'] = round(np.percentile(fw, p), 1)

    p50, p80, p90 = p_values['P50'], p_values['P80'], p_values['P90']

    return {
        'percentiles': p_values,
        'baseline': baseline,
        'baseline_confidence': round((fw <= baseline).mean() * 100, 1),
        'funded_contingency_weeks': round(p80 - p50, 1),
        'funded_contingency_eur': round((p80 - p50) * dcw, 0),
        'mgmt_reserve_weeks': round(p90 - p80, 1),
        'mgmt_reserve_eur': round((p90 - p80) * dcw, 0),
        'total_risk_weeks': round(p90 - p50, 1),
        'total_risk_eur': round((p90 - p50) * dcw, 0),
        'mean': round(np.mean(fw), 1),
        'std_dev': round(np.std(fw), 1),
    }


def sensitivity_analysis(
    results: pd.DataFrame,
    packages: List[WorkPackage],
    durations: Dict[str, np.ndarray]
) -> pd.DataFrame:
    """Rank risk drivers by correlation to project finish."""
    fw = results['Project_Finish'].values

    sensitivities = []
    for pkg in packages:
        r = np.corrcoef(durations[pkg.wbs_id], fw)[0, 1]
        sensitivities.append({
            'WBS_ID': pkg.wbs_id,
            'Activity': pkg.name,
            'Correlation_R': round(r, 4),
            'R_Squared': round(r**2, 4),
            'Variance_Pct': round(r**2 * 100, 1),
            'Category': (
                'DOMINANT' if abs(r) > 0.7 else
                'SIGNIFICANT' if abs(r) > 0.4 else
                'MODERATE' if abs(r) > 0.2 else 'LOW'
            )
        })

    return pd.DataFrame(sensitivities).sort_values(
        'Correlation_R', ascending=False
    ).reset_index(drop=True)


# ============================================================
# EXECUTION
# ============================================================
if __name__ == '__main__':

    # Define work packages (from €127M portfolio)
    packages = [
        WorkPackage('ACT-2110', 'Rotary UPS System',
                    'Hitec Power Protection', 48, 60, 78,
                    17440000, 10, 'A', 2, 'ACT-2140'),
        WorkPackage('ACT-2120', '90MVA Power Transformer',
                    'Siemens Energy', 130, 182, 208,
                    4200000, 10, 'B', 2, 'ACT-2150'),
        WorkPackage('ACT-2130', 'Backup Diesel Generator',
                    'Caterpillar', 40, 52, 68,
                    10500000, 9, 'A', 3, 'ACT-2110'),
        WorkPackage('ACT-2140', 'MV Switchgear',
                    'Siemens', 30, 42, 56,
                    8220000, 8, 'A', 1),
        WorkPackage('ACT-2150', 'HV Cable Installation',
                    'EPC Subcontractor', 24, 36, 52,
                    4800000, 7, 'B', 1),
    ]

    # Run simulation
    results = run_simulation(packages)
    metrics = calculate_percentiles(results)

    # Output
    print(f"P6 Baseline:     {metrics['baseline']} weeks")
    print(f"Confidence:      {metrics['baseline_confidence']}%")
    print(f"P50:             {metrics['percentiles']['P50']} weeks")
    print(f"P80:             {metrics['percentiles']['P80']} weeks")
    print(f"P90:             {metrics['percentiles']['P90']} weeks")
    print(f"Contingency:     {metrics['funded_contingency_weeks']} wks"
          f" = €{metrics['funded_contingency_eur']:,.0f}")
    print(f"Mgmt Reserve:    {metrics['mgmt_reserve_weeks']} wks"
          f" = €{metrics['mgmt_reserve_eur']:,.0f}")

