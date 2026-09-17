-- ============================================================
-- EVM Core Metrics — Multi-Facility Portfolio View
-- Standard: ANSI/EIA-748-D Earned Value Management
-- Author: Kiran Kumar Srinivasan
-- ============================================================
-- This query calculates Earned Value Management metrics
-- across multiple infrastructure programmes, enabling
-- portfolio-level performance visibility.
--
-- Applicable to: Data Centers, Energy/BESS, Pharma CapEx,
-- Logistics Infrastructure, Financial Services Operations
-- ============================================================

SELECT
    p.programme_id,
    p.programme_name,
    p.facility_type,
    r.reporting_period,
    r.reporting_date,

    -- Core EVM Metrics
    SUM(r.bcws)                                             AS planned_value_pv,
    SUM(r.bcwp)                                             AS earned_value_ev,
    SUM(r.acwp)                                             AS actual_cost_ac,
    SUM(p.bac)                                              AS budget_at_completion,

    -- Performance Indices
    ROUND(SUM(r.bcwp) / NULLIF(SUM(r.acwp), 0), 3)         AS cost_performance_index,
    ROUND(SUM(r.bcwp) / NULLIF(SUM(r.bcws), 0), 3)         AS schedule_performance_index,

    -- Variance Analysis
    SUM(r.bcwp) - SUM(r.acwp)                               AS cost_variance_eur,
    SUM(r.bcwp) - SUM(r.bcws)                               AS schedule_variance_eur,

    -- Forecasting
    ROUND(SUM(p.bac) / NULLIF(
        SUM(r.bcwp) / NULLIF(SUM(r.acwp), 0), 0
    ), 0)                                                    AS estimate_at_completion,

    SUM(p.bac) - SUM(r.acwp)                                AS estimate_to_complete,

    -- To-Complete Performance Index
    ROUND(
        (SUM(p.bac) - SUM(r.bcwp)) /
        NULLIF(SUM(p.bac) - SUM(r.acwp), 0), 3
    )                                                        AS tcpi_bac,

    -- Percent Complete
    ROUND(SUM(r.bcwp) / NULLIF(SUM(p.bac), 0) * 100, 1)    AS pct_complete,

    -- Duration Metrics
    r.duration_consumed_pct,
    ROUND(SUM(r.bcwp) / NULLIF(SUM(p.bac), 0) * 100, 1)
        - r.duration_consumed_pct                            AS schedule_efficiency_gap

FROM fact_evm_monthly r
JOIN dim_programmes p
    ON r.programme_id = p.programme_id
WHERE r.reporting_date = (SELECT MAX(reporting_date) FROM fact_evm_monthly)
GROUP BY
    p.programme_id, p.programme_name, p.facility_type,
    r.reporting_period, r.reporting_date, r.duration_consumed_pct
ORDER BY
    cost_performance_index ASC;

