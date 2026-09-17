-- ============================================================
-- Procurement Risk × Cost Exposure Matrix
-- Standard: ICMS 3rd Edition Cost Classification
-- Author: Kiran Kumar Srinivasan
-- ============================================================

SELECT
    pkg.package_id,
    pkg.package_name,
    pkg.vendor_name,
    pkg.vendor_country,
    pkg.system_group,
    pkg.lead_time_weeks,
    pkg.unit_cost_eur,
    pkg.quantity,
    pkg.unit_cost_eur * pkg.quantity                         AS total_exposure_eur,
    pkg.risk_score,

    -- Cost per week of delay
    ROUND(
        (pkg.unit_cost_eur * pkg.quantity) /
        NULLIF(pkg.lead_time_weeks, 0), 0
    )                                                        AS cost_per_week_delay_eur,

    -- Dead capital exposure (monthly carrying cost)
    ROUND(pkg.dead_capital_monthly_eur *
        GREATEST(0, pkg.lead_time_weeks - pkg.site_ready_weeks) / 4.33, 0
    )                                                        AS stranded_capital_eur,

    -- Procurement priority ranking
    RANK() OVER (
        ORDER BY pkg.risk_score DESC,
        (pkg.unit_cost_eur * pkg.quantity) DESC
    )                                                        AS procurement_priority,

    -- Risk quadrant classification
    CASE
        WHEN pkg.risk_score >= 9 AND (pkg.unit_cost_eur * pkg.quantity) > 10000000
            THEN 'CRITICAL — Immediate Action'
        WHEN pkg.risk_score >= 7 AND (pkg.unit_cost_eur * pkg.quantity) > 5000000
            THEN 'HIGH — Accelerate Procurement'
        WHEN pkg.risk_score >= 5
            THEN 'MEDIUM — Monitor Lead Times'
        ELSE 'LOW — Standard Procurement'
    END                                                      AS risk_quadrant

FROM dim_procurement_packages pkg
WHERE pkg.programme_id = 'PRG-2026-AMS'
ORDER BY procurement_priority;

