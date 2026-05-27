"""Apex Analytics — FastAPI entrypoint.

Serves the static dashboard HTML and the JSON endpoints the pages
fetch. Designed to run as one process on a VM today and as a Cloud
Run container later (same code, same auth path via ADC).

Routes
------
  GET /                  → dashboards/index.html (landing page)
  GET /healthz           → liveness probe (used by Cloud Run)
  GET /<slug>            → dashboards/<slug>.html
  GET /api/<slug>        → JSON payload for that dashboard
                            - reads queries/<slug>.sql if present and
                              non-placeholder; otherwise sample data.

Adding a new dashboard: see GEMINI.md and the registry below.
"""

from __future__ import annotations

import os
from pathlib import Path
from typing import Callable, Dict, Optional

from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse, JSONResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles

from lib import bq, payloads

ROOT = Path(__file__).parent
DASHBOARDS_DIR = ROOT / "dashboards"
QUERIES_DIR = ROOT / "queries"


# slug -> payload builder. Keep alphabetical for sanity.
PAYLOAD_BUILDERS: Dict[str, Callable] = {
    "gauges": payloads.gauges_payload,
    "geo": payloads.geo_payload,
    "portfolio_flow": payloads.portfolio_flow_payload,
    "sankey": payloads.sankey_payload,
    "scatter": payloads.scatter_payload,
    "treemap": payloads.treemap_payload,
}


app = FastAPI(title="Apex Analytics", docs_url="/api/docs", redoc_url=None)

# Mount /dashboards as static so relative asset paths (if any are added
# later) Just Work. The route handlers below take precedence for the
# specific HTML files we serve directly.
if DASHBOARDS_DIR.exists():
    app.mount("/static", StaticFiles(directory=DASHBOARDS_DIR), name="static")


@app.get("/healthz")
def healthz() -> dict:
    return {"ok": True}


@app.get("/", include_in_schema=False)
def index() -> FileResponse:
    return FileResponse(DASHBOARDS_DIR / "index.html")


@app.get("/api/{slug}")
def api(slug: str) -> JSONResponse:
    if slug not in PAYLOAD_BUILDERS:
        raise HTTPException(404, f"unknown dashboard: {slug}")
    builder = PAYLOAD_BUILDERS[slug]
    sections = _try_run_queries(slug)
    payload = builder(sections)
    return JSONResponse(payload)


@app.get("/{slug}", include_in_schema=False)
def page(slug: str) -> FileResponse:
    # Allow slugs with or without .html
    name = slug[:-5] if slug.endswith(".html") else slug
    candidate = DASHBOARDS_DIR / f"{name}.html"
    if candidate.exists():
        return FileResponse(candidate)
    raise HTTPException(404)


def _try_run_queries(slug: str) -> Optional[Dict]:
    """Run queries/<slug>.sql if present and non-placeholder. Returns
    a dict of section_name -> DataFrame, or None if we should use
    sample data.
    """
    sql_file = QUERIES_DIR / f"{slug}.sql"
    if not sql_file.exists():
        return None
    text = sql_file.read_text()
    if bq.is_placeholder(text):
        return None
    try:
        return bq.run_section_file(sql_file)
    except Exception as exc:  # noqa: BLE001
        # Log and fall through to sample data so the page still renders.
        print(f"[api/{slug}] BigQuery failed, using sample data: {exc}")
        return None


if __name__ == "__main__":
    import uvicorn
    port = int(os.environ.get("PORT", "8000"))
    uvicorn.run(app, host="0.0.0.0", port=port)
