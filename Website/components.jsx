// SentinelIQ components

const { useState, useEffect, useRef, useMemo } = React;

// =====================================================================
// Brand pill (top-left, idle state)
// =====================================================================
function BrandPill() {
  return (
    <div className="siq-brand-pill-wrap">
      <div className="siq-brand-pill">
        <svg viewBox="0 0 32 32" width="22" height="22" aria-hidden="true">
          <defs>
            <linearGradient id="pillGrad" x1="0" y1="1" x2="1" y2="0">
              <stop offset="0" stopColor="#7df9ff" />
              <stop offset="1" stopColor="#3b82f6" />
            </linearGradient>
          </defs>
          {/* candlesticks */}
          <line x1="8" y1="14" x2="8" y2="24" stroke="url(#pillGrad)" strokeWidth="1.2" />
          <rect x="6" y="17" width="4" height="6" rx="0.6" fill="url(#pillGrad)" opacity="0.55" />
          <line x1="15" y1="9" x2="15" y2="22" stroke="url(#pillGrad)" strokeWidth="1.2" />
          <rect x="13" y="11" width="4" height="9" rx="0.6" fill="url(#pillGrad)" opacity="0.75" />
          <line x1="22" y1="4" x2="22" y2="20" stroke="url(#pillGrad)" strokeWidth="1.2" />
          <rect x="20" y="6" width="4" height="12" rx="0.6" fill="url(#pillGrad)" />
          {/* trend arrow */}
          <path d="M5 22 L11 18 L17 14 L25 6" stroke="url(#pillGrad)" strokeWidth="2" fill="none" strokeLinecap="round" strokeLinejoin="round" />
          <path d="M21 6 L26 5 L26 11" stroke="url(#pillGrad)" strokeWidth="2" fill="none" strokeLinecap="round" strokeLinejoin="round" />
        </svg>
        <span>SentinelIQ</span>
      </div>
    </div>);

}

// =====================================================================
// Search header (sticky)
// =====================================================================
function SearchHeader({ onSearch, isAnalyzing, hasResults, onReset, theme }) {
  const [value, setValue] = useState("");
  const [focused, setFocused] = useState(false);

  const submit = (e) => {
    e?.preventDefault();
    if (!value.trim() || isAnalyzing) return;
    onSearch(value.trim());
  };

  const examples = window.SUGGESTED_QUERIES;

  return (
    <header className={`siq-header ${hasResults ? "compact" : ""}`}>
      <div className="siq-header-inner">
        <form className={`siq-search ${focused ? "focused" : ""}`} onSubmit={submit} style={{ width: "1000px", alignItems: "flex-start", flexDirection: "row", justifyContent: "center" }}>
          <svg className="siq-search-icon" viewBox="0 0 24 24" width="16" height="16">
            <circle cx="11" cy="11" r="6.5" fill="none" stroke="currentColor" strokeWidth="1.6" />
            <path d="M16 16 L21 21" stroke="currentColor" strokeWidth="1.6" strokeLinecap="round" />
          </svg>
          <input
            type="text"
            placeholder="e.g. Apple Q2 2026 10-Q — please include the quarter and year"
            value={value}
            onChange={(e) => setValue(e.target.value)}
            onFocus={() => setFocused(true)}
            onBlur={() => setFocused(false)}
            disabled={isAnalyzing}
            aria-label="Filing query" />
          
          {hasResults &&
          <button
            type="button"
            className="siq-reset"
            onClick={() => {
              setValue("");
              onReset();
            }}
            title="New request">
            
              <svg viewBox="0 0 24 24" width="14" height="14">
                <path d="M5 5 L19 19 M19 5 L5 19" stroke="currentColor" strokeWidth="1.8" strokeLinecap="round" />
              </svg>
            </button>
          }
          <button type="submit" className="siq-go" disabled={isAnalyzing || !value.trim()}>
            {isAnalyzing ?
            <span className="siq-go-spin" /> :

            <>
                Analyze
                <svg viewBox="0 0 24 24" width="14" height="14">
                  <path d="M5 12 H19 M13 6 L19 12 L13 18" stroke="currentColor" strokeWidth="1.8" strokeLinecap="round" strokeLinejoin="round" fill="none" />
                </svg>
              </>
            }
          </button>
        </form>
      </div>

      {!hasResults && !isAnalyzing &&
      <div className="siq-examples">
          <span className="siq-examples-label">Try</span>
          {examples.map((ex) =>
        <button
          key={ex.ticker}
          className="siq-chip"
          onClick={() => {
            setValue(ex.q);
            onSearch(ex.q);
          }}>
          
              <span className="siq-chip-ticker">{ex.ticker}</span>
              <span className="siq-chip-q">{ex.q}</span>
            </button>
        )}
        </div>
      }
    </header>);

}

