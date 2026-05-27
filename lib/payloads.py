"""Dashboard payload builders.

Each dashboard has a function `<slug>_payload(sections=None)` that returns
the JSON dict the matching HTML file's JS expects. The optional
``sections`` arg is the dict returned by ``lib.bq.run_section_file`` —
when present, the BigQuery results are reshaped into the JSON contract;
when absent (or any required section is missing/empty), the function
returns the bundled sample data so the page still renders.

Why this shape? The original HTML was authored against specific
in-page constants (DATA, OBLIGOR_DATA, STATE_DATA, etc.). To minimize
churn in the HTML, the API returns those exact shapes verbatim.

To add a new dashboard:
1. Add a `<slug>_payload(sections=None)` function below.
2. Wire it into ``server.PAYLOAD_BUILDERS``.
3. Drop ``queries/<slug>.sql`` (sectioned by ``-- ##name``).
4. Drop ``dashboards/<slug>.html`` that fetches ``/api/<slug>``.
"""

from __future__ import annotations

import copy
from typing import Any, Dict, Optional

import pandas as pd

from lib import period as period_mod


# ----------------------------------------------------------------------------
# Sample data — drop-in dicts shaped exactly like the original HTML constants.
# ----------------------------------------------------------------------------

RATING_LABELS = ["Pass", "Watch", "Substandard", "Doubtful", "Loss"]


def _quarters() -> list[str]:
    """Trailing 8 quarter labels (e.g. \"Q2'24\"..\"Q1'26\"), computed fresh."""
    return [q.short for q in period_mod.trailing_quarters(8)]


def _with_period(payload: Dict[str, Any]) -> Dict[str, Any]:
    """Inject period context onto a payload before serving.

    The HTML reads `data.period_label`, `data.bridge_label`,
    `data.quarters`, etc., so every dashboard always shows the current
    reporting quarter without anyone editing HTML.
    """
    payload = copy.deepcopy(payload)
    payload.update(period_mod.period_context())
    # Always overwrite a `quarters` key in the payload (sample data has a
    # static one; live data won't have one). Keeps the contract consistent.
    payload["quarters"] = _quarters()
    return payload


