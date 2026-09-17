-- ============================================================
-- Diversity Factor → Stranded Capital Cascade
-- Standards: NEC 210.20 / IEC 60364 (80% derating)
--            Uptime Institute / ASHRAE TC 9.9 (diversity)
-- Author: Kiran Kumar Srinivasan
-- ============================================================

WITH capacity_cascade AS (
    SELECT
        f.facility_id,
        f.facility_type,
        f.region,
        f.nameplate_mw,
        f.cost_per_mw_eur,
        s.diversity_factor,
        s.phase_imbalance_pct,

        -- NEC/IEC 80% continuous load derating
        f.nameplate_mw * 0.80                                AS derated_mw,

        -- Real demand after diversity factor
        ROUND(f.nameplate_mw * 0.80 * s.diversity_factor
            * (1 - s.phase_imbalance_pct / 100.0), 2)        AS real_demand_mw,

        -- Stranded capacity
        ROUND(f.nameplate_mw - (f.nameplate_mw * 0.80
            * s.diversity_factor
            * (1 - s.phase_imbalance_pct / 100.0)), 2)       AS stranded_mw

    FROM dim_facilities f
    CROSS JOIN dim_scenarios s
    WHERE s.diversity_factor BETWEEN 0.50 AND 1.00
      AND s.phase_imbalance_pct BETWEEN 0 AND 30
)

SELECT
    facility_type,
    nameplate_mw,
    diversity_factor,
    phase_imbalance_pct,
    derated_mw,
    real_demand_mw,
    stranded_mw,

    -- Stranded percentage
    ROUND(stranded_mw / nameplate_mw * 100, 1)              AS stranded_pct,

    -- Financial impact
    ROUND(stranded_mw * cost_per_mw_eur, 0)                 AS stranded_capital_eur,

    -- UPS savings potential
    ROUND(stranded_mw * cost_per_mw_eur * 0.48, 0)          AS ups_savings_eur,

    -- Workload classification
    CASE
        WHEN diversity_factor BETWEEN 0.50 AND 0.55 THEN 'Extreme Overspec'
        WHEN diversity_factor BETWEEN 0.56 AND 0.65 THEN 'Heavy AI/GPU'
        WHEN diversity_factor BETWEEN 0.66 AND 0.75 THEN 'Mixed AI/Cloud'
        WHEN diversity_factor BETWEEN 0.76 AND 0.85 THEN 'Traditional Cloud'
        WHEN diversity_factor BETWEEN 0.86 AND 1.00 THEN 'Near Nameplate'
    END                                                      AS workload_category

FROM capacity_cascade
ORDER BY stranded_capital_eur DESC;

