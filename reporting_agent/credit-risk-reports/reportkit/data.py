"""Read-only data access: governed marts, predefined filters, parameterized queries."""
from __future__ import annotations

import operator
import os
import re
from pathlib import Path
from typing import Any

import pandas as pd

from .spec import Dataset

REPO_ROOT = Path(__file__).resolve().parent.parent
OPS = {"gte": ">=", "lte": "<=", "gt": ">", "lt": "<"}
PYOPS = {"gte": operator.ge, "lte": operator.le, "gt": operator.gt, "lt": operator.lt}
_PLACEHOLDER = re.compile(r"^\{(\w+)\}$")


def _sub(v: Any, params: dict) -> Any:
    """Replace a whole-string '{param}' with the param value. Partial templating is not allowed."""
    if isinstance(v, str):
        m = _PLACEHOLDER.match(v)
        if m:
            if m.group(1) not in params:
                raise ValueError(f"filter references undeclared param {m.group(1)!r}")
            return params[m.group(1)]
    if isinstance(v, list):
        return [_sub(x, params) for x in v]
    if isinstance(v, dict):
        return {k: _sub(x, params) for k, x in v.items()}
    return v


def resolved_filters(ds: Dataset, params: dict) -> dict[str, Any]:
    return {c: _sub(cond, params) for c, cond in ds.filters.items()}


def load(ds: Dataset, params: dict) -> tuple[pd.DataFrame, str]:
    backend = os.getenv("REPORTKIT_BACKEND", "fixtures")
    filters = resolved_filters(ds, params)
    if backend == "bigquery":
        return _bigquery(ds, filters)
    return _fixture(ds, filters)


def _fixture(ds: Dataset, filters: dict) -> tuple[pd.DataFrame, str]:
    path = REPO_ROOT / "fixtures" / f"{ds.mart}.csv"
    df = pd.read_csv(path)
    for col, cond in filters.items():
        s = df[col].astype(str) if df[col].dtype == object or isinstance(cond, str) else df[col]
        if isinstance(cond, dict):
            for op, val in cond.items():
                s2 = df[col].astype(str) if isinstance(val, str) else df[col]
                df = df[PYOPS[op](s2, val)]
        elif isinstance(cond, list):
            df = df[s.isin([str(x) if isinstance(x, str) else x for x in cond])]
        else:
            df = df[s == (str(cond) if isinstance(cond, str) else cond)]
    if ds.order_by:
        col, asc = ds.order_by.lstrip("-"), not ds.order_by.startswith("-")
        df = df.sort_values(col, ascending=asc)
    if ds.limit:
        df = df.head(ds.limit)
    df = df.reset_index(drop=True)
    if df.empty:
        raise ValueError(f"No rows in {path.name} for filters {filters}")
    return df, f"fixtures/{path.name}"


def _bigquery(ds: Dataset, filters: dict) -> tuple[pd.DataFrame, str]:
    from google.cloud import bigquery

    project, dataset = os.environ["REPORTKIT_BQ_PROJECT"], os.environ["REPORTKIT_BQ_DATASET"]
    table = f"{project}.{dataset}.{ds.mart}"
    where, qp = [], []

    def param(name, val):
        typ = "INT64" if isinstance(val, int) else "FLOAT64" if isinstance(val, float) else "STRING"
        qp.append(bigquery.ScalarQueryParameter(name, typ, val))
        return f"@{name}"

    i = 0
    for col, cond in filters.items():
        if isinstance(cond, dict):
            for op, val in cond.items():
                i += 1
                where.append(f"CAST({col} AS STRING) {OPS[op]} {param(f'p{i}', str(val))}" if isinstance(val, str)
                             else f"{col} {OPS[op]} {param(f'p{i}', val)}")
        elif isinstance(cond, list):
            names = []
            for val in cond:
                i += 1
                names.append(param(f"p{i}", val))
            where.append(f"CAST({col} AS STRING) IN ({', '.join(names)})")
        else:
            i += 1
            where.append(f"CAST({col} AS STRING) = {param(f'p{i}', str(cond))}")
    sql = f"SELECT * FROM `{table}`"
    if where:
        sql += " WHERE " + " AND ".join(where)
    if ds.order_by:
        sql += f" ORDER BY {ds.order_by.lstrip('-')}{' DESC' if ds.order_by.startswith('-') else ''}"
    if ds.limit:
        sql += f" LIMIT {int(ds.limit)}"
    df = bigquery.Client(project=project).query(sql, job_config=bigquery.QueryJobConfig(query_parameters=qp)).to_dataframe()
    if df.empty:
        raise ValueError(f"No rows in {table} for filters {filters}")
    return df, table