// =====================================================================
// Empty / hero state
// =====================================================================
function HeroState({ onSearch }) {
  const [value, setValue] = useState("");
  const [focused, setFocused] = useState(false);
  const examples = window.SUGGESTED_QUERIES;

  const submit = (e) => {
    e?.preventDefault();
    if (!value.trim()) return;
    onSearch(value.trim());
  };

  return (
    <div className="siq-hero-centered" data-screen-label="01 Search">
      <div className="siq-hero-centered-inner">
        <h1 className="siq-hero-greeting">
          <span className="siq-grad">Ready</span> when you are.
        </h1>

        <form className={`siq-search siq-search-hero ${focused ? "focused" : ""}`} onSubmit={submit} style={{ fontWeight: "600" }}>
          <button type="button" className="siq-search-plus" aria-label="Add">
            <svg viewBox="0 0 24 24" width="16" height="16">
              <path d="M12 5 V19 M5 12 H19" stroke="currentColor" strokeWidth="1.8" strokeLinecap="round" />
            </svg>
          </button>
          <input
            type="text"
            placeholder="Ask anything"
            value={value}
            onChange={(e) => setValue(e.target.value)}
            onFocus={() => setFocused(true)}
            onBlur={() => setFocused(false)}
            aria-label="Filing query" />
          
          <button type="submit" className="siq-go siq-go-hero" disabled={!value.trim()}>
            Analyze
            <svg viewBox="0 0 24 24" width="14" height="14">
              <path d="M5 12 H19 M13 6 L19 12 L13 18" stroke="currentColor" strokeWidth="1.8" strokeLinecap="round" strokeLinejoin="round" fill="none" />
            </svg>
          </button>
        </form>

        <div className="siq-hero-chips">
          {examples.map((ex) =>
          <button
            key={ex.ticker}
            className="siq-chip"
            onClick={() => {
              setValue(ex.q);
              onSearch(ex.q);
            }}>
            
              <span className="siq-chip-ticker">{ex.ticker}</span>
              <span className="siq-chip-q">{ex.q}</span>
            </button>
          )}
        </div>
      </div>
    </div>);

}

// =====================================================================
// Analyzing flow
// =====================================================================
function formatToolName(name) {
  if (!name) return "Connecting to EDGAR…";
  const labels = {
    fetch_10q_mda: "Fetching MD&A section…",
    fetch_10q_risk_factors: "Fetching risk factors…",
    fetch_10q_financials: "Fetching financial statements…",
    fetch_10q_metadata: "Fetching filing metadata…",
  };
  return labels[name] || name.replace(/_/g, " ").replace(/\b\w/g, (c) => c.toUpperCase()) + "…";
}

function AnalyzingState({ query, currentTool }) {
  return (
    <div className="siq-analyzing" data-screen-label="02 Analyzing">
      <div className="siq-analyzing-card">
        <div className="siq-analyzing-orb">
          <div className="siq-orb-ring" />
          <div className="siq-orb-ring siq-orb-ring-2" />
          <div className="siq-orb-core" />
        </div>
        <div className="siq-analyzing-title">Analyzing filing</div>
        <div className="siq-analyzing-query">"{query}"</div>
        <div className="siq-analyzing-tool">
          <span className="siq-step-spin" />
          {formatToolName(currentTool)}
        </div>
      </div>
    </div>);
}

