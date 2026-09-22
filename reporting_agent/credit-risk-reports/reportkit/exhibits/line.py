"""Time-series line chart: x = date column, one line per value of `series`, y = metric.
The pivot here is presentation only; the numbers are untouched."""
from __future__ import annotations

import html
from typing import Literal

from pptx.enum.chart import XL_CHART_TYPE

from ._chart import add_chart, reconcile_chart
from .base import Exhibit


class Line(Exhibit):
    type: Literal["line"]
    data: str
    x: str
    y: str
    series: str | None = None

    def _pivot(self, ctx):
        df, f = ctx.df(self.data), ctx.spec.fmt(self.y)
        xs = sorted(df[self.x].astype(str).unique())
        if self.series:
            out = []
            for name, g in df.groupby(self.series, sort=True):
                m = dict(zip(g[self.x].astype(str), g[self.y]))
                out.append((str(name), [f.chart_value(m[x]) for x in xs]))   # KeyError = missing period, by design
            return xs, out
        m = dict(zip(df[self.x].astype(str), df[self.y]))
        return xs, [(self.y.upper(), [f.chart_value(m[x]) for x in xs])]

    def render_pptx(self, slide, box, ctx):
        xs, series = self._pivot(ctx)
        chart = add_chart(slide, box, XL_CHART_TYPE.LINE_MARKERS, xs, series, ctx.spec.fmt(self.y).excel)
        chart.plots[0].has_data_labels = False

    def render_html(self, ctx):
        xs, series = self._pivot(ctx)
        f = ctx.spec.fmt(self.y)
        head = "<tr><th></th>" + "".join(f"<th>{html.escape(x)}</th>" for x in xs) + "</tr>"
        rows = "".join(f"<tr><td>{html.escape(n)}</td>" + "".join(f"<td>{f.text(v / f.scale)}</td>" for v in vals) + "</tr>"
                       for n, vals in series)
        return f"<p><i>(line chart rendered as table in HTML)</i></p><table>{head}{rows}</table>"

    def reconcile(self, shapes, ctx):
        return reconcile_chart(self.title, shapes, [vals for _, vals in self._pivot(ctx)[1]])
