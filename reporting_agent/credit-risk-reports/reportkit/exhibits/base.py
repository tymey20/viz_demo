from __future__ import annotations

from dataclasses import dataclass
from typing import Any

import pandas as pd
from pptx.dml.color import RGBColor
from pydantic import BaseModel

from .. import style


@dataclass
class Ctx:
    spec: Any
    datasets: dict[str, tuple[pd.DataFrame, str]]
    prov: Any
    commentary: Any

    def df(self, name: str) -> pd.DataFrame:
        return self.datasets[name][0]


def rgb(h: str) -> RGBColor:
    return RGBColor.from_string(h)


class Exhibit(BaseModel):
    type: str
    title: str

    def render_pptx(self, slide, box, ctx: Ctx) -> None: ...
    def render_html(self, ctx: Ctx) -> str: ...
    def reconcile(self, slide_shapes: dict, ctx: Ctx) -> list[str]:
        """Consume the next shape of this exhibit's kind from slide_shapes and compare it to source."""
        return []
