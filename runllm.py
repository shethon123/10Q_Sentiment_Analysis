from openai import OpenAI
import json
import re
from mcp_server import (
    fetch_10q_mda,
    fetch_10q_risk_factors,
    fetch_10q_financials,
    fetch_10q_market_risk,
    fetch_10q_legal_proceedings,
    fetch_10q_all_sections,
)
import os
from dotenv import load_dotenv
import ollama

# 1. Load the variables from .env into the environment
load_dotenv()

client = OpenAI(base_url='http://localhost:3000/api',
                api_key=os.getenv("OLLAMA_API_KEY"))  # reads OPENAI_API_KEY from env

SYSTEM_PROMPT = (
    "You are a financial analyst assistant. When answering questions about SEC 10-Q filings, "
    "always respond with ONLY a JSON object in exactly this format:\n"
    "{\n"
    '  "summary": {\n'
    '    "overallToneAssessment": "string describing overall tone",\n'
    '    "keyRiskSignals": ["risk1", "risk2"],\n'
    '    "notableChangesFromPriorQuarter": {"changeKey": "description"},\n'
    '    "specificEvidenceCitations": ["[1] direct quote", "[2] ..."]\n'
    "  }\n"
    "}\n"
    "Do not include any text outside the JSON object."
)

# --- Tool schemas (same structure, OpenAI uses "function" wrapper) ---
tools = [
    {
        "type": "function",
        "function": {
            "name": "fetch_10q_mda",
            "description": "Returns the MD&A section from a 10-Q for sentiment analysis.",
            "parameters": {
                "type": "object",
                "properties": {
                    "ticker": {"type": "string", "description": "Stock ticker symbol (e.g. 'AAPL')"},
                    "year": {"type": "integer", "description": "Filing year (e.g. 2024). Omit for most recent."},
                    "quarter": {"type": "integer", "description": "Fiscal quarter 1-3. Omit for most recent."},
                },
                "required": ["ticker"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "fetch_10q_risk_factors",
            "description": "Returns the Risk Factors section from a 10-Q.",
            "parameters": {
                "type": "object",
                "properties": {
                    "ticker": {"type": "string", "description": "Stock ticker symbol (e.g. 'AAPL')"},
                    "year": {"type": "integer", "description": "Filing year (e.g. 2024). Omit for most recent."},
                    "quarter": {"type": "integer", "description": "Fiscal quarter 1-3. Omit for most recent."},
                },
                "required": ["ticker"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "fetch_10q_financials",
            "description": "Returns structured financial statements (income statement, balance sheet, cash flow) from a 10-Q.",
            "parameters": {
                "type": "object",
                "properties": {
                    "ticker": {"type": "string", "description": "Stock ticker symbol (e.g. 'AAPL')"},
                    "year": {"type": "integer", "description": "Filing year (e.g. 2024). Omit for most recent."},
                    "quarter": {"type": "integer", "description": "Fiscal quarter 1-3. Omit for most recent."},
                },
                "required": ["ticker"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "fetch_10q_market_risk",
            "description": "Returns the Market Risk section (Part I, Item 3) — interest rate risk, FX exposure, commodity risk.",
            "parameters": {
                "type": "object",
                "properties": {
                    "ticker": {"type": "string", "description": "Stock ticker symbol (e.g. 'AAPL')"},
                    "year": {"type": "integer", "description": "Filing year (e.g. 2024). Omit for most recent."},
                    "quarter": {"type": "integer", "description": "Fiscal quarter 1-3. Omit for most recent."},
                },
                "required": ["ticker"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "fetch_10q_legal_proceedings",
            "description": "Returns the Legal Proceedings section (Part II, Item 1) — litigation, regulatory actions, legal risks.",
            "parameters": {
                "type": "object",
                "properties": {
                    "ticker": {"type": "string", "description": "Stock ticker symbol (e.g. 'AAPL')"},
                    "year": {"type": "integer", "description": "Filing year (e.g. 2024). Omit for most recent."},
                    "quarter": {"type": "integer", "description": "Fiscal quarter 1-3. Omit for most recent."},
                },
                "required": ["ticker"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "fetch_10q_all_sections",
            "description": "Returns ALL 10-Q sections in one call: MD&A, risk factors, market risk, controls, legal proceedings, and financials. Use this when you need a comprehensive view or are unsure which sections are relevant. Check metadata.available_sections to see what keys this filing actually contains.",
            "parameters": {
                "type": "object",
                "properties": {
                    "ticker": {"type": "string", "description": "Stock ticker symbol (e.g. 'AAPL')"},
                    "year": {"type": "integer", "description": "Filing year (e.g. 2024). Omit for most recent."},
                    "quarter": {"type": "integer", "description": "Fiscal quarter 1-3. Omit for most recent."},
                },
                "required": ["ticker"],
            },
        },
    },
]

tool_registry = {
    "fetch_10q_mda": fetch_10q_mda,
    "fetch_10q_risk_factors": fetch_10q_risk_factors,
    "fetch_10q_financials": fetch_10q_financials,
    "fetch_10q_market_risk": fetch_10q_market_risk,
    "fetch_10q_legal_proceedings": fetch_10q_legal_proceedings,
    "fetch_10q_all_sections": fetch_10q_all_sections,
}

def parse_llm_response(content: str):
    """Extract and parse JSON from LLM response. Returns dict on success, raw string on failure."""
    try:
        return json.loads(content)
    except json.JSONDecodeError:
        pass
    match = re.search(r'\{.*\}', content, re.DOTALL)
    if match:
        try:
            return json.loads(match.group())
        except json.JSONDecodeError:
            pass
    return content


def run_tool(tool_name: str, tool_input: dict):
    fn = tool_registry.get(tool_name)
    if not fn:
        return f"Unknown tool: {tool_name}"
    try:
        result = fn(**tool_input)
        return json.dumps(result) if isinstance(result, dict) else str(result)
    except Exception as e:
        return f"Error fetching data: {e}"

def chat(user_message: str):
    messages = [
        {"role": "system", "content": SYSTEM_PROMPT},
        {"role": "user", "content": user_message},
    ]

    while True:
        response = ollama.chat(
            model="gemma4:latest",
            tools=tools,
            messages=messages,
        )

        msg = response.message
        messages.append(msg)

        if msg.tool_calls:
            for tool_call in msg.tool_calls:
                tool_name = tool_call.function.name
                tool_input = dict(tool_call.function.arguments)
                args_str = ", ".join(f"{k}={v}" for k, v in tool_input.items())
                print(f"[Tool: {tool_name}({args_str})]")
                result = run_tool(tool_name, tool_input)
                messages.append({"role": "tool", "content": result})
        else:
            return parse_llm_response(msg.content or "")
