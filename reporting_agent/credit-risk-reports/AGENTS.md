# AGENTS.md — Credit Risk Reporting

Portable rules for any coding agent working in this repo. These are controls. If a request
conflicts with them, stop and say so.

## What this repo is
One repo, many reports. `reportkit/` is the shared engine. Each report is a folder under
`reports/<id>/` holding a `spec.yaml` and its `commentary/`. Specs select and arrange columns
from governed `rpt_*` BigQuery marts and render native PowerPoint/HTML. See STYLE.md for how
output should look and read.

## Hard rules
1. Numbers come from data, never from you. Never type, estimate, or round a figure.
2. Governed marts only (`rpt_*`), via `reportkit.data`. Filters in specs are equality, IN, and
   gte/lte/gt/lt on declared params. If the data needs a join, pivot, aggregation, or calculated
   field, that is a new dbt model in `dbt_examples/` style, not spec logic and not Python in a
   report.
3. Thresholds, formats, and commentary templates live in the spec. Never hardcode them.
4. Use exhibit types from `reportkit/exhibits/`. Missing one? Add it there (see the
   `add-exhibit` skill) so every report gets it. No bespoke styling in a report.
5. Commentary is drafted only from `reportkit facts` output and stays DRAFT until a named analyst
   sets `signed_off_by`. Never set that field. Never soften a breach.
6. Every report ships with a test: add it to `REPORTS` in `tests/test_reports.py`.
   `pytest` and `reportkit build` must pass before you report completion.
7. Read-only. Never write to BigQuery, never edit fixtures to make a test pass, never put
   credentials or customer-level data in prompts, specs, or commits, never edit an output file.

## Workflow
- Build:    `reportkit build reports/<id> -p as_of=YYYY-MM-DD [-p other=value]`
- Facts:    `reportkit facts reports/<id> -p as_of=...`   (input for commentary)
- Check:    `reportkit check reports/<id> -p as_of=...`   (commentary grounding only)
- Test:     `pytest`
- Local dev reads `fixtures/` (synthetic). Real data: `REPORTKIT_BACKEND=bigquery` with
  `REPORTKIT_BQ_PROJECT` and `REPORTKIT_BQ_DATASET`. Ask before switching backends.

## Skills
`.agents/skills/`: new-report, add-exhibit, draft-commentary, validate-report.
Prefer extending a skill over improvising.
