import pandas as pd
from urllib.parse import urlparse

# =========================
# FILE PATHS
# =========================
BASE_FILE = r"C:\Users\joeid\Projects\ICU\enrichment_agent\data\companies_enriched_FINAL_CLEAN.xlsx"
PITAGONE_FILE = r"C:\Users\joeid\Downloads\Wesco Anixter\ICU\תערוכות וגנטים 2026\Pitagone mailinglist.xlsx"
OUTPUT_FILE = r"C:\Users\joeid\Projects\ICU\enrichment_agent\data\companies_merged_FINAL.xlsx"

# =========================
# HELPERS
# =========================
def clean_domain(url):
    if not isinstance(url, str) or url.strip() == "":
        return None
    url = url.strip().lower()
    if not url.startswith("http"):
        url = "http://" + url
    parsed = urlparse(url)
    domain = parsed.netloc.replace("www.", "")
    return domain

# =========================
# MAIN
# =========================
def main():
    df_base = pd.read_excel(BASE_FILE)
    df_pita = pd.read_excel(PITAGONE_FILE)

    # normalize domains
    df_base["domain_clean"] = df_base["Website"].apply(clean_domain)
    df_pita["domain_clean"] = df_pita["Website"].apply(clean_domain)

    # group emails by domain
    pita_grouped = (
        df_pita.groupby("domain_clean")["Email"]
        .apply(lambda x: ", ".join(sorted(set(e for e in x if isinstance(e, str)))))
        .reset_index()
    )

    # merge
    df_merged = df_base.merge(
        pita_grouped,
        on="domain_clean",
        how="left"
    )

    # add rows for domains not in base
    missing_domains = pita_grouped[
        ~pita_grouped["domain_clean"].isin(df_base["domain_clean"])
    ]

    if not missing_domains.empty:
        extra_rows = pd.DataFrame({
            "Company Name": missing_domains["domain_clean"],
            "Website": missing_domains["domain_clean"],
            "Email": missing_domains["Email"]
        })
        df_merged = pd.concat([df_merged, extra_rows], ignore_index=True)

    # cleanup
    df_merged.drop(columns=["domain_clean"], inplace=True)

    df_merged.to_excel(OUTPUT_FILE, index=False)
    print(f"✔ File created: {OUTPUT_FILE}")

if __name__ == "__main__":
    main()
