# credit-risk-reports

One repo, many reports. Spec-driven, reproducible PowerPoint/HTML packs from governed BigQuery
marts, built to be extended by Antigravity or any coding agent. Replaces Tableau-and-screenshot
workflows for recurring reports. Every build reconciles the deck to source and fails on mismatch.

```
credit-risk-reports/
  reportkit/            shared engine (data, formats, thresholds, exhibits, renderers, validate)
  reports/<id>/         one folder per report: spec.yaml + commentary/<as_of>.md
  fixtures/             synthetic CSV per rpt_* mart, for dev and tests
  templates/            branded PowerPoint master
  dbt_examples/         what rpt_* marts look like
  STYLE.md              visual, numeric, and commentary style guide
  AGENTS.md GEMINI.md   agent rules;  .agents/skills/  agent playbooks
  tests/                every report builds + reconciles; controls are tested
```

## Quick start
```bash
pip install -e ".[dev]"                 # add ,bigquery for warehouse access
pytest
reportkit build reports/pd_monitoring_quarterly -p as_of=2026-06-30
reportkit build reports/raroc_committee        -p as_of=2026-08-31 -p lob="Commercial Banking"
```
Outputs land in `out/`. Real data: `export REPORTKIT_BACKEND=bigquery REPORTKIT_BQ_PROJECT=... REPORTKIT_BQ_DATASET=...`

## How a report works
A spec declares **params** (as_of, portfolio, scenario...), **datasets** (an `rpt_*` mart plus
predefined filters, sort, limit), **formats** per column, **thresholds** (with per-segment
overrides), **slides** made of exhibits from the registry (table, bar, column, line,
commentary), and **commentary templates**. To run next month: change `-p as_of=`. To change
the pack: edit the YAML. Nothing is copied from a previous deck.

Data shaping is not allowed in specs. Joins, pivots, aggregations, and calculated fields belong
in dbt, where they are tested and have lineage. Specs only select, filter, sort, and arrange.

## Controls
- Mart names and filter columns are validated identifiers; queries are parameterized; filters
  are limited to =, IN, and range operators on declared params.
- RAG status is computed from spec thresholds by code. The model never decides a status.
- Every table cell and chart data point is reconciled to source on build (`reportkit/validate.py`).
  Tests prove tampering is caught.
- Commentary defaults to deterministic sentences from the spec's templates. An agent or analyst
  draft may replace it; every number in a draft must exist in `facts.json` or the build fails.
  Drafts show DRAFT until a named analyst sets `signed_off_by`.
- Provenance (params, source marts, row counts, data hashes, spec hash, git SHA, run time) is in
  every slide's notes and the footer.

## Adding a report
Use the `new-report` skill, or by hand: copy the nearest `reports/*/spec.yaml`, point it at
the marts, set formats/thresholds/slides, add fixtures, add the report to `tests/test_reports.py`.

## Before real use
1. Put the branded master in `templates/` and set layout names in `reportkit/style.py`.
2. Point one spec at a real mart with read-only credentials; compare against the manual pack.
3. Replace the placeholder thresholds and commentary wording with the policy-sourced values.
