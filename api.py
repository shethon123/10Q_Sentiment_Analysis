import asyncio
import json
import sys

if sys.platform == "win32":
    asyncio.set_event_loop_policy(asyncio.WindowsProactorEventLoopPolicy())

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from pydantic import BaseModel

from runllm import _chat_async_stream
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
    async def event_stream():
        try:
            async for event in _chat_async_stream(req.query):
                if event["type"] == "tool":
                    yield f"data: {json.dumps({'type': 'tool', 'name': event['name'], 'args': event['args']})}\n\n"
                elif event["type"] == "result":
                    result = event["data"]
                    if isinstance(result, str):
                        yield f"data: {json.dumps({'type': 'error', 'detail': 'LLM did not return valid JSON'})}\n\n"
                        return
                    enriched = analyze_json_output(result)
                    summary = enriched.get("summary", {})
                    notable_changes = [
                        {"key": k, **v}
                        for k, v in summary.get("notableChangesFromPriorQuarter", {}).items()
                    ]
                    payload = {
                        "type": "result",
                        "data": {
                            "meta": summary.get("meta", {}),
                            "overallToneAssessment": summary.get("overallToneAssessment", ""),
                            "analystTakeaway": summary.get("analystTakeaway", ""),
                            "overallSentiment": compute_overall_sentiment(enriched),
                            "keyRiskSignals": summary.get("keyRiskSignals", []),
                            "notableChanges": notable_changes,
                            "evidenceCitations": summary.get("specificEvidenceCitations", []),
                        },
                    }
                    yield f"data: {json.dumps(payload)}\n\n"
        except Exception as exc:
            yield f"data: {json.dumps({'type': 'error', 'detail': str(exc)})}\n\n"

    return StreamingResponse(
        event_stream(),
        media_type="text/event-stream",
        headers={"Cache-Control": "no-cache", "X-Accel-Buffering": "no"},
    )
