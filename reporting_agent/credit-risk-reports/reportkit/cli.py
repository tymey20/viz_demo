"""reportkit build|facts|check reports/<id> [-p as_of=2026-06-30 -p scenario=baseline]"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from . import commentary, data, facts, provenance, render_html, render_pptx
from .exhibits.base import Ctx
from .spec import load_spec, resolve_params
from .validate import validate_pptx

RENDERERS = {"pptx": render_pptx.render, "html": render_html.render}


def prepare(report: str, raw_params: dict[str, str]) -> Ctx:
    spec = load_spec(report)
    params = resolve_params(spec, raw_params)
    datasets = {name: data.load(ds, params) for name, ds in spec.datasets.items()}
    prov = provenance.make(spec.id, params, spec.spec_hash, datasets, spec.datasets)
    fx = facts.build(spec, datasets)
    ctx = Ctx(spec, datasets, prov, commentary.build(spec, fx, prov.label))
    ctx.facts = fx
    return ctx


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(prog="reportkit")
    ap.add_argument("command", choices=["build", "facts", "check"])
    ap.add_argument("report", help="reports/<id> directory or a spec.yaml")
    ap.add_argument("-p", "--param", action="append", default=[], metavar="KEY=VALUE")
    ap.add_argument("--out", default="out")
    a = ap.parse_args(argv)
    raw = dict(p.split("=", 1) for p in a.param)
    out = Path(a.out); out.mkdir(parents=True, exist_ok=True)

    ctx = prepare(a.report, raw)
    label = f"{ctx.spec.id}_{ctx.prov.label}"

    if a.command == "facts":
        path = out / f"{label}_facts.json"
        path.write_text(json.dumps({"provenance": ctx.prov.__dict__, "facts": ctx.facts}, indent=2, default=str))
        print(path); return 0

    problems = []
    if ctx.commentary.source == "draft":
        problems += [f"commentary: ungrounded number {b}" for b in commentary.ungrounded(ctx.commentary.lines, ctx.facts)]
    if a.command == "check":
        for p in problems: print(f"VALIDATION: {p}", file=sys.stderr)
        print("commentary:", ctx.commentary.status, f"({ctx.commentary.source})")
        return 1 if problems else 0

    for fmt in ctx.spec.outputs:
        path = RENDERERS[fmt](ctx, out); print(path)
        if fmt == "pptx":
            problems += validate_pptx(path, ctx)
    for p in problems:
        print(f"VALIDATION: {p}", file=sys.stderr)
    return 1 if problems else 0


if __name__ == "__main__":
    sys.exit(main())
