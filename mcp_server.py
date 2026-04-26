from typing import Optional
from download import get_10q_sections


def fetch_10q_mda(ticker: str, year: Optional[int] = None, quarter: Optional[int] = None) -> str:
    """
    Returns the MD&A section (Part I, Item 2) from a 10-Q.
    This is management's own narrative on financial condition and results — most useful for sentiment.

    Args:
        ticker: Stock ticker symbol (e.g. 'AAPL')
        year: Filing year (e.g. 2024). If omitted, uses the most recent filing.
        quarter: Fiscal quarter (1, 2, or 3 — 10-Qs are not filed for Q4). If omitted, uses the most recent filing.
    """
    sections = get_10q_sections(ticker, year=year, quarter=quarter)
    return sections.get("mdna") or "MD&A section not found."


def fetch_10q_risk_factors(ticker: str, year: Optional[int] = None, quarter: Optional[int] = None) -> str:
    """
    Returns the Risk Factors section (Part II, Item 1A) from a 10-Q.
    Use this to identify material risks disclosed by the company.

    Args:
        ticker: Stock ticker symbol (e.g. 'AAPL')
        year: Filing year (e.g. 2024). If omitted, uses the most recent filing.
        quarter: Fiscal quarter (1, 2, or 3 — 10-Qs are not filed for Q4). If omitted, uses the most recent filing.
    """
    sections = get_10q_sections(ticker, year=year, quarter=quarter)
    return sections.get("risk_factors") or "Risk factors not found."


def fetch_10q_financials(ticker: str, year: Optional[int] = None, quarter: Optional[int] = None) -> dict:
    """
    Returns structured financial statements (income statement, balance sheet, cash flow) from a 10-Q.
    Use this for quantitative financial data.

    Args:
        ticker: Stock ticker symbol (e.g. 'AAPL')
        year: Filing year (e.g. 2024). If omitted, uses the most recent filing.
        quarter: Fiscal quarter (1, 2, or 3 — 10-Qs are not filed for Q4). If omitted, uses the most recent filing.
    """
    sections = get_10q_sections(ticker, year=year, quarter=quarter)
    return {
        "income_statement": str(sections.get("income_statement") or "Not available"),
        "balance_sheet": str(sections.get("balance_sheet") or "Not available"),
        "cash_flow": str(sections.get("cash_flow") or "Not available"),
    }


def fetch_10q_market_risk(ticker: str, year: Optional[int] = None, quarter: Optional[int] = None) -> str:
    """
    Returns the Quantitative and Qualitative Disclosures About Market Risk section (Part I, Item 3).
    Use this for interest rate risk, foreign exchange exposure, and commodity risk disclosures.

    Args:
        ticker: Stock ticker symbol (e.g. 'AAPL')
        year: Filing year (e.g. 2024). If omitted, uses the most recent filing.
        quarter: Fiscal quarter (1, 2, or 3 — 10-Qs are not filed for Q4). If omitted, uses the most recent filing.
    """
    sections = get_10q_sections(ticker, year=year, quarter=quarter)
    return sections.get("market_risk") or "Market risk section not found."


def fetch_10q_legal_proceedings(ticker: str, year: Optional[int] = None, quarter: Optional[int] = None) -> str:
    """
    Returns the Legal Proceedings section (Part II, Item 1) from a 10-Q.
    Use this to identify ongoing litigation, regulatory actions, or legal risks.

    Args:
        ticker: Stock ticker symbol (e.g. 'AAPL')
        year: Filing year (e.g. 2024). If omitted, uses the most recent filing.
        quarter: Fiscal quarter (1, 2, or 3 — 10-Qs are not filed for Q4). If omitted, uses the most recent filing.
    """
    sections = get_10q_sections(ticker, year=year, quarter=quarter)
    return sections.get("legal_proceedings") or "Legal proceedings section not found."


def fetch_10q_all_sections(ticker: str, year: Optional[int] = None, quarter: Optional[int] = None) -> dict:
    """
    Returns all available 10-Q sections in a single call: MD&A, risk factors, market risk,
    controls, legal proceedings, and financial statements.
    Use this when you need a comprehensive view or are unsure which sections are most relevant.
    The metadata field includes 'available_sections' listing what keys this filing actually contains.

    Args:
        ticker: Stock ticker symbol (e.g. 'AAPL')
        year: Filing year (e.g. 2024). If omitted, uses the most recent filing.
        quarter: Fiscal quarter (1, 2, or 3 — 10-Qs are not filed for Q4). If omitted, uses the most recent filing.
    """
    sections = get_10q_sections(ticker, year=year, quarter=quarter)
    return {
        "metadata": sections.get("metadata", {}),
        "mdna": sections.get("mdna") or "Not available",
        "risk_factors": sections.get("risk_factors") or "Not available",
        "market_risk": sections.get("market_risk") or "Not available",
        "controls": sections.get("controls") or "Not available",
        "legal_proceedings": sections.get("legal_proceedings") or "Not available",
        "income_statement": str(sections.get("income_statement") or "Not available"),
        "balance_sheet": str(sections.get("balance_sheet") or "Not available"),
        "cash_flow": str(sections.get("cash_flow") or "Not available"),
    }
