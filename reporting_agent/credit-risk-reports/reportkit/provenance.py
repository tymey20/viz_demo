"""Every output carries enough metadata to reproduce it."""
from __future__ import annotations

import hashlib
import subprocess
from dataclasses import dataclass, field
from datetime import datetime, timezone

import pandas as pd


@dataclass
class Provenance:
    report_id: str
    params: dict
    spec_hash: str
    git_sha: str
    run_utc: str
    sources: dict[str, dict] = field(default_factory=dict)   # dataset -> {source, rows, hash}

    @property
    def label(self) -> str:
        return self.params.get("as_of") or self.run_utc[:10]

    def footer(self) -> str:
        srcs = ", ".join(s["mart"] for s in self.sources.values())
        return f"Source: {srcs} | {' '.join(f'{k}={v}' for k, v in self.params.items())} | build {self.git_sha}"

    def notes(self) -> str:
        head = f"report_id={self.report_id} spec={self.spec_hash} git={self.git_sha} run={self.run_utc} params={self.params}"
        return head + "\n" + "\n".join(f"{k}: {v['source']} rows={v['rows']} hash={v['hash']}" for k, v in self.sources.items())


def _git_sha() -> str:
    try:
        sha = subprocess.check_output(["git", "rev-parse", "--short", "HEAD"], stderr=subprocess.DEVNULL, text=True).strip()
        return sha + ("-dirty" if subprocess.call(["git", "diff", "--quiet"], stderr=subprocess.DEVNULL) else "")
    except Exception:
        return "no-git"


def make(report_id: str, params: dict, spec_hash: str, datasets: dict[str, tuple[pd.DataFrame, str]], datasets_spec=None) -> Provenance:
    prov = Provenance(report_id, params, spec_hash, _git_sha(), datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"))
    for name, (df, src) in datasets.items():
        prov.sources[name] = {"mart": datasets_spec[name].mart if datasets_spec else name, "source": src, "rows": len(df), "hash": hashlib.sha256(df.to_csv(index=False).encode()).hexdigest()[:12]}
    return prov
