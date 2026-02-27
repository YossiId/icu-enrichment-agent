import pandas as pd

from enrich import find_website
from utils import infer_country_from_domain
from page_fetcher import fetch_pages
from email_enrich import extract_email_from_soups
from country_enrich import detect_country


# =========================
# Configuration
# =========================
INPUT_FILE = "data/companies.xlsx"
OUTPUT_FILE = "data/test_output.xlsx"

MAX_ROWS = None        # None = all rows | number = test subset (e.g. 10 / 50)
PRINT_PROGRESS = True


# =========================
# Main
# =========================
def main():
    # Load data
    df = pd.read_excel(INPUT_FILE)

    # Optional limit for testing
    if MAX_ROWS:
        df = df.head(MAX_ROWS)

    # Ensure columns exist
    for col in ["Inferred_Website", "Inferred_Country",
                "Country_Confidence", "Inferred_Email"]:
        if col not in df.columns:
            df[col] = None

    # Iterate companies
    for i, row in df.iterrows():
        company = str(row.get("Company Name", "")).strip()

        if not company:
            continue

        # 1. Find website
        site = find_website(company)

        if not site:
            if PRINT_PROGRESS:
                print(f"[{i}] {company} | No valid website found")
            continue

        df.at[i, "Inferred_Website"] = site

        # 2. Fetch pages once (shared between email + country)
        soups = fetch_pages(site)

        # 3. Extract email from pre-fetched pages
        email = extract_email_from_soups(soups)
        df.at[i, "Inferred_Email"] = email

        # 4. Detect country (all signals)
        cctld_country = infer_country_from_domain(site)
        soup_list = list(soups.values())
        country, confidence = detect_country(
            company_name=company,
            website=site,
            cctld_country=cctld_country,
            soups=soup_list,
        )
        df.at[i, "Inferred_Country"] = country
        df.at[i, "Country_Confidence"] = confidence

        if PRINT_PROGRESS:
            print(f"[{i}] {company} | {site} | "
                  f"{country} ({confidence}) | {email}")

    # Save results
    df.to_excel(OUTPUT_FILE, index=False)
    print(f"\nFinished. Output saved to: {OUTPUT_FILE}")


# =========================
# Entry point
# =========================
if __name__ == "__main__":
    main()
