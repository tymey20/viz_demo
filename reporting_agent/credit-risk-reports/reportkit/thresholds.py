"""Threshold definitions and deterministic RAG logic. The model never decides a status."""
from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, Field


class Threshold(BaseModel):
    direction: Literal["higher_better", "lower_better"]
    green: float
    amber: float
    label: str | None = None
    by: dict[str, dict[str, dict[str, float]]] = Field(default_factory=dict)  # {column: {value: {green, amber}}}

    def for_row(self, row) -> tuple[float, float]:
        for col, table in self.by.items():
            ov = table.get(str(row.get(col))) if row is not None else None
            if ov:
                return ov.get("green", self.green), ov.get("amber", self.amber)
        return self.green, self.amber


def rag(value: float, rule: Threshold, row=None) -> str:
    green, amber = rule.for_row(row)
    if rule.direction == "lower_better":
        return "G" if value <= green else "A" if value <= amber else "R"
    return "G" if value >= green else "A" if value >= amber else "R"
