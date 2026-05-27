-- Portfolio Flow Analysis
--
-- Four sections. Each section is run as a separate BigQuery query and
-- its result is reshaped by lib/payloads.py::portfolio_flow_payload.
-- The column names below are the contract — do not rename.
--
-- Until every section has real SQL (i.e. you've deleted every `-- TODO`
-- line), the page serves bundled sample data instead. So you can fill
-- in one section at a time and the page will still load.

-- ##industries
-- TODO: one row per industry for the comparison period.
-- Columns: industry STRING, lob STRING ('cre'|'ci'|'sbl'|'mfl'),
--          start FLOAT64, outflow FLOAT64 (negative), aq FLOAT64,
--          nbv FLOAT64 (positive), risk_start FLOAT64, risk_end FLOAT64.
SELECT
  industry, lob,
  start_balance_m   AS start,
  outflow_m         AS outflow,
  aq_migration_m    AS aq,
  new_business_m    AS nbv,
  avg_risk_start    AS risk_start,
  avg_risk_end      AS risk_end
FROM `your-project.your_dataset.industry_flows`
WHERE period_start = '${period_start}' AND period_end = '${period_end}';

-- ##migration
-- TODO: 5x5 rating-transition matrix in $M (Pass/Watch/Substandard/Doubtful/Loss).
-- Columns: from_rating STRING, to_rating STRING, balance_m FLOAT64.
SELECT from_rating, to_rating, SUM(balance_m) AS balance_m
FROM `your-project.your_dataset.risk_migration`
WHERE period = '${as_of}'
GROUP BY 1, 2;

-- ##timeseries
-- TODO: trailing 8-quarter time series per industry.
-- Columns: industry STRING, quarter_idx INT64 (0=oldest..7=newest),
--          balance FLOAT64, concentration FLOAT64 (% of portfolio),
--          aq FLOAT64 (weighted-avg risk rating).
SELECT industry, quarter_idx, balance, concentration, aq
FROM `your-project.your_dataset.industry_timeseries`
WHERE quarter_idx BETWEEN 0 AND 7;

-- ##obligors
-- TODO: obligor-level rows for the drill-down panel.
-- Columns: industry STRING, name STRING, balance FLOAT64,
--          risk STRING ('Pass'|'Watch'|'Substandard'|'Doubtful'|'Loss'),
--          flow STRING ('static'|'outflow'|'nbv'|'aq-up'|'aq-down').
SELECT industry, name, balance, risk, flow
FROM `your-project.your_dataset.obligors`
WHERE period = '${as_of}';
