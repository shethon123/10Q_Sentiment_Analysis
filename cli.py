from runllm import chat
from finbert import analyze_json_output, compute_overall_sentiment


def display_summary(data: dict) -> None:
    """Display the LLM summary. Must be called before analyze_json_output() enriches the data."""
    summary = data.get("summary", {})
    print("\n--- LLM SUMMARY ---")
    print(f"Overall tone: {summary.get('overallToneAssessment', 'N/A')}\n")

    risks = summary.get("keyRiskSignals", [])
    if risks:
        print("Key risk signals:")
        for risk in risks:
            print(f"  • {risk}")

    changes = summary.get("notableChangesFromPriorQuarter", {})
    if changes:
        print("\nNotable changes from prior quarter:")
        for key, val in changes.items():
            print(f"  • {key}: {val}")

    citations = summary.get("specificEvidenceCitations", [])
    if citations:
        print("\nEvidence citations:")
        for citation in citations:
            print(f"  {citation}")


def display_sentiment(data: dict) -> None:
    summary = data.get("summary", {})
    overall = compute_overall_sentiment(data)

    print("\n--- SENTIMENT ANALYSIS ---")
    print(f"Overall: {overall['label']} (confidence: {overall['confidence']})\n")

    risks = summary.get("keyRiskSignals", [])
    if risks:
        print("Key Risks:")
        for item in risks:
            print(f"  • {item['risk']:<30} → {item['sentiment'].upper()} ({item['score']})")

    changes = summary.get("notableChangesFromPriorQuarter", {})
    if changes:
        print("\nNotable Changes:")
        for key, item in changes.items():
            print(f"  • {key:<30} → {item['sentiment'].upper()} ({item['score']})")

    citations = summary.get("specificEvidenceCitations", [])
    if citations:
        print("\nEvidence:")
        for i, item in enumerate(citations, 1):
            print(f"  [{i}]{'':<27} → {item['sentiment'].upper()} ({item['score']})")


def main() -> None:
    print("10-Q Sentiment Analyzer")
    print("Type 'exit' to quit.\n")

    while True:
        try:
            query = input("> ").strip()
        except (KeyboardInterrupt, EOFError):
            print("\nGoodbye.")
            break

        if query.lower() == "exit":
            break
        if not query:
            continue

        print("\n[Fetching filing...]")
        result = chat(query)

        if isinstance(result, dict):
            display_summary(result)
            try:
                enriched = analyze_json_output(result)
                display_sentiment(enriched)
            except Exception as e:
                print(f"\n[Warning: Sentiment analysis failed — {e}]")
        else:
            print(f"\n{result}")
            print("\n[Warning: Could not parse structured output — skipping sentiment analysis]")

        print()


if __name__ == "__main__":
    main()