// =====================================================================
// Results
// =====================================================================
function Results({ data, query }) {
  const s = data.summary;
  return (
    <div className="siq-results" data-screen-label="03 Results">
      <FilingHeader meta={s.meta} query={query} />

      <div className="siq-grid">
        <section className="siq-card siq-card-tone siq-span-2">
          <CardHeader
            kicker="01"
            title="Overall Tone"
            subtitle="Aggregate sentiment across MD&A and risk sections" />
          
          <ToneSpectrum score={s.toneScore} confidence={s.confidence} />
          <p className="siq-tone-text">{s.overallToneAssessment}</p>
          <SentimentBars breakdown={s.sentimentBreakdown} />
        </section>

        <section className="siq-card siq-card-meta">
          <CardHeader kicker="02" title="Filing Metadata" />
          <MetaTable meta={s.meta} />
        </section>

        <section className="siq-card siq-span-3">
          <CardHeader
            kicker="03"
            title="AI Analyst Summary"
            subtitle="Investor-facing interpretation" />
          <p className="siq-analyst-takeaway">{s.analystTakeaway}</p>
        </section>

        <section className="siq-card siq-span-3">
          <CardHeader
            kicker="04"
            title="Key Risk Signals"
            subtitle={`${s.keyRiskSignals.length} signals detected · ranked by severity`} />

          <RiskGrid risks={s.keyRiskSignals} />
        </section>

        <section className="siq-card siq-span-3">
          <CardHeader
            kicker="05"
            title="Notable Changes from Prior Quarter" />

          <DeltaTable changes={s.notableChangesFromPriorQuarter} />
        </section>

        <section className="siq-card siq-span-3">
          <CardHeader
            kicker="06"
            title="Citations"
            subtitle="Grounded evidence from the filing" />

          <Citations citations={s.specificEvidenceCitations} />
        </section>
      </div>
    </div>);

}

function FilingHeader({ meta, query }) {
  return (
    <div className="siq-filing-header">
      <div className="siq-filing-left">
        <div className="siq-ticker">
          <span className="siq-ticker-sym">{meta.ticker}</span>
          <span className="siq-ticker-badge">{meta.filing}</span>
        </div>
        <div className="siq-filing-meta">
          <span className="siq-filing-co">{meta.company}</span>
          <span className="siq-dot-sep">·</span>
          <span>{meta.period}</span>
          <span className="siq-dot-sep">·</span>
          <span>Filed {meta.filedOn}</span>
        </div>
      </div>
      <div className="siq-filing-right">
        <div className="siq-filing-query-label">Query</div>
        <div className="siq-filing-query">"{query}"</div>
      </div>
    </div>);

}

function CardHeader({ kicker, title, subtitle }) {
  return (
    <div className="siq-card-header">
      <div className="siq-kicker">{kicker}</div>
      <div className="siq-card-title-wrap">
        <h2 className="siq-card-title">{title}</h2>
        {subtitle && <div className="siq-card-subtitle">{subtitle}</div>}
      </div>
    </div>);

}

// =====================================================================
// Tone spectrum bar
// =====================================================================
function ToneSpectrum({ score, confidence }) {
  // score: -1 .. +1
  const pct = (score + 1) / 2 * 100;
  const label =
  score > 0.5 ?
  "Optimistic" :
  score > 0.15 ?
  "Cautiously optimistic" :
  score > -0.15 ?
  "Neutral" :
  score > -0.5 ?
  "Cautious" :
  "Negative";

  return (
    <div className="siq-tone">
      <div className="siq-tone-row">
        <div className="siq-tone-readout">
          <div className="siq-tone-label">{label}</div>
          <div className="siq-tone-score">
            <span className="siq-tone-score-num">{score >= 0 ? "+" : ""}{score.toFixed(2)}</span>
            <span className="siq-tone-score-sep">/</span>
            <span className="siq-tone-score-max">+1.00</span>
          </div>
        </div>
        <div className="siq-tone-conf">
          <span className="siq-tone-conf-label">Confidence</span>
          <span className="siq-tone-conf-val">{(confidence * 100).toFixed(0)}%</span>
        </div>
      </div>

      <div className="siq-tone-bar">
        <div className="siq-tone-bar-track">
          <div className="siq-tone-bar-grad" />
          <div className="siq-tone-bar-ticks" aria-hidden="true">
            {[0, 25, 50, 75, 100].map((t) =>
            <span key={t} style={{ left: `${t}%` }} />
            )}
          </div>
          <div
            className="siq-tone-bar-marker"
            style={{ left: `${pct}%` }}>
            
            <div className="siq-tone-bar-marker-glow" />
            <div className="siq-tone-bar-marker-dot" />
          </div>
        </div>
        <div className="siq-tone-bar-axis">
          <span>Negative</span>
          <span>Cautious</span>
          <span>Neutral</span>
          <span>Cautious +</span>
          <span>Positive</span>
        </div>
      </div>
    </div>);

}

function SentimentBars({ breakdown }) {
  const items = [
  { key: "positive", label: "Positive", val: breakdown.positive, cls: "pos" },
  { key: "neutral", label: "Neutral", val: breakdown.neutral, cls: "neu" },
  { key: "negative", label: "Negative", val: breakdown.negative, cls: "neg" }];

  return (
    <div className="siq-senti">
      {items.map((it) =>
      <div key={it.key} className={`siq-senti-row siq-senti-${it.cls}`}>
          <div className="siq-senti-label">{it.label}</div>
          <div className="siq-senti-track">
            <div
            className="siq-senti-fill"
            style={{ width: `${it.val * 100}%` }} />
          
          </div>
          <div className="siq-senti-val">{(it.val * 100).toFixed(0)}%</div>
        </div>
      )}
    </div>);

}

