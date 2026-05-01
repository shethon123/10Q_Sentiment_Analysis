import asyncio
import sys

if sys.platform == "win32":
    asyncio.set_event_loop_policy(asyncio.WindowsProactorEventLoopPolicy())

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from runllm import _chat_async
from finbert import analyze_json_output, compute_overall_sentiment

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


class AnalyzeRequest(BaseModel):
    query: str


@app.get("/health")
def health():
    return {"status": "ok"}


@app.post("/analyze")
async def analyze(req: AnalyzeRequest):
    try:
        result = await _chat_async(req.query)
    except Exception as exc:
        raise HTTPException(status_code=502, detail=str(exc))

    if isinstance(result, str):
        raise HTTPException(
            status_code=422,
            detail={"detail": "LLM did not return valid JSON", "raw": result},
        )

    enriched = analyze_json_output(result)
    summary = enriched.get("summary", {})

    notable_changes = [
        {"key": k, **v}
        for k, v in summary.get("notableChangesFromPriorQuarter", {}).items()
    ]

    return {
        "meta": summary.get("meta", {}),
        "overallToneAssessment": summary.get("overallToneAssessment", ""),
        "overallSentiment": compute_overall_sentiment(enriched),
        "keyRiskSignals": summary.get("keyRiskSignals", []),
        "notableChanges": notable_changes,
        "evidenceCitations": summary.get("specificEvidenceCitations", []),
    }
