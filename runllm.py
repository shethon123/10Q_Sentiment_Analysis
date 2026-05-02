import json
import re
import os
import sys
import asyncio
from dotenv import load_dotenv
from openai import OpenAI
import anthropic
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

load_dotenv()

SYSTEM_PROMPT = (
    "You are a financial analyst assistant. When answering questions about SEC 10-Q filings, "
    "always respond with ONLY a JSON object in exactly this format:\n"
    "{\n"
    '  "summary": {\n'
    '    "meta": {"ticker": "AAPL", "company_name": "Apple Inc.", "period_of_report": "2024-09-30", "filed": "2024-11-01", "accession_number": "0001234"},\n'
    '    "overallToneAssessment": "string describing overall tone",\n'
    '    "analystTakeaway": "2-3 sentence investor-facing summary",\n'
    '    "keyRiskSignals": ["risk signal 1", "risk signal 2", "risk signal 3", "risk signal 4", "risk signal 5", "risk signal 6", "risk signal 7"],\n'
    '    "notableChangesFromPriorQuarter": {"changeKey": "description"},\n'
    '    "specificEvidenceCitations": ["[1] direct quote from filing", "[2] direct quote", "[3] direct quote", "[4] direct quote", "[5] direct quote", "[6] direct quote", "[7] direct quote"]\n'
    "  }\n"
    "}\n\n"
    "Requirements:\n"
    "- analystTakeaway: write 2-3 sentences in plain English, investor-facing, synthesizing the overall tone and key risks into a single actionable takeaway. No jargon. Focus on what an investor should know.\n"
    "- keyRiskSignals: include AT LEAST 5 distinct risk signals. Each must be a complete descriptive phrase (10+ words) drawn from the risk factors and MD&A sections.\n"
    "- specificEvidenceCitations: include AT LEAST 5 direct verbatim quotes from the filing that support the tone assessment. Each quote should be 15–80 words.\n"
    "- notableChangesFromPriorQuarter: include AT LEAST 3 distinct changes observed in the financial statements or MD&A.\n"
    "- Call fetch_10q_metadata with the same ticker, year, and quarter you use for other tools, "
    "and embed the parsed result as the value of the 'meta' field.\n"
    "- Do not include any text outside the JSON object."
)

_SERVER_SCRIPT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "mcp_server.py")


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


def openai_tools(tools: list[dict]) -> list[dict]:
    return [{"type": "function", "function": t} for t in tools]


def claude_tools(tools: list[dict]) -> list[dict]:
    return [
        {"name": t["name"], "description": t.get("description", ""), "input_schema": t["parameters"]}
        for t in tools
    ]


class OllamaClient:
    def __init__(self, model: str):
        import ollama as _ollama
        self._ollama = _ollama
        self.model = model

    async def chat_turn(
        self, messages: list, tools: list[dict]
    ) -> tuple[list, list[tuple[str, str, dict]], str]:
        response = self._ollama.chat(
            model=self.model,
            tools=openai_tools(tools),
            messages=messages,
        )
        msg = response.message
        updated = messages + [msg]
        tool_calls = []
        if msg.tool_calls:
            for tc in msg.tool_calls:
                tool_calls.append((tc.function.name, "", dict(tc.function.arguments)))
        return updated, tool_calls, msg.content or ""

    def tool_result_message(self, _tool_name: str, _call_id: str, result: str) -> dict:
        return {"role": "tool", "content": result}


class OpenAIClient:
    def __init__(self, api_key: str, model: str):
        self._client = OpenAI(api_key=api_key)
        self.model = model

    async def chat_turn(
        self, messages: list, tools: list[dict]
    ) -> tuple[list, list[tuple[str, str, dict]], str]:
        response = self._client.chat.completions.create(
            model=self.model,
            tools=openai_tools(tools),
            messages=messages,
        )
        msg = response.choices[0].message
        msg_dict = {
            "role": "assistant",
            "content": msg.content,
            "tool_calls": [
                {
                    "id": tc.id,
                    "type": "function",
                    "function": {"name": tc.function.name, "arguments": tc.function.arguments},
                }
                for tc in (msg.tool_calls or [])
            ],
        }
        updated = messages + [msg_dict]
        tool_calls = []
        if msg.tool_calls:
            for tc in msg.tool_calls:
                tool_calls.append((tc.function.name, tc.id, json.loads(tc.function.arguments)))
        return updated, tool_calls, msg.content or ""

    def tool_result_message(self, _tool_name: str, call_id: str, result: str) -> dict:
        return {"role": "tool", "tool_call_id": call_id, "content": result}


