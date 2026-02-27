import pandas as pd
from urllib.parse import urlparse

# =========================
# Configuration
# =========================
COMPANIES_FILE = "data/companies_enriched_FINAL_CLEAN.xlsx"
PITAGONE_FILE = "data/Pitagone mailinglist.xlsx"
OUTPUT_FILE = "data/companies_enriched_WITH_PITAGONE.xlsx"


# =========================
# Helpers
# =========================
def extract_domain(url):
    if not isinstance(url, str):
        return None
    try:
        parsed = urlparse(url.lower())
        domain = parsed.netloc
        if domain.startswith("www."):
            domain = domain[4:]
        return domain
    except Exception:
        return None


# =========================
# Main
# =========================
def main():
    # Load files
    df_companies = pd.read_excel(COMPANIES_FILE)
    df_pitagone = pd.read_excel(PITAGONE_FILE)

    # Normalize domains
    df_companies["Domain"] = df_companies["Website"].apply(extract_domain)
    df_pitagone["Domain"] = df_pitagone.iloc[:, 0].astype(str).str.lower().str.strip()
    df_pitagone["Email"] = df_pitagone.iloc[:, 1].astype(str).str.strip()

    # Merge by Domain
    df_merged = df_companies.merge(
        df_pitagone[["Domain", "Email"]],
        on="Domain",
        how="left"
    )

    # Fill missing Final_Email only
    def choose_email(row):
        if pd.notna(row.get("Final_Email")):
            return row["Final_Email"]
        return row.get("Email")

    df_merged["Final_Email"] = df_merged.apply(choose_email, axis=1)

    # Cleanup
    df_merged.drop(columns=["Email", "Domain"], inplace=True)

    # Save output
    df_merged.to_excel(OUTPUT_FILE, index=False)
    print(f"✔ Done. File saved to: {OUTPUT_FILE}")


if __name__ == "__main__":
    main()
