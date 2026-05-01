// Canned response — simulates the LLM JSON output for a 10-Q query
window.MOCK_RESPONSE = {
  summary: {
    overallToneAssessment:
      "Cautiously optimistic with hedged language around macro headwinds. Management emphasizes operational discipline and margin expansion while acknowledging softening enterprise demand and FX volatility. Tone is more measured than the prior quarter, with notable de-emphasis of forward growth claims.",
    toneScore: 0.34, // -1 negative, +1 positive
    confidence: 0.87,
    keyRiskSignals: [
      {
        label: "Enterprise sales cycle elongation",
        severity: "high",
        detail:
          "References to 'extended deliberation' and 'larger deal scrutiny' appear 7 times, up from 2 last quarter.",
        citation: 1,
      },
      {
        label: "FX exposure widening",
        severity: "medium",
        detail:
          "USD strength cited as a 240bps headwind to reported revenue, with limited hedging coverage on EMEA balance.",
        citation: 2,
      },
      {
        label: "Customer concentration drift",
        severity: "medium",
        detail:
          "Top-10 customers now 31% of ARR vs 27% YoY; renewal timing discussed defensively.",
        citation: 3,
      },
      {
        label: "Inventory position elevated",
        severity: "low",
        detail:
          "Days-on-hand up 11% sequentially; described as 'strategic positioning' but inconsistent with prior commentary.",
        citation: 4,
      },
    ],
    notableChangesFromPriorQuarter: {
      "Forward guidance language": {
        direction: "down",
        delta: "−18%",
        detail: "Use of confident forward verbs ('will', 'expect to') down materially.",
      },
      "Hedging qualifiers": {
        direction: "up",
        delta: "+42%",
        detail: "Phrases like 'subject to', 'depending on', 'if conditions persist' rose sharply.",
      },
      "Margin commentary": {
        direction: "up",
        delta: "+9%",
        detail: "More confident framing around gross margin trajectory and cost discipline.",
      },
      "Competitive positioning": {
        direction: "flat",
        delta: "±0%",
        detail: "Stable share of voice; no new named competitors introduced.",
      },
      "Capital allocation tone": {
        direction: "down",
        delta: "−6%",
        detail: "Buyback enthusiasm softened; pivoted toward 'optionality' framing.",
      },
    },
    sentimentBreakdown: {
      positive: 0.41,
      neutral: 0.38,
      negative: 0.21,
    },
    specificEvidenceCitations: [
      {
        n: 1,
        quote:
          "We are seeing extended deliberation cycles among our largest enterprise customers, particularly in regulated verticals where capital approval has tightened.",
        source: "10-Q, MD&A § 2.1",
      },
      {
        n: 2,
        quote:
          "Foreign currency translation reduced reported revenue by approximately 240 basis points in the quarter, with limited offset from our existing hedging program.",
        source: "10-Q, MD&A § 3.4",
      },
      {
        n: 3,
        quote:
          "Our top ten customers represented approximately 31% of annual recurring revenue at quarter-end, up from 27% in the prior year period.",
        source: "10-Q, Item 7A",
      },
      {
        n: 4,
        quote:
          "Inventory levels reflect strategic positioning ahead of anticipated second-half demand, though we continue to monitor sell-through carefully.",
        source: "10-Q, Notes to Financials § 5",
      },
      {
        n: 5,
        quote:
          "We remain disciplined on operating expense and continue to see margin expansion opportunity through the back half of the year.",
        source: "10-Q, Earnings Commentary",
      },
    ],
    meta: {
      ticker: "ACME",
      company: "Acme Holdings, Inc.",
      filing: "10-Q",
      period: "Q2 2026",
      filedOn: "Apr 24, 2026",
      pages: 87,
      tokensAnalyzed: 41320,
    },
  },
};

window.SUGGESTED_QUERIES = [
  { ticker: "AAPL", q: "Apple Q2 2026 10-Q tone analysis" },
  { ticker: "NVDA", q: "Nvidia Q1 2026 risk signals vs prior quarter" },
  { ticker: "TSLA", q: "Tesla Q4 2025 forward guidance shifts" },
  { ticker: "MSFT", q: "Microsoft Q3 2026 hedging language changes" },
];

window.ANALYSIS_STEPS = [
  "Locating filing in EDGAR",
  "Parsing MD&A and risk sections",
  "Tokenizing 41,320 tokens",
  "Comparing against prior quarter baseline",
  "Scoring tone and risk signals",
  "Extracting evidence citations",
];
