import edgar
from edgar import Company, set_identity
from typing import Optional

# Required by SEC — set your identity once
set_identity("Your Name yourname@email.com")


def get_fiscal_quarter(period_of_report: str) -> int:
    """Derives calendar quarter from period_of_report date (YYYY-MM-DD)."""
    month = int(period_of_report[5:7])
    if month in (1, 2, 3):
        return 1
    elif month in (4, 5, 6):
        return 2
    elif month in (7, 8, 9):
        return 3
    else:
        return 4


def _get_section(tenq, *keys) -> Optional[str]:
    """
    Try each candidate key in order; return the first non-empty result.
    Covers variations like 'Part I, Item 2' vs 'PART I, ITEM 2' vs 'Item 2'.
    """
    for key in keys:
        try:
            val = tenq[key]
            if val:
                return str(val)
        except (KeyError, TypeError, AttributeError):
            pass
    return None


def _list_available_sections(tenq) -> list:
    """Return section keys present in this filing (useful for debugging missing sections)."""
    try:
        raw = tenq.items
        if isinstance(raw, dict):
            return [k for k, v in raw.items() if v]
    except (AttributeError, TypeError):
        pass
    return []


def get_10q_sections(ticker: str, year: int = None, quarter: int = None) -> dict:
    """
    Fetches a 10-Q and returns the key sections as clean text.
    Defaults to the most recent filing if year/quarter not specified.

    Quarter matching: when year is given, filings are ordered oldest→newest within
    that year (Q1=first filing, Q2=second, Q3=third). This follows fiscal-year order
    regardless of calendar month, which matches how analysts reference quarters.
    """
    company = Company(ticker)

    if year:
        filings = company.get_filings(form="10-Q", date=f"{year}-01-01:{year}-12-31")
    else:
        filings = company.get_filings(form="10-Q")

    filing_list = sorted(list(filings), key=lambda f: str(f.filing_date))

    if not filing_list:
        raise ValueError(
            f"No 10-Q filings found for {ticker}" + (f" in {year}" if year else "")
        )

    if quarter:
        idx = quarter - 1  # Q1=0, Q2=1, Q3=2
        if idx >= len(filing_list):
            available = [
                f"{str(f.period_of_report)} (Q{get_fiscal_quarter(str(f.period_of_report))})"
                for f in filing_list
            ]
            raise ValueError(
                f"Quarter {quarter} not found for {ticker}"
                + (f" in {year}" if year else "")
                + f". Available filings: {available}"
            )
        filing = filing_list[idx]
    else:
        filing = filing_list[-1]

    tenq = filing.obj()
    sections: dict = {}

    # --- Part I, Item 2: MD&A ---
    sections["mdna"] = _get_section(
        tenq,
        "Part I, Item 2",
        "PART I, ITEM 2",
        "Item 2",
        "ITEM 2",
        "Management's Discussion and Analysis",
        "Management's Discussion and Analysis of Financial Condition and Results of Operations",
    )

    # --- Part II, Item 1A: Risk Factors ---
    sections["risk_factors"] = _get_section(
        tenq,
        "Part II, Item 1A",
        "PART II, ITEM 1A",
        "Item 1A",
        "ITEM 1A",
        "Risk Factors",
    )

    # --- Part I, Item 3: Quantitative and Qualitative Disclosures About Market Risk ---
    sections["market_risk"] = _get_section(
        tenq,
        "Part I, Item 3",
        "PART I, ITEM 3",
        "Item 3",
        "ITEM 3",
        "Quantitative and Qualitative Disclosures About Market Risk",
    )

    # --- Part I, Item 4: Controls and Procedures ---
    sections["controls"] = _get_section(
        tenq,
        "Part I, Item 4",
        "PART I, ITEM 4",
        "Item 4",
        "ITEM 4",
        "Controls and Procedures",
    )

    # --- Part II, Item 1: Legal Proceedings ---
    sections["legal_proceedings"] = _get_section(
        tenq,
        "Part II, Item 1",
        "PART II, ITEM 1",
        "Legal Proceedings",
    )

    # --- Financial Statements (Part I, Item 1) ---
    financials = tenq.financials
    if financials:
        sections["income_statement"] = financials.income_statement
        sections["balance_sheet"] = financials.balance_sheet
        sections["cash_flow"] = financials.cash_flow_statement
    else:
        sections["income_statement"] = None
        sections["balance_sheet"] = None
        sections["cash_flow"] = None

    # --- Metadata (includes available_sections for debugging missing keys) ---
    sections["metadata"] = {
        "ticker": ticker,
        "company_name": filing.company,
        "period_of_report": str(filing.period_of_report),
        "fiscal_quarter": get_fiscal_quarter(str(filing.period_of_report)),
        "filed": str(filing.filing_date),
        "accession_number": filing.accession_number,
        "available_sections": _list_available_sections(tenq),
    }

    return sections


def print_section_preview(sections: dict, chars: int = 500):
    """Preview each section."""
    for key, val in sections.items():
        if key == "metadata":
            print(f"\n{'='*60}")
            print(f"METADATA: {val}")
            continue
        print(f"\n{'='*60}")
        print(f"SECTION: {key.upper()}")
        print(f"{'='*60}")
        if val is None:
            print("  [Not available]")
        elif hasattr(val, '__str__'):
            text = str(val)
            print(text[:chars] + "..." if len(text) > chars else text)


if __name__ == "__main__":
    sections = get_10q_sections("AAPL")
    print_section_preview(sections)
