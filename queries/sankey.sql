-- Risk Migration Sankey
-- Single section. lib/payloads.py::sankey_payload pivots the rows
-- into one 5x5 matrix per LOB.

-- ##migration
-- TODO: rating transitions in $M, by LOB and the 'all' aggregate.
-- Columns: lob STRING ('all'|'cre'|'ci'|'sbl'|'mfl'),
--          from_rating STRING, to_rating STRING, balance_m FLOAT64.
SELECT lob, from_rating, to_rating, SUM(balance_m) AS balance_m
FROM `your-project.your_dataset.risk_migration_by_lob`
WHERE period = '${as_of}'
GROUP BY 1, 2, 3;
