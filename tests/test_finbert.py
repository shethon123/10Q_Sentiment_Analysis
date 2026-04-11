from finbert import compute_overall_sentiment


def test_compute_overall_sentiment_negative_majority():
    data = {
        "summary": {
            "keyRiskSignals": [
                {"risk": "Operational Costs", "sentiment": "negative", "score": 0.9},
                {"risk": "Market Competition", "sentiment": "negative", "score": 0.8},
            ],
            "notableChangesFromPriorQuarter": {
                "revenueGrowth": {"text": "+20% YoY", "sentiment": "positive", "score": 0.85}
            },
            "specificEvidenceCitations": [
                {"text": "Operating costs rose.", "sentiment": "negative", "score": 0.75}
            ],
        }
    }
    result = compute_overall_sentiment(data)
    assert result["label"] == "NEGATIVE"
    assert 0.0 <= result["confidence"] <= 1.0


def test_compute_overall_sentiment_positive_majority():
    data = {
        "summary": {
            "keyRiskSignals": [
                {"risk": "Low risk", "sentiment": "positive", "score": 0.9},
            ],
            "notableChangesFromPriorQuarter": {
                "revenue": {"text": "Revenue up", "sentiment": "positive", "score": 0.88}
            },
            "specificEvidenceCitations": [
                {"text": "Strong growth reported.", "sentiment": "positive", "score": 0.92}
            ],
        }
    }
    result = compute_overall_sentiment(data)
    assert result["label"] == "POSITIVE"
    assert result["confidence"] >= 0.88


def test_compute_overall_sentiment_returns_required_keys():
    data = {
        "summary": {
            "keyRiskSignals": [
                {"risk": "X", "sentiment": "neutral", "score": 0.6}
            ],
            "notableChangesFromPriorQuarter": {},
            "specificEvidenceCitations": [],
        }
    }
    result = compute_overall_sentiment(data)
    assert "label" in result
    assert "confidence" in result
    assert result["label"] in ("POSITIVE", "NEGATIVE", "NEUTRAL")
