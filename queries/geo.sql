-- Geographic Concentration
-- Single section. One row per active US state.

-- ##states
-- TODO: state-level exposure snapshot.
-- Columns: fips STRING (two-digit, with leading zero e.g. '06'),
--          state STRING (full name),
--          abbr STRING (USPS, e.g. 'OH'),
--          exposure FLOAT64 ($M),
--          obligors INT64 (distinct count),
--          risk FLOAT64 (exposure-weighted internal rating),
--          change FLOAT64 (QoQ % change in exposure),
--          region STRING (census region: Northeast|Midwest|Southeast|West).
SELECT
  LPAD(fips, 2, '0')  AS fips,
  state, abbr,
  exposure_m          AS exposure,
  obligor_count       AS obligors,
  wtd_avg_risk        AS risk,
  qoq_pct_change      AS change,
  census_region       AS region
FROM `your-project.your_dataset.state_snapshot`
WHERE as_of_quarter = '${as_of}';