SAMPLE_PORTFOLIO_FLOW: Dict[str, Any] = {
    "industries": [
        {"name": "Healthcare",    "lob": "ci",  "start": 820, "outflow": -95, "aq": -12, "nbv": 140, "riskStart": 3.2, "riskEnd": 3.4},
        {"name": "Technology",    "lob": "ci",  "start": 650, "outflow": -40, "aq":   8, "nbv": 110, "riskStart": 2.8, "riskEnd": 2.6},
        {"name": "Manufacturing", "lob": "ci",  "start": 540, "outflow": -70, "aq": -22, "nbv":  55, "riskStart": 4.1, "riskEnd": 4.4},
        {"name": "Retail Trade",  "lob": "ci",  "start": 410, "outflow": -85, "aq": -18, "nbv":  30, "riskStart": 4.5, "riskEnd": 4.8},
        {"name": "Office",        "lob": "cre", "start": 780, "outflow":-120, "aq": -35, "nbv":  45, "riskStart": 5.2, "riskEnd": 5.6},
        {"name": "Industrial",    "lob": "cre", "start": 520, "outflow": -30, "aq":   5, "nbv":  95, "riskStart": 3.0, "riskEnd": 2.9},
        {"name": "Retail CRE",    "lob": "cre", "start": 340, "outflow": -55, "aq": -15, "nbv":  20, "riskStart": 4.8, "riskEnd": 5.1},
        {"name": "Hospitality",   "lob": "cre", "start": 290, "outflow": -25, "aq":  -8, "nbv":  35, "riskStart": 4.0, "riskEnd": 3.8},
        {"name": "Prof Services", "lob": "sbl", "start": 180, "outflow": -20, "aq":  -3, "nbv":  45, "riskStart": 3.5, "riskEnd": 3.3},
        {"name": "Restaurants",   "lob": "sbl", "start": 120, "outflow": -30, "aq":  -8, "nbv":  15, "riskStart": 5.0, "riskEnd": 5.3},
        {"name": "Multifamily A", "lob": "mfl", "start": 620, "outflow": -40, "aq":   3, "nbv":  80, "riskStart": 2.5, "riskEnd": 2.4},
        {"name": "Multifamily B", "lob": "mfl", "start": 380, "outflow": -35, "aq":  -5, "nbv":  50, "riskStart": 3.2, "riskEnd": 3.3},
    ],
    "migration": [
        [680, 45, 10, 2, 0],
        [20, 320, 38, 5, 1],
        [5,  15, 180, 25, 8],
        [0,   2,  10, 95, 18],
        [0,   0,   1,  5, 48],
    ],
    "ratingLabels": RATING_LABELS,
    # `quarters` is overwritten by _with_period() at serve time.
    "timeseries": {
        "Healthcare":    {"balance": [720,740,760,790,800,810,820,853], "concentration": [14.2,14.1,14.3,14.5,14.4,14.6,14.5,14.7], "aq": [3.0,3.0,3.1,3.1,3.2,3.2,3.2,3.4]},
        "Technology":    {"balance": [480,510,540,570,590,620,650,728], "concentration": [9.5,9.7,10.1,10.5,10.6,11.2,11.5,12.6], "aq": [2.9,2.9,2.8,2.8,2.7,2.8,2.8,2.6]},
        "Manufacturing": {"balance": [560,555,550,548,545,542,540,503], "concentration": [11.1,10.6,10.3,10.1,9.8,9.8,9.6,8.7],   "aq": [3.8,3.9,3.9,4.0,4.0,4.1,4.1,4.4]},
        "Office":        {"balance": [880,860,840,820,810,795,780,670], "concentration": [17.4,16.4,15.7,15.1,14.6,14.3,13.8,11.6],"aq": [4.5,4.6,4.8,4.9,5.0,5.1,5.2,5.6]},
        "Industrial":    {"balance": [400,420,440,460,480,500,520,590], "concentration": [7.9,8.0,8.2,8.5,8.6,9.0,9.2,10.2],      "aq": [3.2,3.1,3.1,3.0,3.0,3.0,3.0,2.9]},
        "Multifamily A": {"balance": [500,520,540,560,580,600,620,663], "concentration": [9.9,9.9,10.1,10.3,10.4,10.8,11.0,11.5], "aq": [2.6,2.6,2.5,2.5,2.5,2.5,2.5,2.4]},
    },
    "obligors": {
        "Healthcare": [
            {"name":"Mercy Health Partners","bal":145,"risk":"Pass","flow":"static"},{"name":"Pinnacle Medical Group","bal":112,"risk":"Pass","flow":"static"},
            {"name":"CareFirst Regional Hospital","bal":98,"risk":"Watch","flow":"aq-up"},{"name":"NovaCare Rehabilitation","bal":88,"risk":"Pass","flow":"nbv"},
            {"name":"Tri-County Health Systems","bal":82,"risk":"Pass","flow":"static"},{"name":"Summit Behavioral Health","bal":75,"risk":"Pass","flow":"nbv"},
            {"name":"Heartland Senior Living","bal":65,"risk":"Watch","flow":"aq-up"},{"name":"Pacific Dental Partners","bal":52,"risk":"Pass","flow":"nbv"},
            {"name":"Apex Urgent Care Holdings","bal":42,"risk":"Substandard","flow":"aq-up"},{"name":"Lakeview Specialty Clinic","bal":38,"risk":"Pass","flow":"outflow"},
            {"name":"Genesis Therapeutics Inc","bal":35,"risk":"Pass","flow":"outflow"},{"name":"Prairie Health Network","bal":22,"risk":"Pass","flow":"outflow"},
        ],
        "Technology": [
            {"name":"Nexus Cloud Solutions","bal":120,"risk":"Pass","flow":"nbv"},{"name":"Veristream Data Corp","bal":105,"risk":"Pass","flow":"static"},
            {"name":"Quantum Edge AI","bal":95,"risk":"Pass","flow":"nbv"},{"name":"CyberVault Security","bal":88,"risk":"Pass","flow":"static"},
            {"name":"DataPulse Analytics","bal":78,"risk":"Pass","flow":"static"},{"name":"TechBridge Platforms","bal":65,"risk":"Pass","flow":"aq-down"},
            {"name":"CloudForge Inc","bal":55,"risk":"Pass","flow":"static"},{"name":"Sentinel IoT Systems","bal":48,"risk":"Pass","flow":"nbv"},
            {"name":"AeroCode Software","bal":40,"risk":"Pass","flow":"outflow"},{"name":"Brightpath DevOps","bal":34,"risk":"Pass","flow":"static"},
        ],
        "Manufacturing": [
            {"name":"Ironworks Precision Mfg","bal":95,"risk":"Watch","flow":"aq-up"},{"name":"Cascade Metals Group","bal":88,"risk":"Pass","flow":"static"},
            {"name":"Heartland Plastics Inc","bal":72,"risk":"Substandard","flow":"aq-up"},{"name":"Summit Tooling Corp","bal":65,"risk":"Pass","flow":"static"},
            {"name":"Great Lakes Fabrication","bal":55,"risk":"Watch","flow":"aq-up"},{"name":"Atlas Components LLC","bal":48,"risk":"Pass","flow":"nbv"},
            {"name":"Pioneer Industrial","bal":42,"risk":"Pass","flow":"outflow"},{"name":"Midwest Stamping Co","bal":38,"risk":"Pass","flow":"outflow"},
            {"name":"Precision CNC Holdings","bal":20,"risk":"Pass","flow":"outflow"},{"name":"Ridgeline Assembly","bal":17,"risk":"Pass","flow":"nbv"},
        ],
        "Retail Trade": [
            {"name":"Grandview Retail Partners","bal":78,"risk":"Watch","flow":"aq-up"},{"name":"Sterling Home Furnishings","bal":65,"risk":"Substandard","flow":"aq-up"},
            {"name":"BrightMart Holdings","bal":52,"risk":"Pass","flow":"outflow"},{"name":"Northern Outlet Group","bal":48,"risk":"Watch","flow":"static"},
            {"name":"Riverdale Auto Parts","bal":42,"risk":"Pass","flow":"static"},{"name":"Peak Sporting Goods","bal":35,"risk":"Pass","flow":"outflow"},
            {"name":"Harbor General Store","bal":30,"risk":"Pass","flow":"nbv"},{"name":"Main Street Brands","bal":28,"risk":"Pass","flow":"outflow"},
            {"name":"Cornerstone Apparel","bal":22,"risk":"Pass","flow":"static"},{"name":"Elm Street Grocers","bal":10,"risk":"Pass","flow":"static"},
        ],
        "Office": [
            {"name":"Metro Tower Partners","bal":155,"risk":"Substandard","flow":"aq-up"},{"name":"Civic Center Properties","bal":128,"risk":"Watch","flow":"aq-up"},
            {"name":"Lakefront Office REIT","bal":110,"risk":"Watch","flow":"static"},{"name":"Cornerstone Business Park","bal":95,"risk":"Pass","flow":"outflow"},
            {"name":"Gateway Tower Holdings","bal":82,"risk":"Substandard","flow":"aq-up"},{"name":"Meridian Plaza LLC","bal":68,"risk":"Pass","flow":"static"},
            {"name":"Harbor View Office","bal":55,"risk":"Pass","flow":"outflow"},{"name":"Summit Ridge Campus","bal":45,"risk":"Pass","flow":"nbv"},
            {"name":"Crossroads Commercial","bal":22,"risk":"Pass","flow":"outflow"},{"name":"Innovation Hub Realty","bal":20,"risk":"Pass","flow":"static"},
        ],
        "Industrial": [
            {"name":"Great Lakes Logistics Park","bal":110,"risk":"Pass","flow":"nbv"},{"name":"Midwest Distribution Hub","bal":95,"risk":"Pass","flow":"static"},
            {"name":"Central Corridor Warehousing","bal":82,"risk":"Pass","flow":"nbv"},{"name":"Buckeye Flex Space","bal":68,"risk":"Pass","flow":"static"},
            {"name":"Pinnacle Cold Storage","bal":62,"risk":"Pass","flow":"aq-down"},{"name":"Northern Industrial REIT","bal":55,"risk":"Pass","flow":"static"},
            {"name":"CrossDock Partners","bal":48,"risk":"Pass","flow":"nbv"},{"name":"Heartland Last Mile","bal":40,"risk":"Pass","flow":"outflow"},
            {"name":"Summit Fulfillment","bal":30,"risk":"Pass","flow":"static"},
        ],
        "Retail CRE": [
            {"name":"Towne Centre Mall LP","bal":72,"risk":"Substandard","flow":"aq-up"},{"name":"Heritage Shopping Plaza","bal":58,"risk":"Watch","flow":"static"},
            {"name":"Crossroads Retail REIT","bal":52,"risk":"Pass","flow":"outflow"},{"name":"Maple Grove Strip Center","bal":45,"risk":"Pass","flow":"static"},
            {"name":"Lakeshore Marketplace","bal":38,"risk":"Pass","flow":"nbv"},{"name":"Eastgate Commons","bal":35,"risk":"Watch","flow":"aq-up"},
            {"name":"Valley View Retail","bal":22,"risk":"Pass","flow":"outflow"},{"name":"Sunridge Shops","bal":18,"risk":"Pass","flow":"static"},
        ],
        "Hospitality": [
            {"name":"Lakeshore Resort Group","bal":65,"risk":"Pass","flow":"static"},{"name":"Heritage Inn Collection","bal":55,"risk":"Watch","flow":"aq-down"},
            {"name":"Metro Select Hotels","bal":48,"risk":"Pass","flow":"nbv"},{"name":"Cascade Lodge Partners","bal":42,"risk":"Pass","flow":"static"},
            {"name":"Riverfront Hospitality","bal":38,"risk":"Pass","flow":"outflow"},{"name":"Bayview Conference Center","bal":25,"risk":"Pass","flow":"nbv"},
            {"name":"Summit Stay Hotels","bal":17,"risk":"Pass","flow":"outflow"},
        ],
        "Prof Services": [
            {"name":"Meridian Law Partners","bal":48,"risk":"Pass","flow":"nbv"},{"name":"Cornerstone CPA Group","bal":42,"risk":"Pass","flow":"static"},
            {"name":"Summit Advisory LLC","bal":35,"risk":"Pass","flow":"nbv"},{"name":"Lakeview Engineering","bal":28,"risk":"Pass","flow":"static"},
            {"name":"Brightpath Consulting","bal":22,"risk":"Pass","flow":"outflow"},{"name":"Apex Marketing Group","bal":15,"risk":"Watch","flow":"aq-up"},
        ],
        "Restaurants": [
            {"name":"Great Lakes Restaurant Grp","bal":32,"risk":"Substandard","flow":"aq-up"},{"name":"Metro Dining Holdings","bal":25,"risk":"Watch","flow":"static"},
            {"name":"Fireside Grill Concepts","bal":20,"risk":"Pass","flow":"outflow"},{"name":"Harbor Fresh Inc","bal":18,"risk":"Pass","flow":"nbv"},
            {"name":"Cornerstone Catering","bal":15,"risk":"Watch","flow":"aq-up"},{"name":"Sunrise Bakery Chain","bal":10,"risk":"Pass","flow":"outflow"},
        ],
        "Multifamily A": [
            {"name":"Parkview Apartments REIT","bal":135,"risk":"Pass","flow":"static"},{"name":"Metro Living Partners","bal":115,"risk":"Pass","flow":"nbv"},
            {"name":"Lakewood Residential","bal":98,"risk":"Pass","flow":"static"},{"name":"Summit View Apartments","bal":85,"risk":"Pass","flow":"nbv"},
            {"name":"Heritage Garden Homes","bal":72,"risk":"Pass","flow":"aq-down"},{"name":"Crossroads Multi-Family","bal":62,"risk":"Pass","flow":"static"},
            {"name":"Riverside Community LP","bal":48,"risk":"Pass","flow":"outflow"},{"name":"Northgate Residential","bal":35,"risk":"Pass","flow":"nbv"},
            {"name":"Bayview Living Trust","bal":13,"risk":"Pass","flow":"static"},
        ],
        "Multifamily B": [
            {"name":"Eastside Housing Group","bal":85,"risk":"Pass","flow":"static"},{"name":"Willowbrook Apartments","bal":72,"risk":"Pass","flow":"nbv"},
            {"name":"Gateway Residences","bal":58,"risk":"Watch","flow":"aq-up"},{"name":"Central Park Estates","bal":52,"risk":"Pass","flow":"static"},
            {"name":"Cedar Grove Living","bal":45,"risk":"Pass","flow":"nbv"},{"name":"Hilltop Apartment Group","bal":38,"risk":"Pass","flow":"outflow"},
            {"name":"Oakmont Housing LP","bal":30,"risk":"Pass","flow":"outflow"},
        ],
    },
}


