# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

Proof-of-concept interactive analytics dashboard — a potential Tableau replacement built with pure HTML/CSS/JS and D3.js. Designed to be deployed on SharePoint as a self-contained static page to demonstrate what AI-assisted development (Claude Code) can produce for internal analytics.

## Architecture

- **viz.html** — Self-contained single-file dashboard (HTML + CSS + D3.js). All styles, data, and logic are inline. Uses D3 v7 via CDN.
- **main.py** — Placeholder PyCharm project file (not used by the dashboard).
- **.venv** — Python 3.11 virtual environment.

### Dashboard Components (viz.html)
- **KPI cards** — Top-level summary metrics (start balance, outflows, AQ migration, new business, net change, end balance)
- **Waterfall chart** — Portfolio bridge showing balance flows, toggleable between $ and %
- **Detail table** — Industry/severity breakdown with clickable drill-down rows
- **Risk migration heatmap** — Rating transition matrix (Pass → Loss)
- **Time series** — Trailing 8-quarter trends for balance, concentration, and avg risk
- **Drill-down panel** — Slide-out panel with obligor-level detail, mini waterfall, and sortable table

### Key Design Decisions
- All data is currently hardcoded in JS objects (`DATA`, `OBLIGOR_DATA`) — no external data loading yet
- Filter state managed via a simple `state` object, not a framework
- D3.js used for SVG charts; tables and heatmap are HTML-rendered
- Animations via CSS `@keyframes` and D3 transitions
- Responsive: grid collapses at 1200px breakpoint

## Development

Open `viz.html` directly in a browser — no build step or server required.

## Goals

- Remove any company-specific branding and replace with generic/neutral branding
- Add ability to load data from CSV/Parquet files instead of hardcoded JS
- Create additional visualization examples to showcase the platform's capabilities
- Target deployment: SharePoint (static HTML, no server-side processing)
