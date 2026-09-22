"""Report spec schema. Specs SELECT and ARRANGE columns that already exist in rpt_* marts.
They never transform data: if you need a pivot, join, or calculated field, that is a dbt model.
"""
from __future__ import annotations

import hashlib
import re
from pathlib import Path
from typing import Any, Literal

import yaml
from pydantic import BaseModel, Field, field_validator, model_validator

from . import formats
from .exhibits import AnyExhibit
from .thresholds import Threshold

IDENT = re.compile(r"^[A-Za-z_][A-Za-z0-9_]*$")


class Param(BaseModel):
    type: Literal["date", "str", "int"] = "str"
    default: Any = None
    required: bool = False


class Dataset(BaseModel):
    mart: str
    key: str | None = None                   # entity column used in facts/commentary
    filters: dict[str, Any] = Field(default_factory=dict)
    order_by: str | None = None
    limit: int | None = None

    @field_validator("mart")
    @classmethod
    def governed(cls, v):
        if not (v.startswith("rpt_") and IDENT.match(v)):
            raise ValueError(f"mart must be a governed rpt_* model, got {v!r}")
        return v

    @field_validator("order_by", "key")
    @classmethod
    def ident(cls, v):
        if v is not None and not IDENT.match(v.lstrip("-")):
            raise ValueError(f"bad column name {v!r}")
        return v

    @field_validator("filters")
    @classmethod
    def simple_filters(cls, v):
        for col, cond in v.items():
            if not IDENT.match(col):
                raise ValueError(f"bad filter column {col!r}")
            if isinstance(cond, dict) and not set(cond) <= {"gte", "lte", "gt", "lt"}:
                raise ValueError(f"filter {col}: only gte/lte/gt/lt allowed, got {list(cond)}")
        return v


class Slide(BaseModel):
    title: str
    layout: Literal["single", "two_up", "commentary"] = "single"
    exhibits: list[AnyExhibit]

    @model_validator(mode="after")
    def exhibits_fit_layout(self):
        from .style import LAYOUTS
        n = len(LAYOUTS[self.layout])
        if len(self.exhibits) != n:
            raise ValueError(f"layout {self.layout!r} takes {n} exhibit(s), slide {self.title!r} has {len(self.exhibits)}")
        return self


class CommentaryRules(BaseModel):
    red: str = "{label} for {key} is Red at {value} (Amber threshold {amber})."
    amber: str = "{label} for {key} is Amber at {value} (Green threshold {green})."
    all_green: str = "All monitored metrics are within Green thresholds."
    header: str = "Key observations (system-generated from source data):"


class ReportSpec(BaseModel):
    id: str
    title: str
    owner: str
    params: dict[str, Param] = Field(default_factory=dict)
    datasets: dict[str, Dataset]
    formats: dict[str, str] = Field(default_factory=dict)      # column -> format name
    thresholds: dict[str, Threshold] = Field(default_factory=dict)
    slides: list[Slide]
    commentary: CommentaryRules = CommentaryRules()
    outputs: list[Literal["pptx", "html"]] = ["pptx"]
    template: str | None = None
    _dir: Path | None = None

    @field_validator("formats")
    @classmethod
    def known_formats(cls, v):
        for col, name in v.items():
            formats.get(name)
        return v

    @model_validator(mode="after")
    def exhibits_reference_datasets(self):
        for s in self.slides:
            for ex in s.exhibits:
                ds = getattr(ex, "data", None)
                if ds and ds not in self.datasets:
                    raise ValueError(f"exhibit {ex.title!r} references unknown dataset {ds!r}")
        return self

    def fmt(self, col: str) -> formats.Format:
        return formats.get(self.formats.get(col, "dec3"))

    @property
    def spec_hash(self) -> str:
        return hashlib.sha256(self.model_dump_json().encode()).hexdigest()[:12]

    @property
    def dir(self) -> Path:
        return self._dir


def load_spec(report_dir: str | Path) -> ReportSpec:
    report_dir = Path(report_dir)
    path = report_dir / "spec.yaml" if report_dir.is_dir() else report_dir
    with open(path) as f:
        spec = ReportSpec.model_validate(yaml.safe_load(f))
    spec._dir = path.parent
    return spec


def resolve_params(spec: ReportSpec, given: dict[str, str]) -> dict[str, Any]:
    out = {}
    for name, p in spec.params.items():
        if name in given:
            out[name] = int(given[name]) if p.type == "int" else given[name]
        elif p.default is not None:
            out[name] = p.default
        elif p.required:
            raise ValueError(f"missing required param {name!r}")
    unknown = set(given) - set(spec.params)
    if unknown:
        raise ValueError(f"unknown params {sorted(unknown)}; declare them in spec.params")
    return out
