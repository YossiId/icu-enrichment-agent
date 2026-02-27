import pandas as pd

from enrich import find_website
from utils import is_valid_company_site, infer_country_from_domain
from email_enrich import extract_email_from_website


# =========================
# Configuration
# =========================
INPUT_FILE = "data/companies.xlsx"
OUTPUT_FILE = "data/test_output.xlsx"

MAX_ROWS = None        # None = כל הקובץ | מספר = בדיקה (למשל 10 / 50)
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
    for col in ["Inferred_Website", "Inferred_Country", "Inferred_Email"]:
        if col not in df.columns:
            df[col] = None

    # Iterate companies
    for i, row in df.iterrows():
        company = str(row.get("Company Name", "")).strip()

        if not company:
            continue

        # 1️⃣ Find website
        site = find_website(company)

        if site and is_valid_company_site(site):
            df.at[i, "Inferred_Website"] = site

            # 2️⃣ Infer country
            country = infer_country_from_domain(site)
            df.at[i, "Inferred_Country"] = country

            # 3️⃣ Extract email
            email = extract_email_from_website(site)
            df.at[i, "Inferred_Email"] = email

            if PRINT_PROGRESS:
                print(f"[{i}] {company} | {site} | {country} | {email}")

        else:
            if PRINT_PROGRESS:
                print(f"[{i}] {company} | No valid website found")

    # Save results
    df.to_excel(OUTPUT_FILE, index=False)
    print(f"\n✔ Finished. Output saved to: {OUTPUT_FILE}")


# =========================
# Entry point
# =========================
if __name__ == "__main__":
    main()



