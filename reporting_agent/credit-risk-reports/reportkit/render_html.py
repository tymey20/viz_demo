from __future__ import annotations

import html
from pathlib import Path

from .exhibits.base import Ctx

CSS = ("body{font-family:Calibri,Arial,sans-serif;max-width:1000px;margin:2rem auto;color:#1f2933}"
       "table{border-collapse:collapse;margin:.5rem 0 1.5rem}td,th{border:1px solid #ccc;padding:6px 10px;text-align:right}"
       "td:first-child,th:first-child{text-align:left}footer{margin-top:2rem;font-size:11px;color:#5f6b7a;white-space:pre-wrap}")


def render(ctx: Ctx, out: Path) -> Path:
    spec, prov = ctx.spec, ctx.prov
    parts = [f"<h1>{html.escape(spec.title)}</h1><p>{html.escape('  |  '.join(f'{k}: {v}' for k, v in prov.params.items()))}  |  Owner: {html.escape(spec.owner)}</p>"]
    for s in spec.slides:
        parts.append(f"<h2>{html.escape(s.title)}</h2>")
        for ex in s.exhibits:
            if len(s.exhibits) > 1:
                parts.append(f"<h3>{html.escape(ex.title)}</h3>")
            parts.append(ex.render_html(ctx))
    parts.append(f"<footer>{html.escape(prov.notes())}</footer>")
    path = out / f"{spec.id}_{prov.label}.html"
    path.write_text(f"<!doctype html><meta charset=utf-8><style>{CSS}</style>{''.join(parts)}")
    return path