SAMPLE_SANKEY: Dict[str, Any] = {
    "migration": {
        "all": {"matrix": [[3200,180,42,8,2],[85,620,95,22,5],[15,65,410,55,18],[2,8,35,185,32],[0,1,3,12,88]]},
        "cre": {"matrix": [[1280,85,22,4,1],[35,260,45,10,2],[6,28,175,25,8],[1,3,15,82,15],[0,0,1,5,38]]},
        "ci":  {"matrix": [[1120,55,12,2,1],[30,210,30,8,2],[5,22,140,18,6],[1,3,12,62,10],[0,1,1,4,30]]},
        "sbl": {"matrix": [[420,22,5,1,0],[12,85,12,2,1],[2,8,52,8,3],[0,1,5,24,4],[0,0,1,2,12]]},
        "mfl": {"matrix": [[380,18,3,1,0],[8,65,8,2,0],[2,7,43,4,1],[0,1,3,17,3],[0,0,0,1,8]]},
    },
}


SAMPLE_SCATTER: Dict[str, Any] = {
    "segments": [
        {"name":"Healthcare",   "lob":"ci",  "exposure":853, "risk":3.4, "spread":285},
        {"name":"Technology",   "lob":"ci",  "exposure":728, "risk":2.6, "spread":225},
        {"name":"Manufacturing","lob":"ci",  "exposure":503, "risk":4.4, "spread":340},
        {"name":"Retail Trade", "lob":"ci",  "exposure":337, "risk":4.8, "spread":380},
        {"name":"Office",       "lob":"cre", "exposure":670, "risk":5.6, "spread":420},
        {"name":"Industrial",   "lob":"cre", "exposure":590, "risk":2.9, "spread":210},
        {"name":"Retail CRE",   "lob":"cre", "exposure":290, "risk":5.1, "spread":395},
        {"name":"Hospitality",  "lob":"cre", "exposure":292, "risk":3.8, "spread":310},
        {"name":"Prof Services","lob":"sbl", "exposure":202, "risk":3.3, "spread":265},
        {"name":"Restaurants",  "lob":"sbl", "exposure":97,  "risk":5.3, "spread":435},
        {"name":"Multifamily A","lob":"mfl", "exposure":663, "risk":2.4, "spread":185},
        {"name":"Multifamily B","lob":"mfl", "exposure":390, "risk":3.3, "spread":240},
    ],
}