// =====================================================================
// Meta table
// =====================================================================
function MetaTable({ meta }) {
  const rows = [
  ["Company", meta.company],
  ["Ticker", meta.ticker],
  ["Filing", meta.filing],
  ["Period", meta.period],
  ["Filed", meta.filedOn]];

  return (
    <dl className="siq-meta">
      {rows.map(([k, v]) =>
      <div key={k} className="siq-meta-row">
          <dt>{k}</dt>
          <dd>{v}</dd>
        </div>
      )}
    </dl>);

}

// =====================================================================
// Risk grid
// =====================================================================
function RiskGrid({ risks }) {
  return (
    <div className="siq-risk-grid">
      {risks.map((r, i) =>
      <article key={i} className={`siq-risk siq-risk-${r.severity}`}>
          <div className="siq-risk-top">
            <div className="siq-risk-num">R{String(i + 1).padStart(2, "0")}</div>
            <div className={`siq-risk-sev siq-risk-sev-${r.severity}`}>
              <span className="siq-risk-sev-dot" />
              {r.severity}
            </div>
          </div>
          <h3 className="siq-risk-label">{r.label}</h3>
          <div className="siq-risk-foot">
            <span className="siq-cite-ref">[{r.citation}]</span>
            <span className="siq-risk-foot-label">Evidence</span>
          </div>
        </article>
      )}
    </div>);

}

// =====================================================================
// Delta table (Notable Changes)
// =====================================================================
function formatChangeKey(key) {
  return key
    .replace(/YoY/g, " Year Over Year")
    .replace(/QoQ/g, " Quarter Over Quarter")
    .replace(/([A-Z])/g, " $1")
    .replace(/\s+/g, " ")
    .trim()
    .replace(/\b\w/g, (c) => c.toUpperCase());
}

function DeltaTable({ changes }) {
  const entries = Object.entries(changes);
  return (
    <div className="siq-delta">
      {entries.map(([key, val]) =>
      <div key={key} className={`siq-delta-row siq-delta-${val.direction}`}>
          <div className="siq-delta-key">{formatChangeKey(key)}</div>
          <div className="siq-delta-bar">
            <DeltaBar direction={val.direction} delta={val.delta} />
          </div>
          <div className="siq-delta-num">
            <span className={`siq-delta-arrow siq-delta-arrow-${val.direction}`}>
              {val.direction === "up" ? "↑" : val.direction === "down" ? "↓" : "→"}
            </span>
          </div>
        </div>
      )}
    </div>);

}

function DeltaBar({ direction, delta }) {
  const num = parseFloat(String(delta).replace(/[^0-9.\-]/g, "")) || 0;
  const mag = Math.min(Math.abs(num) / 50, 1); // 50% = full width
  if (direction === "flat") {
    return (
      <div className="siq-deltabar siq-deltabar-flat">
        <div className="siq-deltabar-axis" />
        <div className="siq-deltabar-flat-mark" />
      </div>);

  }
  return (
    <div className={`siq-deltabar siq-deltabar-${direction}`}>
      <div className="siq-deltabar-axis" />
      <div
        className={`siq-deltabar-fill siq-deltabar-fill-${direction}`}
        style={{ width: `${mag * 50}%` }} />
      
    </div>);

}

// =====================================================================
// Citations (numbered footnote list)
// =====================================================================
function Citations({ citations }) {
  return (
    <ol className="siq-cites">
      {citations.map((c) =>
      <li key={c.n} className="siq-cite">
          <div className="siq-cite-n">[{c.n}]</div>
          <div className="siq-cite-body">
            <blockquote className="siq-cite-quote">{c.quote}</blockquote>
            <div className="siq-cite-source">
              <svg viewBox="0 0 16 16" width="11" height="11">
                <path d="M3 2 L10 2 L13 5 L13 14 L3 14 Z M10 2 L10 5 L13 5" fill="none" stroke="currentColor" strokeWidth="1.3" strokeLinejoin="round" />
              </svg>
              {c.source}
            </div>
          </div>
        </li>
      )}
    </ol>);

}

Object.assign(window, {
  BrandPill,
  SearchHeader,
  HeroState,
  AnalyzingState,
  Results
});