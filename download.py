import edgar
from edgar import Company, set_identity

# Required by SEC — set your identity once
set_identity("Your Name yourname@email.com")

def get_fiscal_quarter(period_of_report: str) -> int:
    """
    Derives the fiscal quarter number from the filing's own period_of_report date.
    This works regardless of when the company's fiscal year starts.
    """
    month = int(period_of_report[5:7])  # Extract MM from YYYY-MM-DD
    if month in (1, 2, 3):
        return 1
    elif month in (4, 5, 6):
        return 2
    elif month in (7, 8, 9):
        return 3
    else:
        return 4  # Shouldn't appear in 10-Qs but just in case
    
def get_10q_sections(ticker: str, year: int = None, quarter: int = None):
    """
    Fetches a 10-Q and returns the key sections as clean text.
    Defaults to the most recent filing if year/quarter not specified.
    """
    company = Company(ticker)
    
    # Get 10-Q filings
    if year:
        # Get all 10-Qs for that year directly from edgartools
        filings = company.get_filings(form="10-Q", date=f"{year}-01-01:{year}-12-31")
    else:
        filings = company.get_filings(form="10-Q")

    # Convert to list sorted oldest -> newest
    filing_list = sorted(list(filings), key=lambda f: str(f.filing_date))

    if not filing_list:
        raise ValueError(f"No 10-Q filings found for {ticker} in {year}")

    if quarter:
        idx = quarter - 1  # Q1=0, Q2=1, Q3=2
        if idx >= len(filing_list):
            available = [str(f.period_of_report) for f in filing_list]
            raise ValueError(
                f"Quarter {quarter} not found for {ticker} in {year}. "
                f"Available periods: {available}"
            )
        filing = filing_list[idx]
    else:
        filing = filing_list[-1]  # most recent

    # Parse into the structured TenQ object
    tenq = filing.obj()

    sections = {}

    # --- MD&A (Item 2) ---
    # Most important for sentiment — management's own narrative
    try:
        sections["mdna"] = tenq["Part I, Item 2"]
    except (KeyError, TypeError):
        sections["mdna"] = None

    # --- Risk Factors (Item 1A) ---
    try:
        sections["risk_factors"] = tenq["Part II, Item 1A"]
    except (KeyError, TypeError):
        sections["risk_factors"] = None

    # --- Financial Statements (Item 1) ---
    financials = tenq.financials
    if financials:
        sections["income_statement"] = financials.income_statement
        sections["balance_sheet"] = financials.balance_sheet
        sections["cash_flow"] = financials.cash_flow_statement
    else:
        sections["income_statement"] = None
        sections["balance_sheet"] = None
        sections["cash_flow"] = None

    # --- Metadata ---
    sections["metadata"] = {
        "ticker": ticker,
        "company_name": filing.company,
        "period_of_report": filing.period_of_report,
        "filed": str(filing.filing_date),
        "accession_number": filing.accession_number,
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


# --- Example usage ---
if __name__ == "__main__":
    sections = get_10q_sections("AAPL")
    print_section_preview(sections)