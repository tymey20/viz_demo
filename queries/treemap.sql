-- Portfolio Composition Treemap
-- One section. payloads.py rolls obligor rows up into a 3-level
-- LOB → Industry → Obligor hierarchy.

-- ##obligors
-- TODO: leaf-level obligor exposure with the full LOB/Industry path.
-- Columns: lob STRING (display label: 'C&I'|'CRE'|'SBL'|'Multifamily'),
--          industry STRING,
--          name STRING (obligor name),
--          value FLOAT64 (balance $M),
--          risk STRING ('Pass'|'Watch'|'Substandard'|'Doubtful'|'Loss').
-- Note: `lob` here is the DISPLAY name (with the ampersand), not the
-- code used elsewhere — the treemap uses it directly as a parent label.
SELECT lob_label AS lob, industry, name, balance_m AS value, risk
FROM `your-project.your_dataset.obligor_snapshot`
WHERE as_of_quarter = '${as_of}';