class ClaudeClient:
    def __init__(self, api_key: str, model: str):
        self._client = anthropic.Anthropic(api_key=api_key)
        self.model = model

    async def chat_turn(
        self, messages: list, tools: list[dict]
    ) -> tuple[list, list[tuple[str, str, dict]], str]:
        system = next((m["content"] for m in messages if m["role"] == "system"), "")
        claude_messages = [m for m in messages if m["role"] != "system"]

        response = self._client.messages.create(
            model=self.model,
            max_tokens=4096,
            system=system,
            tools=claude_tools(tools),
            messages=claude_messages,
        )

        assistant_msg = {"role": "assistant", "content": response.content}
        updated = messages + [assistant_msg]

        tool_calls = []
        text = ""
        for block in response.content:
            if block.type == "tool_use":
                tool_calls.append((block.name, block.id, block.input))
            elif block.type == "text":
                text = block.text

        return updated, tool_calls, text

    def tool_result_message(self, _tool_name: str, call_id: str, result: str) -> dict:
        return {
            "role": "user",
            "content": [{"type": "tool_result", "tool_use_id": call_id, "content": result}],
        }


def get_client():
    provider = os.getenv("LLM_PROVIDER", "ollama")
    if provider == "ollama":
        model = os.getenv("OLLAMA_MODEL", "gemma4:latest")
        return OllamaClient(model)
    elif provider == "openai":
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            raise ValueError("OPENAI_API_KEY is required when LLM_PROVIDER=openai")
        model = os.getenv("OPENAI_MODEL", "gpt-4o")
        return OpenAIClient(api_key, model)
    elif provider == "claude":
        api_key = os.getenv("ANTHROPIC_API_KEY")
        if not api_key:
            raise ValueError("ANTHROPIC_API_KEY is required when LLM_PROVIDER=claude")
        model = os.getenv("CLAUDE_MODEL", "claude-sonnet-4-6")
        return ClaudeClient(api_key, model)
    else:
        raise ValueError(
            f"Unknown LLM_PROVIDER '{provider}'. Valid options: ollama, openai, claude"
        )


async def _chat_async_stream(user_message: str):
    """Async generator yielding tool events then a final result event."""
    client = get_client()

    server_params = StdioServerParameters(
        command=sys.executable,
        args=[_SERVER_SCRIPT],
    )

    async with stdio_client(server_params) as (read, write):
        async with ClientSession(read, write) as session:
            await session.initialize()

            tools_result = await session.list_tools()
            tools = [
                {
                    "name": tool.name,
                    "description": tool.description or "",
                    "parameters": tool.inputSchema,
                }
                for tool in tools_result.tools
            ]

            messages = [
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": user_message},
            ]

            while True:
                messages, tool_calls, text = await client.chat_turn(messages, tools)

                if tool_calls:
                    for tool_name, call_id, tool_input in tool_calls:
                        yield {"type": "tool", "name": tool_name, "args": tool_input}
                        result = await session.call_tool(tool_name, tool_input)
                        result_text = result.content[0].text if result.content else ""
                        messages.append(client.tool_result_message(tool_name, call_id, result_text))
                else:
                    yield {"type": "result", "data": parse_llm_response(text)}
                    return


async def _chat_async(user_message: str):
    async for event in _chat_async_stream(user_message):
        if event["type"] == "result":
            return event["data"]


def chat(user_message: str):
    return asyncio.run(_chat_async(user_message))
