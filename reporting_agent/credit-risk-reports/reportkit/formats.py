"""Named number formats. Reports reference these by name; never inline a format string.

py     : Python format applied to (value * scale)
excel  : PowerPoint/Excel number format applied to the raw chart value (unscaled unless
         scale != 1, in which case chart data is scaled too, so both stay consistent)
"""
from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class Format:
    py: str
    excel: str
    scale: float = 1.0

    def text(self, v) -> str:
        return self.py.format(float(v) * self.scale)

    def chart_value(self, v) -> float:
        return float(v) * self.scale


FORMATS: dict[str, Format] = {
    "str":    Format("{}", "General"),
    "int":    Format("{:,.0f}", "#,##0"),
    "dec2":   Format("{:.2f}", "0.00"),
    "dec3":   Format("{:.3f}", "0.000"),
    "pct1":   Format("{:.1%}", "0.0%"),
    "pct2":   Format("{:.2%}", "0.00%"),
    "bps":    Format("{:,.0f} bps", '#,##0" bps"', scale=10_000),
    "usd_mm": Format("${:,.1f}MM", '"$"#,##0.0"MM"'),
    "usd_k":  Format("${:,.0f}K", '"$"#,##0"K"'),
}


def get(name: str) -> Format:
    try:
        return FORMATS[name]
    except KeyError:
        raise ValueError(f"Unknown format {name!r}. Add it to reportkit/formats.py") from None
