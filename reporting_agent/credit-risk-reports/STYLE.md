# Style guide

Applies to every report. Code enforces most of it (`reportkit/style.py`, `reportkit/formats.py`);
this file is the human- and agent-readable version. Change both together.

## Visual
- Branded master in `templates/`; reports never define their own colors, fonts, or positions.
- One idea per slide. `single` for a full-width exhibit, `two_up` for a summary table next to
  its chart. Never more than two exhibits on a slide.
- Slide title states the subject, not the finding ("Population Stability", not "PSI is worsening").
  Findings live on the Commentary slide.
- Native tables and charts only. No screenshots, no pasted images of charts.
- Charts: no chart title (the slide/caption has it), no gridlines, data labels on when there are
  two or fewer series, legend at the bottom only when there are two or more series.
- RAG colors mean one thing: threshold status computed by `reportkit.thresholds`. Never use red,
  amber, or green for anything else.
- Every content slide has the provenance footer; every slide has provenance in its notes.

## Numbers
- Formats are named (`pct1`, `usd_mm`, `bps`, `dec3`, ...) and set once per column in the spec.
  The same column is formatted the same way on every slide and in every report.
- Ratios display as percent (`pct1`/`pct2`); model statistics (Gini, KS, PSI) as `dec3`;
  exposures and revenue as `usd_mm`; margins as `bps`.
- Sort tables by the column the audience cares about (largest exposure first, alphabetical for
  segment summaries). State the sort in `order_by`; never rely on source order.

## Commentary
- Structure: status line, header, then one observation per line. Red before Amber, then by
  metric, then by entity.
- Sentence pattern: `<Metric> for <entity> is <Status> at <value>, <relation to threshold>.`
  Use the spec's `commentary` templates so wording is consistent across reports.
- Every number must come from `facts.json`. The build fails on any number that isn't there.
- Say what the data shows. Do not speculate on causes; add "Question for review:" lines instead.
- Do not soften: a Red is "Red" or "breaches", never "slightly elevated" or "worth watching".
- No narrative that would read the same regardless of the numbers ("continues to perform in
  line with expectations"). If nothing breached, use the `all_green` sentence and stop.
- Commentary is DRAFT until a named analyst sets `signed_off_by`. Never set it yourself.

## Naming
- Report ids: `snake_case`, `<subject>_<cadence>` (e.g. `pd_monitoring_quarterly`).
- Dataset names inside a spec are short nouns: `seg`, `trend`, `top_clients`.
- Output files: `<id>_<as_of>.pptx`; never rename by hand.