SAMPLE_GEO: Dict[str, Any] = {
    "states": {
        "39":{"name":"Ohio","abbr":"OH","exposure":820,"obligors":95,"risk":3.4,"change":2.1,"region":"Midwest"},
        "36":{"name":"New York","abbr":"NY","exposure":680,"obligors":72,"risk":3.8,"change":-1.2,"region":"Northeast"},
        "12":{"name":"Florida","abbr":"FL","exposure":590,"obligors":65,"risk":4.1,"change":3.5,"region":"Southeast"},
        "48":{"name":"Texas","abbr":"TX","exposure":520,"obligors":58,"risk":3.6,"change":1.8,"region":"West"},
        "42":{"name":"Pennsylvania","abbr":"PA","exposure":485,"obligors":54,"risk":3.2,"change":0.5,"region":"Northeast"},
        "06":{"name":"California","abbr":"CA","exposure":460,"obligors":48,"risk":3.9,"change":-0.8,"region":"West"},
        "17":{"name":"Illinois","abbr":"IL","exposure":380,"obligors":42,"risk":3.5,"change":1.2,"region":"Midwest"},
        "26":{"name":"Michigan","abbr":"MI","exposure":340,"obligors":38,"risk":3.7,"change":-0.5,"region":"Midwest"},
        "13":{"name":"Georgia","abbr":"GA","exposure":310,"obligors":35,"risk":3.3,"change":2.8,"region":"Southeast"},
        "37":{"name":"North Carolina","abbr":"NC","exposure":285,"obligors":32,"risk":3.1,"change":1.5,"region":"Southeast"},
        "34":{"name":"New Jersey","abbr":"NJ","exposure":265,"obligors":30,"risk":3.6,"change":0.2,"region":"Northeast"},
        "51":{"name":"Virginia","abbr":"VA","exposure":240,"obligors":28,"risk":3.0,"change":1.0,"region":"Southeast"},
        "25":{"name":"Massachusetts","abbr":"MA","exposure":220,"obligors":25,"risk":3.2,"change":-0.3,"region":"Northeast"},
        "18":{"name":"Indiana","abbr":"IN","exposure":195,"obligors":22,"risk":3.4,"change":0.8,"region":"Midwest"},
        "55":{"name":"Wisconsin","abbr":"WI","exposure":175,"obligors":20,"risk":3.1,"change":0.6,"region":"Midwest"},
        "27":{"name":"Minnesota","abbr":"MN","exposure":165,"obligors":18,"risk":2.9,"change":1.1,"region":"Midwest"},
        "47":{"name":"Tennessee","abbr":"TN","exposure":155,"obligors":18,"risk":3.5,"change":2.0,"region":"Southeast"},
        "29":{"name":"Missouri","abbr":"MO","exposure":140,"obligors":16,"risk":3.3,"change":0.4,"region":"Midwest"},
        "24":{"name":"Maryland","abbr":"MD","exposure":130,"obligors":15,"risk":3.1,"change":0.7,"region":"Northeast"},
        "08":{"name":"Colorado","abbr":"CO","exposure":120,"obligors":14,"risk":3.0,"change":1.9,"region":"West"},
        "04":{"name":"Arizona","abbr":"AZ","exposure":110,"obligors":12,"risk":3.8,"change":2.5,"region":"West"},
        "53":{"name":"Washington","abbr":"WA","exposure":95,"obligors":11,"risk":2.8,"change":0.9,"region":"West"},
        "21":{"name":"Kentucky","abbr":"KY","exposure":85,"obligors":10,"risk":3.6,"change":-0.2,"region":"Southeast"},
        "09":{"name":"Connecticut","abbr":"CT","exposure":78,"obligors":9,"risk":3.4,"change":-1.0,"region":"Northeast"},
        "41":{"name":"Oregon","abbr":"OR","exposure":65,"obligors":8,"risk":2.9,"change":1.3,"region":"West"},
    },
}


