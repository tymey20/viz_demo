# Apex Analytics

Internal credit-risk dashboard suite. Static HTML + D3 front-end,
small FastAPI backend that runs BigQuery queries and serves the
results as JSON. One Python process, deployable on a VM today or
Cloud Run tomorrow.

## Repo layout

```
work_viz/
├── server.py                # FastAPI: serves HTML + /api/<slug> endpoints
├── dashboards/              # the polished HTML pages (with fetch())
│   ├── index.html           # landing page
│   ├── portfolio_flow.html
│   ├── sankey.html
│   ├── scatter.html
│   ├── treemap.html
│   ├── geo.html
│   └── gauges.html
├── queries/                 # one SQL file per dashboard — Gemini's playground
│   ├── portfolio_flow.sql
│   ├── sankey.sql
│   ├── scatter.sql
│   ├── treemap.sql
│   ├── geo.sql
│   └── gauges.sql
├── lib/
│   ├── bq.py                # BigQuery client, section-aware runner, cache
│   └── payloads.py          # demo data + DataFrame→JSON reshaping per dashboard
├── Dockerfile               # Cloud Run-ready image
├── requirements.txt
├── GEMINI.md                # SQL-writing contract for Gemini CLI
└── README.md
```

## Local dev

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt

# Optional — for live BigQuery data:
gcloud auth application-default login
gcloud config set project <your-project>

python server.py            # serves on http://localhost:8000
# or: uvicorn server:app --reload
```

Open <http://localhost:8000>. Every page loads sample data out of the
box. Once you fill in the SQL placeholders in `queries/<dashboard>.sql`
(see `GEMINI.md`), that page switches to live BigQuery data.

If a query fails at runtime, the server logs the error and the page
silently falls back to sample data — tail `uvicorn`'s stdout to spot
breakage.

## VM deploy

```bash
# On the VM (one-time):
gcloud auth application-default login
gcloud config set project <your-project>
git clone … work_viz && cd work_viz
python -m venv .venv && .venv/bin/pip install -r requirements.txt

# Run (under tmux/screen for "temporary", or as a systemd unit for "real"):
.venv/bin/python server.py    # 0.0.0.0:8000
```

Access via SSH tunnel: `ssh -L 8000:localhost:8000 <user>@<vm>`.

## Cloud Run deploy

```bash
gcloud run deploy apex-analytics \
    --source . \
    --region us-central1 \
    --service-account apex-analytics@<project>.iam.gserviceaccount.com \
    --allow-unauthenticated      # or use IAP / IAM authentication
```

The attached service account needs `roles/bigquery.dataViewer` on the
relevant datasets and `roles/bigquery.jobUser` on the project.

## Adding a new dashboard

1. Drop a new HTML file in `dashboards/<slug>.html`. Use one of the
   existing files as a template (look at the `bootstrap()` function
   at the end of any of them).
2. Drop a new SQL file in `queries/<slug>.sql` with `-- ##section`
   markers and `-- TODO` placeholder bodies.
3. Add a payload builder to `lib/payloads.py` (function
   `<slug>_payload(sections=None)` returning the JSON shape the HTML
   expects) and register it in `server.PAYLOAD_BUILDERS`.
4. The dashboard is now live at `/<slug>` with API at `/api/<slug>`.

## Environment variables

| Var | Default | Purpose |
| --- | --- | --- |
| `PORT` | `8000` | HTTP port to bind. Cloud Run sets this automatically. |
| `BQ_PROJECT` | (gcloud default) | Override the GCP project for queries. |
| `GOOGLE_CLOUD_PROJECT` | (gcloud default) | Standard fallback for `BQ_PROJECT`. |
| `BQ_CACHE_TTL` | `300` | Seconds to cache query results in-memory. |
