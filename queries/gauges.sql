-- Portfolio Health (gauges + donuts + sparklines)
-- Three sections.

-- ##gauges
-- TODO: top-of-page health-score gauges.
-- Columns: title STRING, value FLOAT64, max FLOAT64,
--          trend STRING ("+3pts from Q4"), trend_dir STRING ('up'|'down').
SELECT title, value, max, trend, trend_dir
FROM `your-project.your_dataset.health_scores`
WHERE as_of_quarter = '${as_of}';

-- ##donuts
-- TODO: limit-utilization donuts.
-- Columns: title STRING, pct FLOAT64 (0-100+),
--          limit_b FLOAT64 ($B policy limit), used_b FLOAT64 ($B in use).
SELECT title, pct, limit_b, used_b
FROM `your-project.your_dataset.limit_utilization`
WHERE as_of_quarter = '${as_of}';

-- ##sparklines
-- TODO: trailing-8-quarter mini-trend per metric (long format).
-- Columns: title STRING, idx INT64 (0..7 oldest..newest),
--          value FLOAT64, unit STRING ('' or '%').
SELECT title, idx, value, unit
FROM `your-project.your_dataset.health_trends`
WHERE idx BETWEEN 0 AND 7
ORDER BY title, idx;