SAMPLE_GAUGES: Dict[str, Any] = {
    "gauges": [
        {"title":"Portfolio Health Score","value":78,"max":100,"trend":"+3pts from Q4","trendDir":"up"},
        {"title":"Credit Quality Index",  "value":72,"max":100,"trend":"-1pt from Q4", "trendDir":"down"},
        {"title":"Diversification Score", "value":85,"max":100,"trend":"+2pts from Q4","trendDir":"up"},
        {"title":"Stress Resilience",     "value":68,"max":100,"trend":"+5pts from Q4","trendDir":"up"},
    ],
    "donuts": [
        {"title":"Total Portfolio",   "pct":82,"limit":8.2,"used":6.7},
        {"title":"CRE Concentration", "pct":74,"limit":3.5,"used":2.6},
        {"title":"Single Obligor",    "pct":45,"limit":0.5,"used":0.225},
        {"title":"Industry Limit",    "pct":68,"limit":1.8,"used":1.22},
        {"title":"Geographic Limit",  "pct":55,"limit":2.0,"used":1.1},
        {"title":"Watchlist Ratio",   "pct":12,"limit":0.8,"used":0.096},
    ],
    "sparklines": [
        {"title":"Portfolio Health",  "values":[68,70,72,74,73,75,75,78],"unit":""},
        {"title":"Credit Quality",    "values":[76,75,74,73,74,73,73,72],"unit":""},
        {"title":"Diversification",   "values":[80,81,82,82,83,84,84,85],"unit":""},
        {"title":"Total Utilization", "values":[75,76,78,79,80,80,81,82],"unit":"%"},
        {"title":"CRE Concentration", "values":[68,69,70,71,72,73,73,74],"unit":"%"},
        {"title":"Watchlist Ratio",   "values":[8,9,10,11,12,13,12,12],"unit":"%"},
    ],
}


