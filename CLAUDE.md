# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

Apex Analytics — a credit-risk dashboard suite built as static HTML + D3 charts (the original polished design) fronted by a small FastAPI backend that runs BigQuery queries and serves the results as JSON. Designed to run on an internal VM today and deploy to Cloud Run later from the same code.

## Architecture

```
work_viz/
├── server.py                # FastAPI app; serves dashboards + /api/<slug> endpoints
├── dashboards/              # the polished HTML pages (each fetch()es its API)
│   ├── index.html           # landing page
│   ├── portfolio_flow.html  # waterfall + drill-down + heatmap + time series
│   ├── sankey.html          # rating-migration flow
│   ├── scatter.html         # risk-vs-spread bubble
│   ├── treemap.html         # LOB→Industry→Obligor
│   ├── geo.html             # US choropleth
│   └── gauges.html          # health gauges + utilization donuts + sparklines
├── queries/                 # one SQL file per dashboard, sectioned by `-- ##name`
│   └── …                    # Gemini CLI's playground — see GEMINI.md
├── lib/
│   ├── bq.py                # BQ client (lazy/cached), section-aware runner, `${as_of}` token substitution
│   ├── payloads.py          # sample data + DataFrame→JSON reshapers per dashboard
│   └── period.py            # reporting-quarter helpers (drives all dynamic dates)
├── Dockerfile               # Cloud Run-ready image
├── requirements.txt
├── GEMINI.md                # SQL-writing contract for Gemini CLI
└── README.md                # local run + Cloud Run deploy instructions
```

### Data flow

1. Browser requests `/<slug>` → FastAPI returns `dashboards/<slug>.html`.
2. The page's `bootstrap()` calls `GET /api/<slug>`.
3. `server.py` looks at `queries/<slug>.sql`:
   - If every section's body still starts with `-- TODO`, it's treated as a placeholder → the payload builder returns bundled sample data from `lib/payloads.py`.
   - Otherwise the runtime substitutes `${as_of}` / `${period_start}` / etc. tokens, runs each section against BigQuery (5-min in-memory cache), and the payload builder reshapes the DataFrames into the JSON shape the HTML expects.
4. Browser renders. Filter buttons (LOB / view) filter the in-memory dataset client-side — no extra API calls.

### Why this shape

- **Static HTML + FastAPI** instead of Streamlit: keeps the original D3 design pixel-for-pixel (Streamlit chrome competes with it), runs as one container on Cloud Run, and is straightforward for non-Python team members to read.
- **`queries/*.sql` as Gemini's only editing surface**: SQL contract per dashboard is documented in `GEMINI.md`; HTML, Python, and routing stay off-limits.
- **`${as_of}` tokens** for dates: dashboards always reflect the most-recently-completed quarter without anyone editing files at quarter close.

## Development

```bash
# Local dev (no BQ auth needed; runs on sample data):
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
python server.py   # http://localhost:8000

# With live BigQuery:
gcloud auth application-default login
gcloud config set project <your-project>
python server.py
```

Override the reporting quarter for what-if scenarios:
`APEX_AS_OF=2025-08-15 python server.py` → dashboards render as if today were Aug 15, 2025.

## Adding a new dashboard

1. Drop `dashboards/<slug>.html` (copy an existing file as a template — they all use the same `bootstrap()` pattern).
2. Drop `queries/<slug>.sql` with `-- ##section` markers and `-- TODO` bodies.
3. Add a `<slug>_payload(sections=None)` function to `lib/payloads.py` and register it in `server.PAYLOAD_BUILDERS`.
4. The new dashboard is live at `/<slug>` with API at `/api/<slug>`.

## Deployment

- **VM**: `python server.py` (binds 0.0.0.0:8000), behind tmux/screen or a systemd unit.
- **Cloud Run**: `gcloud run deploy apex-analytics --source . --service-account <sa>`. The container is built from the `Dockerfile`. BigQuery auth uses the attached service account (no key files).

See `README.md` for full deploy instructions and `GEMINI.md` for the SQL-writing contract.
