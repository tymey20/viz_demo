"""BigQuery helper.

Authentication
--------------
- **Local VM**: run `gcloud auth application-default login` once, then
  `gcloud config set project <your-project>`. ADC picks it up.
- **Cloud Run**: deploy with `--service-account <sa-email>` and the
  attached service account is used automatically (no key files).

The project ID resolves from `BQ_PROJECT` → `GOOGLE_CLOUD_PROJECT` →
the gcloud / Cloud Run default.

Query helpers
-------------
`run_sql(text)` runs a single query and returns a DataFrame.
`run_section_file(path)` reads a `.sql` file split into ``-- ##name``
sections and returns ``{section_name: DataFrame}``.

Each section is cached in-memory with a TTL (default 5 minutes), so
multiple page loads in a row don't re-run the same query.
"""

from __future__ import annotations

import os
import re
import time
from pathlib import Path
from typing import Dict, Mapping

import pandas as pd

from lib import period as period_mod


_client = None
_cache: Dict[str, tuple[float, pd.DataFrame]] = {}
CACHE_TTL_SECONDS = int(os.environ.get("BQ_CACHE_TTL", "300"))


def _project() -> str | None:
    return os.environ.get("BQ_PROJECT") or os.environ.get("GOOGLE_CLOUD_PROJECT")


def get_client():
    """Lazy BigQuery client. Returns None if google-cloud-bigquery isn't
    installed or ADC isn't configured — callers should fall back to
    sample data in that case."""
    global _client
    if _client is not None:
        return _client
    try:
        from google.cloud import bigquery
        _client = bigquery.Client(project=_project())
        return _client
    except Exception:
        return None


def run_sql(sql: str) -> pd.DataFrame:
    """Run one query, return a DataFrame. Cached by SQL text."""
    key = sql.strip()
    now = time.time()
    hit = _cache.get(key)
    if hit and now - hit[0] < CACHE_TTL_SECONDS:
        return hit[1]
    client = get_client()
    if client is None:
        raise RuntimeError("BigQuery client unavailable (check gcloud ADC / google-cloud-bigquery install)")
    df = client.query(sql).to_dataframe(create_bqstorage_client=False)
    _cache[key] = (now, df)
    return df


SECTION_RE = re.compile(r"^\s*--\s*##\s*([A-Za-z0-9_]+)\s*$", re.MULTILINE)


def split_sections(sql_text: str) -> Dict[str, str]:
    """Split a SQL file into named sections.

    Sections are delimited by lines like ``-- ##sectionname``. The text
    before the first marker is ignored. Returns ``{name: sql}``.
    """
    matches = list(SECTION_RE.finditer(sql_text))
    if not matches:
        # No sections — treat whole file as a single "main" query.
        return {"main": sql_text.strip()}
    sections: Dict[str, str] = {}
    for i, m in enumerate(matches):
        name = m.group(1)
        start = m.end()
        end = matches[i + 1].start() if i + 1 < len(matches) else len(sql_text)
        body = sql_text[start:end].strip()
        if body:
            sections[name] = body
    return sections


def substitute_tokens(sql: str, tokens: Mapping[str, str] | None = None) -> str:
    """Replace ``${name}`` tokens in SQL with their string values.

    Default tokens come from ``lib.period.period_context`` so SQL files
    can reference ``${as_of}`` (current quarter code, e.g. '2026Q1'),
    ``${prior}`` (prior quarter code), ``${period_start}`` /
    ``${period_end}`` (ISO dates), etc.

    Caller-supplied ``tokens`` win over the defaults — useful if a
    future "as-of date picker" wants to override the current quarter.
    """
    ctx = period_mod.period_context()
    defaults = {
        "as_of":        ctx["period_code"],
        "as_of_label":  ctx["period_label"],
        "prior":        ctx["prior_code"],
        "prior_label":  ctx["prior_label"],
        "period_start": ctx["period_start"],
        "period_end":   ctx["period_end"],
    }
    if tokens:
        defaults.update(tokens)
    for k, v in defaults.items():
        sql = sql.replace("${" + k + "}", str(v))
    return sql


def run_section_file(path: Path, tokens: Mapping[str, str] | None = None) -> Dict[str, pd.DataFrame]:
    """Read a sectioned SQL file, substitute ``${...}`` tokens, run each section."""
    text = Path(path).read_text()
    return {name: run_sql(substitute_tokens(sql, tokens)) for name, sql in split_sections(text).items()}


def is_placeholder(sql_text: str) -> bool:
    """True if a SQL file is still a TODO stub (no real query yet)."""
    if not sql_text.strip():
        return True
    # Any line starting with `-- TODO` (case-insensitive) marks it as a stub.
    return any(line.lstrip().lower().startswith("-- todo") for line in sql_text.splitlines())