SAMPLE_TREEMAP: Dict[str, Any] = {
    "portfolio": {
        "name": "Portfolio", "children": [
            {"name": "C&I", "risk": "Pass", "children": [
                {"name": "Healthcare", "risk": "Pass", "children": [
                    {"name":"Mercy Health Partners","value":145,"risk":"Pass"},{"name":"Pinnacle Medical Group","value":112,"risk":"Pass"},
                    {"name":"CareFirst Regional Hospital","value":98,"risk":"Watch"},{"name":"NovaCare Rehabilitation","value":88,"risk":"Pass"},
                    {"name":"Tri-County Health Systems","value":82,"risk":"Pass"},{"name":"Summit Behavioral Health","value":75,"risk":"Pass"},
                    {"name":"Heartland Senior Living","value":65,"risk":"Watch"},{"name":"Pacific Dental Partners","value":52,"risk":"Pass"},
                    {"name":"Apex Urgent Care Holdings","value":42,"risk":"Substandard"},{"name":"Lakeview Specialty Clinic","value":38,"risk":"Pass"},
                ]},
                {"name": "Technology", "risk": "Pass", "children": [
                    {"name":"Nexus Cloud Solutions","value":120,"risk":"Pass"},{"name":"Veristream Data Corp","value":105,"risk":"Pass"},
                    {"name":"Quantum Edge AI","value":95,"risk":"Pass"},{"name":"CyberVault Security","value":88,"risk":"Pass"},
                    {"name":"DataPulse Analytics","value":78,"risk":"Pass"},{"name":"TechBridge Platforms","value":65,"risk":"Pass"},
                    {"name":"CloudForge Inc","value":55,"risk":"Pass"},{"name":"Sentinel IoT Systems","value":48,"risk":"Pass"},
                ]},
                {"name": "Manufacturing", "risk": "Watch", "children": [
                    {"name":"Ironworks Precision Mfg","value":95,"risk":"Watch"},{"name":"Cascade Metals Group","value":88,"risk":"Pass"},
                    {"name":"Heartland Plastics Inc","value":72,"risk":"Substandard"},{"name":"Summit Tooling Corp","value":65,"risk":"Pass"},
                    {"name":"Great Lakes Fabrication","value":55,"risk":"Watch"},{"name":"Atlas Components LLC","value":48,"risk":"Pass"},
                    {"name":"Pioneer Industrial","value":42,"risk":"Pass"},{"name":"Midwest Stamping Co","value":38,"risk":"Pass"},
                ]},
                {"name": "Retail Trade", "risk": "Watch", "children": [
                    {"name":"Grandview Retail Partners","value":78,"risk":"Watch"},{"name":"Sterling Home Furnishings","value":65,"risk":"Substandard"},
                    {"name":"BrightMart Holdings","value":52,"risk":"Pass"},{"name":"Northern Outlet Group","value":48,"risk":"Watch"},
                    {"name":"Riverdale Auto Parts","value":42,"risk":"Pass"},{"name":"Peak Sporting Goods","value":35,"risk":"Pass"},
                    {"name":"Harbor General Store","value":30,"risk":"Pass"},{"name":"Main Street Brands","value":28,"risk":"Pass"},
                ]},
            ]},
            {"name": "CRE", "risk": "Watch", "children": [
                {"name": "Office", "risk": "Substandard", "children": [
                    {"name":"Metro Tower Partners","value":155,"risk":"Substandard"},{"name":"Civic Center Properties","value":128,"risk":"Watch"},
                    {"name":"Lakefront Office REIT","value":110,"risk":"Watch"},{"name":"Cornerstone Business Park","value":95,"risk":"Pass"},
                    {"name":"Gateway Tower Holdings","value":82,"risk":"Substandard"},{"name":"Meridian Plaza LLC","value":68,"risk":"Pass"},
                    {"name":"Harbor View Office","value":55,"risk":"Pass"},{"name":"Summit Ridge Campus","value":45,"risk":"Pass"},
                ]},
                {"name": "Industrial", "risk": "Pass", "children": [
                    {"name":"Great Lakes Logistics Park","value":110,"risk":"Pass"},{"name":"Midwest Distribution Hub","value":95,"risk":"Pass"},
                    {"name":"Central Corridor Warehousing","value":82,"risk":"Pass"},{"name":"Buckeye Flex Space","value":68,"risk":"Pass"},
                    {"name":"Pinnacle Cold Storage","value":62,"risk":"Pass"},{"name":"Northern Industrial REIT","value":55,"risk":"Pass"},
                    {"name":"CrossDock Partners","value":48,"risk":"Pass"},
                ]},
                {"name": "Retail CRE", "risk": "Watch", "children": [
                    {"name":"Towne Centre Mall LP","value":72,"risk":"Substandard"},{"name":"Heritage Shopping Plaza","value":58,"risk":"Watch"},
                    {"name":"Crossroads Retail REIT","value":52,"risk":"Pass"},{"name":"Maple Grove Strip Center","value":45,"risk":"Pass"},
                    {"name":"Lakeshore Marketplace","value":38,"risk":"Pass"},{"name":"Eastgate Commons","value":35,"risk":"Watch"},
                ]},
                {"name": "Hospitality", "risk": "Pass", "children": [
                    {"name":"Lakeshore Resort Group","value":65,"risk":"Pass"},{"name":"Heritage Inn Collection","value":55,"risk":"Watch"},
                    {"name":"Metro Select Hotels","value":48,"risk":"Pass"},{"name":"Cascade Lodge Partners","value":42,"risk":"Pass"},
                    {"name":"Riverfront Hospitality","value":38,"risk":"Pass"},{"name":"Bayview Conference Center","value":25,"risk":"Pass"},
                ]},
            ]},
            {"name": "SBL", "risk": "Pass", "children": [
                {"name": "Prof Services", "risk": "Pass", "children": [
                    {"name":"Meridian Law Partners","value":48,"risk":"Pass"},{"name":"Cornerstone CPA Group","value":42,"risk":"Pass"},
                    {"name":"Summit Advisory LLC","value":35,"risk":"Pass"},{"name":"Lakeview Engineering","value":28,"risk":"Pass"},
                    {"name":"Brightpath Consulting","value":22,"risk":"Pass"},{"name":"Apex Marketing Group","value":15,"risk":"Watch"},
                ]},
                {"name": "Restaurants", "risk": "Watch", "children": [
                    {"name":"Great Lakes Restaurant Grp","value":32,"risk":"Substandard"},{"name":"Metro Dining Holdings","value":25,"risk":"Watch"},
                    {"name":"Fireside Grill Concepts","value":20,"risk":"Pass"},{"name":"Harbor Fresh Inc","value":18,"risk":"Pass"},
                    {"name":"Cornerstone Catering","value":15,"risk":"Watch"},{"name":"Sunrise Bakery Chain","value":10,"risk":"Pass"},
                ]},
            ]},
            {"name": "Multifamily", "risk": "Pass", "children": [
                {"name": "Multifamily A", "risk": "Pass", "children": [
                    {"name":"Parkview Apartments REIT","value":135,"risk":"Pass"},{"name":"Metro Living Partners","value":115,"risk":"Pass"},
                    {"name":"Lakewood Residential","value":98,"risk":"Pass"},{"name":"Summit View Apartments","value":85,"risk":"Pass"},
                    {"name":"Heritage Garden Homes","value":72,"risk":"Pass"},{"name":"Crossroads Multi-Family","value":62,"risk":"Pass"},
                    {"name":"Riverside Community LP","value":48,"risk":"Pass"},{"name":"Northgate Residential","value":35,"risk":"Pass"},
                ]},
                {"name": "Multifamily B", "risk": "Pass", "children": [
                    {"name":"Eastside Housing Group","value":85,"risk":"Pass"},{"name":"Willowbrook Apartments","value":72,"risk":"Pass"},
                    {"name":"Gateway Residences","value":58,"risk":"Watch"},{"name":"Central Park Estates","value":52,"risk":"Pass"},
                    {"name":"Cedar Grove Living","value":45,"risk":"Pass"},{"name":"Hilltop Apartment Group","value":38,"risk":"Pass"},
                    {"name":"Oakmont Housing LP","value":30,"risk":"Pass"},
                ]},
            ]},
        ],
    },
}


