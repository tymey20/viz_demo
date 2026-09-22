"""House style in code. STYLE.md is the human/agent-readable version; keep them in sync."""
from pptx.util import Inches, Pt

FONT = "Calibri"
TEXT = "1F2933"
MUTED = "5F6B7A"
WHITE = "FFFFFF"
SERIES = ["1F4E79", "8FAADC", "C55A11", "7F7F7F", "548235", "BF9000"]
RAG = {"G": "2E7D32", "A": "F9A825", "R": "C62828"}
RAG_TEXT = {"G": WHITE, "A": TEXT, "R": WHITE}

SLIDE_W, SLIDE_H = Inches(13.333), Inches(7.5)
TITLE_PT, BODY_PT, TABLE_PT, LABEL_PT, FOOT_PT = 30, 14, 12, 10, 9

# Layout names in the branded master; index fallbacks for the default master.
MASTER_TITLE = ("Title Slide", 0)
MASTER_CONTENT = ("Title Only", 5)

_L, _T, _W, _H = Inches(0.6), Inches(1.4), Inches(12.1), Inches(5.4)
_GAP = Inches(0.4)
_HALF = int((_W - _GAP) / 2)
LAYOUTS = {
    "single":     [(_L, _T, _W, _H)],
    "two_up":     [(_L, _T, _HALF, _H), (_L + _HALF + _GAP, _T, _HALF, _H)],
    "commentary": [(_L, _T, _W, _H)],
}
FOOTER = (Inches(0.6), Inches(7.0), Inches(12.1), Inches(0.3))
