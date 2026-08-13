from app.agents.tools import parse_receipt_fields


def test_parse_receipt_fields():
    parsed = parse_receipt_fields("Coffee Shop\n08/11/2026\nTotal $12.45")
    assert parsed["vendor"] == "Coffee Shop"
    assert parsed["date"] == "08/11/2026"
    assert parsed["total"] == "$12.45"
