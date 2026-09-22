import pytest

from reportkit import commentary
from reportkit.spec import Dataset
from reportkit.thresholds import Threshold, rag


def test_only_governed_marts():
    with pytest.raises(ValueError):
        Dataset(mart="raw_loans")
    with pytest.raises(ValueError):
        Dataset(mart="rpt_x; drop table y")


def test_only_simple_filters():
    with pytest.raises(ValueError):
        Dataset(mart="rpt_x", filters={"a": {"like": "%foo%"}})
    with pytest.raises(ValueError):
        Dataset(mart="rpt_x", filters={"a or 1=1": 1})


def test_rag_with_segment_override():
    t = Threshold(direction="lower_better", green=0.10, amber=0.25, by={"segment": {"CRE": {"green": 0.15}}})
    assert rag(0.12, t, {"segment": "Other"}) == "A"
    assert rag(0.12, t, {"segment": "CRE"}) == "G"
    assert rag(0.2501, t, {"segment": "CRE"}) == "R"


def test_commentary_grounding():
    facts = [{"value": "0.271", "green": "0.100", "amber": "0.250"}]
    assert commentary.ungrounded(["PSI is Red at 0.271 vs 0.250 in Q2 2026"], facts) == []
    bad = commentary.ungrounded(["PSI is Red at 0.271, up 0.04 from last quarter"], facts)
    assert bad and "0.04" in bad[0]
