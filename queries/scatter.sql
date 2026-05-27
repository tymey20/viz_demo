-- Risk-Return Scatter
-- Single section. One row per segment.

-- ##segments
-- TODO: segment snapshot for the current as-of quarter.
-- Columns: segment STRING (industry/sub-portfolio name),
--          lob STRING ('cre'|'ci'|'sbl'|'mfl'),
--          exposure FLOAT64 ($M),
--          risk FLOAT64 (1-10 internal rating, lower = better),
--          spread FLOAT64 (basis points, weighted-avg).
SELECT segment, lob, exposure, risk, spread
FROM `your-project.your_dataset.segment_snapshot`
WHERE as_of_quarter = '${as_of}';
