# Gemini CLI context — Apex Analytics

This file is the brief for Gemini CLI when authoring SQL for the
Apex Analytics dashboard suite. **Your job is to edit
`queries/*.sql` files. Nothing else.** The HTML, Python, and routing
are already in place — they just need queries that return the right
columns.

## How the app uses your SQL

```
queries/<dashboard>.sql   ←  YOU EDIT THIS
        │
        ▼
lib/bq.py                   splits the file on `-- ##section` markers,
                            runs each section, returns DataFrames.
        │
        ▼
lib/payloads.py             reshapes DataFrames into the JSON the HTML
                            JS expects (key contract documented per
                            payload builder).
        │
        ▼
GET /api/<dashboard>        JSON served to the browser.
```

Each `queries/<slug>.sql` file holds one or more *sections* delimited
by lines that look like `-- ##sectionname`. Section names are part
of the contract — they correspond to keys in `payloads.py` and **must
match exactly**.

## Behavior while you're writing SQL

As long as any line in a SQL file starts with `-- TODO`, that whole
file is treated as a placeholder and the page falls back to sample
data. So you can replace the TODOs one section at a time. Once *every*
TODO in a file is gone, the file goes "live" and the page will use
your queries.

If a live query throws (e.g. bad table reference, permission error),
the server logs the error and falls back to sample data for that page
load. So a broken query won't take the site down — but the page will
silently show demo data until you fix it. Tail `uvicorn`'s stdout to
catch this.

## Rules

1. **Only edit files under `queries/`.** Do not touch `server.py`,
   `lib/`, or anything in `dashboards/`. If something in payload-land
   genuinely needs a new column, raise it — don't paper over it in SQL.
2. **Match column names exactly** as listed below. Use `AS` to rename
   warehouse columns into the contract.
3. **Match types.** `INT64` for counts, `FLOAT64` for amounts/rates,
   `STRING` for everything else. Avoid `NUMERIC`/`BIGNUMERIC` (pandas
   handles them awkwardly).
4. **Don't pre-compute derived columns** unless the contract says so —
   payloads.py does the reshaping.
5. **Never hardcode quarter or date literals.** Use the `${...}`
   tokens below — the runtime substitutes them before execution so the
   dashboards always reflect the current reporting period.

## Date / period tokens

The runtime computes the reporting period from today's date (the most
recently *completed* calendar quarter) and substitutes these tokens
in every SQL file before sending it to BigQuery:

| Token | Example | What it is |
| --- | --- | --- |
| `${as_of}` | `2026Q1` | Current reporting quarter, BQ-friendly code. |
| `${as_of_label}` | `Q1 2026` | Same quarter, display form. |
| `${prior}` | `2025Q4` | Prior quarter code (for QoQ joins). |
| `${prior_label}` | `Q4 2025` | Prior quarter, display form. |
| `${period_start}` | `2026-01-01` | First day of the reporting quarter. |
| `${period_end}` | `2026-03-31` | Last day of the reporting quarter. |

Use them like literals — quote them as you would any string:
```sql
WHERE period = '${as_of}'
WHERE as_of_date BETWEEN '${period_start}' AND '${period_end}'
```

For "what would this look like in a previous quarter?" debugging,
set `APEX_AS_OF=YYYY-MM-DD` and restart the server. The tokens will
reflect *that* date's reporting quarter.

## Per-dashboard SQL contracts

### `queries/portfolio_flow.sql` — 4 sections

| Section | Columns | Notes |
| --- | --- | --- |
| `industries` | `industry STRING, lob STRING, start FLOAT64, outflow FLOAT64, aq FLOAT64, nbv FLOAT64, risk_start FLOAT64, risk_end FLOAT64` | `lob` is the code (`cre`/`ci`/`sbl`/`mfl`). `outflow` is negative. `nbv` is positive. `aq` can be either sign. |
| `migration` | `from_rating STRING, to_rating STRING, balance_m FLOAT64` | Ratings: `Pass`/`Watch`/`Substandard`/`Doubtful`/`Loss` (case-sensitive). Missing cells default to 0. |
| `timeseries` | `industry STRING, quarter_idx INT64, balance FLOAT64, concentration FLOAT64, aq FLOAT64` | `quarter_idx` 0..7, oldest → newest. |
| `obligors` | `industry STRING, name STRING, balance FLOAT64, risk STRING, flow STRING` | `flow` ∈ {`static`, `outflow`, `nbv`, `aq-up`, `aq-down`}. |

### `queries/sankey.sql` — 1 section

| Section | Columns |
| --- | --- |
| `migration` | `lob STRING, from_rating STRING, to_rating STRING, balance_m FLOAT64` |

`lob` includes the literal value `'all'` for the unfiltered aggregate plus the four LOB codes.

### `queries/scatter.sql` — 1 section

| Section | Columns |
| --- | --- |
| `segments` | `segment STRING, lob STRING, exposure FLOAT64, risk FLOAT64, spread FLOAT64` |

`spread` is in basis points. `risk` is the 1-10 internal rating, lower = better.

### `queries/geo.sql` — 1 section

| Section | Columns |
| --- | --- |
| `states` | `fips STRING, state STRING, abbr STRING, exposure FLOAT64, obligors INT64, risk FLOAT64, change FLOAT64, region STRING` |

`fips` is the two-character state code (with leading zero — `'06'` for CA). `region` ∈ {`Northeast`, `Midwest`, `Southeast`, `West`}.

### `queries/gauges.sql` — 3 sections

| Section | Columns |
| --- | --- |
| `gauges` | `title STRING, value FLOAT64, max FLOAT64, trend STRING, trend_dir STRING` |
| `donuts` | `title STRING, pct FLOAT64, limit_b FLOAT64, used_b FLOAT64` |
| `sparklines` | `title STRING, idx INT64, value FLOAT64, unit STRING` |

`trend_dir` is `'up'` or `'down'`. `pct` can exceed 100. `idx` is 0..7.

### `queries/treemap.sql` — 1 section

| Section | Columns |
| --- | --- |
| `obligors` | `lob STRING, industry STRING, name STRING, value FLOAT64, risk STRING` |

`lob` here is the **display label** (`'C&I'`, `'CRE'`, `'SBL'`,
`'Multifamily'`), not the code. The 3-level hierarchy
(LOB → Industry → Obligor) is built in Python from these flat rows.

## Adding a brand-new dashboard

If you need a dashboard that doesn't exist yet, **stop and ask for
help** — adding one requires touching `server.py` and `payloads.py`,
which is out of scope for SQL work.

## Reference data: the demo dataset

The sample dicts in `lib/payloads.py` (e.g. `SAMPLE_PORTFOLIO_FLOW`,
`SAMPLE_SANKEY`) are the exact JSON shapes the front-end expects.
Match those shapes once your SQL produces the right columns and the
payload builder will pivot them into JSON automatically.
