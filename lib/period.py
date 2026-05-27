"""Reporting-period helpers.

For credit-risk analytics the "current" period is the most recently
*completed* calendar quarter, not the one in progress — analysts wait
until books close before publishing. So:

    today           reporting_quarter   prior_quarter
    2026-05-26      Q1 2026             Q4 2025
    2026-04-01      Q1 2026             Q4 2025
    2026-03-31      Q4 2025             Q3 2025

All helpers are pure functions of ``today`` (defaults to
``date.today()``) so they're trivial to unit test and easy to override
for "what would this look like in Q3 2026?" scenarios via the
``APEX_AS_OF`` env var (set to YYYY-MM-DD).
"""

from __future__ import annotations

import os
from dataclasses import dataclass
from datetime import date


@dataclass(frozen=True)
class Quarter:
    year: int
    q: int  # 1..4

    @classmethod
    def of(cls, d: date) -> "Quarter":
        return cls(d.year, (d.month - 1) // 3 + 1)

    def prev(self, n: int = 1) -> "Quarter":
        total = self.year * 4 + (self.q - 1) - n
        return Quarter(total // 4, (total % 4) + 1)

    @property
    def code(self) -> str:
        """BigQuery-friendly code, e.g. '2026Q1'."""
        return f"{self.year}Q{self.q}"

    @property
    def label(self) -> str:
        """Display label, e.g. 'Q1 2026'."""
        return f"Q{self.q} {self.year}"

    @property
    def short(self) -> str:
        """Short label used on time-series x-axes, e.g. \"Q1'26\"."""
        return f"Q{self.q}'{self.year % 100:02d}"

    @property
    def start_date(self) -> date:
        return date(self.year, (self.q - 1) * 3 + 1, 1)

    @property
    def end_date(self) -> date:
        # Last day of the quarter.
        next_q = self.prev(-1)  # negate: get next
        from datetime import timedelta
        return next_q.start_date - timedelta(days=1)


def _today() -> date:
    """Today, overridable via APEX_AS_OF for demos / what-ifs."""
    override = os.environ.get("APEX_AS_OF")
    if override:
        return date.fromisoformat(override.strip())
    return date.today()


def reporting_quarter(today: date | None = None) -> Quarter:
    """The most recently *completed* quarter as of `today`."""
    today = today or _today()
    return Quarter.of(today).prev(1)


def trailing_quarters(n: int = 8, today: date | None = None) -> list[Quarter]:
    """``n`` quarters ending at the reporting quarter (oldest first)."""
    rep = reporting_quarter(today)
    return [rep.prev(n - 1 - i) for i in range(n)]


def period_context(today: date | None = None) -> dict:
    """The bundle of period strings every payload ships down to the HTML."""
    rep = reporting_quarter(today)
    prior = rep.prev(1)
    trail = trailing_quarters(8, today)
    return {
        "period_label": rep.label,                          # "Q1 2026"
        "period_short": rep.short,                          # "Q1'26"
        "period_code":  rep.code,                           # "2026Q1"
        "prior_label":  prior.label,                        # "Q4 2025"
        "prior_short":  prior.short,                        # "Q4'25"
        "prior_code":   prior.code,                         # "2025Q4"
        "bridge_label": f"{prior.label} → {rep.label}",# "Q4 2025 → Q1 2026"
        "quarters":     [q.short for q in trail],           # ["Q2'24", ... ,"Q1'26"]
        "period_start": rep.start_date.isoformat(),         # "2026-01-01"
        "period_end":   rep.end_date.isoformat(),           # "2026-03-31"
    }
