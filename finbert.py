from transformers import pipeline

finbert = pipeline("sentiment-analysis", model="ProsusAI/finbert")

MAX_CHARS = 500


def analyze_json_output(data: dict) -> dict:
    """Enrich LLM JSON output with FinBERT sentiment labels and scores in-place."""
    for i, risk in enumerate(data["summary"]["keyRiskSignals"]):
        res = finbert(str(risk)[:MAX_CHARS])[0]
        data["summary"]["keyRiskSignals"][i] = {
            "risk": risk,
            "sentiment": res["label"],
            "score": round(res["score"], 4),
        }

    for key, value in data["summary"]["notableChangesFromPriorQuarter"].items():
        res = finbert(str(value)[:MAX_CHARS])[0]
        data["summary"]["notableChangesFromPriorQuarter"][key] = {
            "text": value,
            "sentiment": res["label"],
            "score": round(res["score"], 4),
        }

    for i, evidence in enumerate(data["summary"]["specificEvidenceCitations"]):
        res = finbert(str(evidence)[:MAX_CHARS])[0]
        data["summary"]["specificEvidenceCitations"][i] = {
            "text": evidence,
            "sentiment": res["label"],
            "score": round(res["score"], 4),
        }

    return data


def compute_overall_sentiment(data: dict) -> dict:
    """
    Aggregate per-item FinBERT scores from enriched data into a single label + confidence.
    Expects data already processed by analyze_json_output().
    """
    buckets: dict[str, list[float]] = {"positive": [], "negative": [], "neutral": []}

    for item in data["summary"].get("keyRiskSignals", []):
        label_key = item["sentiment"].lower()
        if label_key in buckets:
            buckets[label_key].append(item["score"])

    for item in data["summary"].get("notableChangesFromPriorQuarter", {}).values():
        label_key = item["sentiment"].lower()
        if label_key in buckets:
            buckets[label_key].append(item["score"])

    for item in data["summary"].get("specificEvidenceCitations", []):
        label_key = item["sentiment"].lower()
        if label_key in buckets:
            buckets[label_key].append(item["score"])

    if not any(buckets.values()):
        return {"label": "NEUTRAL", "confidence": 0.0}

    total_items = sum(len(v) for v in buckets.values())
    # Weight by proportion of items AND their confidence so a high-confidence minority
    # label cannot outrank a low-confidence majority label.
    weighted = {
        label: sum(vals) / total_items if vals else 0.0
        for label, vals in buckets.items()
    }
    overall_label = max(weighted, key=weighted.get)
    # Confidence = average FinBERT score for items in the winning label
    confidence = round(sum(buckets[overall_label]) / len(buckets[overall_label]), 4)

    return {"label": overall_label.upper(), "confidence": confidence}