# ----------------------------------------------------------------------------
# Payload builders
# ----------------------------------------------------------------------------


def _have(sections: Optional[Dict[str, pd.DataFrame]], *names: str) -> bool:
    return bool(sections) and all(n in sections and not sections[n].empty for n in names)


def portfolio_flow_payload(sections: Optional[Dict[str, pd.DataFrame]] = None) -> Dict[str, Any]:
    """Required sections: industries, migration, timeseries, obligors.

    Shapes (each row is one dict in the JSON output):
      industries:  industry, lob, start, outflow, aq, nbv, risk_start, risk_end
      migration:   from_rating, to_rating, balance_m
      timeseries:  industry, quarter_idx (0..7), balance, concentration, aq
      obligors:    industry, name, balance, risk, flow
    """
    if not _have(sections, "industries", "migration", "timeseries", "obligors"):
        return _with_period(SAMPLE_PORTFOLIO_FLOW)

    ind_df = sections["industries"]
    industries = [
        {
            "name": r["industry"], "lob": r["lob"],
            "start": float(r["start"]), "outflow": float(r["outflow"]),
            "aq": float(r["aq"]), "nbv": float(r["nbv"]),
            "riskStart": float(r["risk_start"]), "riskEnd": float(r["risk_end"]),
        }
        for _, r in ind_df.iterrows()
    ]

    mig_df = sections["migration"]
    matrix = mig_df.pivot(index="from_rating", columns="to_rating", values="balance_m") \
        .reindex(index=RATING_LABELS, columns=RATING_LABELS).fillna(0).values.tolist()

    ts_df = sections["timeseries"].sort_values(["industry", "quarter_idx"])
    timeseries: Dict[str, Dict[str, list]] = {}
    for industry, g in ts_df.groupby("industry"):
        timeseries[industry] = {
            "balance": g["balance"].astype(float).tolist(),
            "concentration": g["concentration"].astype(float).tolist(),
            "aq": g["aq"].astype(float).tolist(),
        }

    ob_df = sections["obligors"]
    obligors: Dict[str, list] = {}
    for industry, g in ob_df.groupby("industry"):
        obligors[industry] = [
            {"name": r["name"], "bal": float(r["balance"]), "risk": r["risk"], "flow": r["flow"]}
            for _, r in g.iterrows()
        ]

    return _with_period({
        "industries": industries,
        "migration": matrix,
        "ratingLabels": RATING_LABELS,
        "timeseries": timeseries,
        "obligors": obligors,
    })


