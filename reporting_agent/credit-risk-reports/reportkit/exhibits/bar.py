from __future__ import annotations

import html
from typing import Literal

from pptx.enum.chart import XL_CHART_TYPE

from .. import style
from ..thresholds import rag
from ._chart import add_chart, reconcile_chart
from .base import Exhibit, rgb


class _CategoryChart(Exhibit):
    data: str
    category: str
    values: list[str]
    rag: list[str] = []
    kind: XL_CHART_TYPE = XL_CHART_TYPE.COLUMN_CLUSTERED
    model_config = {"arbitrary_types_allowed": True}

    def _series(self, ctx):
        df, spec = ctx.df(self.data), ctx.spec
        return [(v.replace("_", " ").upper(), [spec.fmt(v).chart_value(x) for x in df[v]]) for v in self.values]

    def render_pptx(self, slide, box, ctx):
        df, spec = ctx.df(self.data), ctx.spec
        chart = add_chart(slide, box, self.kind, [str(c) for c in df[self.category]], self._series(ctx),
                          spec.fmt(self.values[0]).excel)
        for si, metric in enumerate(self.values):
            if metric in self.rag and metric in spec.thresholds:
                for pi, (_, row) in enumerate(df.iterrows()):
                    pt = chart.plots[0].series[si].points[pi]
                    pt.format.fill.solid()
                    pt.format.fill.fore_color.rgb = rgb(style.RAG[rag(float(row[metric]), spec.thresholds[metric], row)])

    def render_html(self, ctx):
        df, spec = ctx.df(self.data), ctx.spec
        head = "<tr><th>" + html.escape(self.category) + "</th>" + "".join(f"<th>{v}</th>" for v in self.values) + "</tr>"
        rows = "".join("<tr><td>" + html.escape(str(r[self.category])) + "</td>" +
                       "".join(f"<td>{spec.fmt(v).text(r[v])}</td>" for v in self.values) + "</tr>" for _, r in df.iterrows())
        return f"<p><i>(chart rendered as table in HTML)</i></p><table>{head}{rows}</table>"

    def reconcile(self, shapes, ctx):
        return reconcile_chart(self.title, shapes, [vals for _, vals in self._series(ctx)])


class Bar(_CategoryChart):
    type: Literal["bar"]
    kind: XL_CHART_TYPE = XL_CHART_TYPE.BAR_CLUSTERED


class Column(_CategoryChart):
    type: Literal["column"]
    kind: XL_CHART_TYPE = XL_CHART_TYPE.COLUMN_CLUSTERED
