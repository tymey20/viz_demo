"""Structured facts: the ONLY numbers commentary may contain."""
from __future__ import annotations

from .spec import ReportSpec
from .thresholds import rag

STATUS = {"G": "Green", "A": "Amber", "R": "Red"}


def build(spec: ReportSpec, datasets: dict) -> list[dict]:
    facts = []
    for ds_name, (df, _) in datasets.items():
        key = spec.datasets[ds_name].key
        if not key:
            continue
        for metric, rule in spec.thresholds.items():
            if metric not in df.columns:
                continue
            f = spec.fmt(metric)
            for _, row in df.iterrows():
                status = rag(float(row[metric]), rule, row)
                green, amber = rule.for_row(row)
                facts.append({
                    "dataset": ds_name, "metric": metric, "label": rule.label or metric.upper(),
                    "key": str(row[key]), "value": f.text(row[metric]), "raw": float(row[metric]),
                    "status": STATUS[status], "green": f.text(green), "amber": f.text(amber),
                })
    return facts


def allowed_numbers(facts: list[dict]) -> set[str]:
    """Every numeric token a commentary draft may contain."""
    out = set()
    for f in facts:
        for k in ("value", "green", "amber"):
            out.update(_tokens(f[k]))
    return out


def _tokens(s: str) -> set[str]:
    import re
    return set(re.findall(r"\d[\d,]*\.?\d*", s))
