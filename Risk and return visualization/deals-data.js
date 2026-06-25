/* ============================================================================
   RISK & RETURN DASHBOARD — DEAL DATA
   ----------------------------------------------------------------------------
   This is the ONLY file you need to edit to load your real portfolio.
   Replace the empty array below with one object per deal.

   While this array is empty, the dashboard runs on built-in SAMPLE data and
   the header shows an orange "Sample data" badge. As soon as it has rows, the
   badge turns green ("Live data · N deals") and every chart uses your numbers.

   Lines of business and industries are picked up automatically from your data
   — whatever LOB and industry names you use will appear as their own filters,
   series and dropdown entries. (The three names "Institutional Banking",
   "Real Estate", "Middle Market Business Banking" get fixed colors; any others
   are assigned colors automatically.)

   ----------------------------------------------------------------------------
   FIELD REFERENCE  (one object = one deal)

   REQUIRED (map these from your data):
     lob        Line of business name (free text — your internal name is fine).
     industry   Industry / sector name, free text (e.g. "Healthcare").
     netIncome  Net income for the deal, in dollars (e.g. 1850000).
     blendedCapital  Blended (regulatory + economic) capital, in dollars.

   STRONGLY RECOMMENDED:
     exposure   Exposure / EAD / commitment, in dollars.
     rating     Risk rating on a 1–10 scale (1 = best, 10 = worst).
                If your scale differs, convert to 1–10 before loading.

   OPTIONAL (filled in automatically if omitted):
     id         Deal identifier (any string). Auto-generated if missing.
     robc       Return on Blended Capital, in PERCENT (e.g. 16.4).
                If omitted, derived as netIncome / blendedCapital * 100.
     tenor      Tenor in years (e.g. 5). Defaults by LOB if omitted.
     spread     Spread in bps. Estimated if omitted.
     mix        Product mix as an object whose values are shares (any units —
                they are normalized to 100%). Keys:
                  { lending, deposits, ep, capmkts }
                (lending = lending balances, deposits = deposits/DDA,
                 ep = electronic payments, capmkts = capital markets)
                If omitted, a mix is modeled from the deal's return. Supply
                real mix data here to make the "Score a Deal" product-mix
                comparison exact.

   NUMBERS: plain numbers, no "$" or "," (1850000, not "$1,850,000").
            Dollar fields are absolute dollars, not millions.
   ============================================================================ */

window.DEALS = [

  /* ---- EXAMPLE ROWS (delete these and paste your own) ----
  {
    id: "D-1001",
    lob: "Middle Market Business Banking",
    industry: "Healthcare",
    netIncome: 1850000,
    blendedCapital: 11200000,
    exposure: 84000000,
    rating: 4,
    tenor: 3.5,
    mix: { lending: 58, deposits: 22, ep: 12, capmkts: 8 }
  },
  {
    id: "D-1002",
    lob: "Institutional Banking",
    industry: "Technology",
    netIncome: 6200000,
    blendedCapital: 48000000,
    exposure: 410000000,
    rating: 3,
    tenor: 5
    // robc, spread, mix all omitted -> derived/modeled automatically
  },
  ------------------------------------------------------------ */

];