def sankey_payload(sections: Optional[Dict[str, pd.DataFrame]] = None) -> Dict[str, Any]:
    """Required sections: migration.

    Shape: lob ('all'|'cre'|'ci'|'sbl'|'mfl'), from_rating, to_rating, balance_m.
    Reshaped into ``{migration: {<lob>: {matrix: [[..5x5..]]}}}``.
    """
    if not _have(sections, "migration"):
        return _with_period(SAMPLE_SANKEY)
    df = sections["migration"]
    out: Dict[str, Dict[str, list]] = {}
    for lob, g in df.groupby("lob"):
        mat = g.pivot(index="from_rating", columns="to_rating", values="balance_m") \
            .reindex(index=RATING_LABELS, columns=RATING_LABELS).fillna(0).values.tolist()
        out[lob] = {"matrix": mat}
    return _with_period({"migration": out})


def scatter_payload(sections: Optional[Dict[str, pd.DataFrame]] = None) -> Dict[str, Any]:
    """Required sections: segments.

    Shape: name (or segment), lob, exposure, risk, spread.
    """
    if not _have(sections, "segments"):
        return _with_period(SAMPLE_SCATTER)
    df = sections["segments"].rename(columns={"segment": "name"})
    return _with_period({"segments": df[["name", "lob", "exposure", "risk", "spread"]]
            .to_dict(orient="records")})


def geo_payload(sections: Optional[Dict[str, pd.DataFrame]] = None) -> Dict[str, Any]:
    """Required sections: states.

    Shape: fips, name (or state), abbr, exposure, obligors, risk, change, region.
    Reshaped into ``{states: {<fips>: {...}}}``.
    """
    if not _have(sections, "states"):
        return _with_period(SAMPLE_GEO)
    df = sections["states"].rename(columns={"state": "name"})
    states: Dict[str, Dict[str, Any]] = {}
    for _, r in df.iterrows():
        states[str(r["fips"]).zfill(2)] = {
            "name": r["name"], "abbr": r["abbr"],
            "exposure": float(r["exposure"]), "obligors": int(r["obligors"]),
            "risk": float(r["risk"]), "change": float(r["change"]),
            "region": r["region"],
        }
    return _with_period({"states": states})


def gauges_payload(sections: Optional[Dict[str, pd.DataFrame]] = None) -> Dict[str, Any]:
    """Required sections: gauges, donuts, sparklines.

    Shapes:
      gauges:     title, value, max, trend, trend_dir
      donuts:     title, pct, limit_b, used_b
      sparklines: title, unit, value_array (REPEATED FLOAT64) OR title, idx, value
    """
    if not _have(sections, "gauges", "donuts", "sparklines"):
        return _with_period(SAMPLE_GAUGES)

    g_df = sections["gauges"]
    gauges = [
        {"title": r["title"], "value": float(r["value"]), "max": float(r["max"]),
         "trend": r["trend"], "trendDir": r["trend_dir"]}
        for _, r in g_df.iterrows()
    ]

    d_df = sections["donuts"]
    donuts = [
        {"title": r["title"], "pct": float(r["pct"]),
         "limit": float(r["limit_b"]), "used": float(r["used_b"])}
        for _, r in d_df.iterrows()
    ]

    s_df = sections["sparklines"]
    if "value_array" in s_df.columns:
        sparklines = [
            {"title": r["title"], "unit": r.get("unit", ""), "values": list(r["value_array"])}
            for _, r in s_df.iterrows()
        ]
    else:
        sparklines = []
        for title, g in s_df.sort_values(["title", "idx"]).groupby("title"):
            unit = g["unit"].iloc[0] if "unit" in g.columns else ""
            sparklines.append({"title": title, "unit": unit,
                              "values": g["value"].astype(float).tolist()})

    return _with_period({"gauges": gauges, "donuts": donuts, "sparklines": sparklines})


def treemap_payload(sections: Optional[Dict[str, pd.DataFrame]] = None) -> Dict[str, Any]:
    """Required sections: obligors.

    Shape: lob, industry, name, value, risk. We assemble a 3-level
    hierarchy LOB -> Industry -> Obligor on the fly.
    """
    if not _have(sections, "obligors"):
        return _with_period(SAMPLE_TREEMAP)

    df = sections["obligors"]
    # Determine rolled-up risk for parent nodes — pick the bucket with
    # the largest balance share (matches the HTML's `getAvgRisk`).
    def rollup_risk(group: pd.DataFrame) -> str:
        agg = group.groupby("risk")["value"].sum().sort_values(ascending=False)
        return agg.index[0] if len(agg) else "Pass"

    portfolio = {"name": "Portfolio", "children": []}
    for lob, lob_df in df.groupby("lob", sort=False):
        lob_node = {"name": lob, "risk": rollup_risk(lob_df), "children": []}
        for industry, ind_df in lob_df.groupby("industry", sort=False):
            ind_node = {"name": industry, "risk": rollup_risk(ind_df), "children": [
                {"name": r["name"], "value": float(r["value"]), "risk": r["risk"]}
                for _, r in ind_df.iterrows()
            ]}
            lob_node["children"].append(ind_node)
        portfolio["children"].append(lob_node)
    return _with_period({"portfolio": portfolio})
