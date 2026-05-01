import json
from typing import Optional
from mcp.server.fastmcp import FastMCP
from download import get_10q_sections

mcp = FastMCP("10Q Analysis")


@mcp.tool()
def fetch_10q_mda(ticker: str, year: Optional[int] = None, quarter: Optional[int] = None) -> str:
    """
    Returns the MD&A section from a 10-Q for sentiment analysis.

    Args:
        ticker: Stock ticker symbol (e.g. 'AAPL')
        year: Filing year (e.g. 2024). If omitted, uses the most recent filing.
        quarter: Fiscal quarter (1, 2, or 3 — 10-Qs are not filed for Q4). If omitted, uses the most recent filing.
    """
    sections = get_10q_sections(ticker, year=year, quarter=quarter)
    return sections.get("mdna") or "MD&A section not found."


@mcp.tool()
def fetch_10q_risk_factors(ticker: str, year: Optional[int] = None, quarter: Optional[int] = None) -> str:
    """
    Returns the Risk Factors section from a 10-Q.

    Args:
        ticker: Stock ticker symbol (e.g. 'AAPL')
        year: Filing year (e.g. 2024). If omitted, uses the most recent filing.
        quarter: Fiscal quarter (1, 2, or 3 — 10-Qs are not filed for Q4). If omitted, uses the most recent filing.
    """
    sections = get_10q_sections(ticker, year=year, quarter=quarter)
    return sections.get("risk_factors") or "Risk factors not found."


@mcp.tool()
def fetch_10q_financials(ticker: str, year: Optional[int] = None, quarter: Optional[int] = None) -> dict:
    """
    Returns structured financial statements from a 10-Q.

    Args:
        ticker: Stock ticker symbol (e.g. 'AAPL')
        year: Filing year (e.g. 2024). If omitted, uses the most recent filing.
        quarter: Fiscal quarter (1, 2, or 3 — 10-Qs are not filed for Q4). If omitted, uses the most recent filing.
    """
    sections = get_10q_sections(ticker, year=year, quarter=quarter)
    return {
        "income_statement": str(sections.get("income_statement")),
        "balance_sheet": str(sections.get("balance_sheet")),
        "cash_flow": str(sections.get("cash_flow")),
    }


@mcp.tool()
def fetch_10q_metadata(ticker: str, year: Optional[int] = None, quarter: Optional[int] = None) -> str:
    """
    Returns filing metadata (company name, period, filed date, accession number) as a JSON string.

    Args:
        ticker: Stock ticker symbol (e.g. 'AAPL')
        year: Filing year (e.g. 2024). If omitted, uses the most recent filing.
        quarter: Fiscal quarter (1, 2, or 3). If omitted, uses the most recent filing.
    """
    sections = get_10q_sections(ticker, year=year, quarter=quarter)
    return json.dumps(sections["metadata"])


if __name__ == "__main__":
    mcp.run()
