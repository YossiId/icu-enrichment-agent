import pandas as pd
from urllib.parse import urlparse

# ===== PATHS =====
COMPANIES_FILE = r"C:\Users\joeid\Projects\ICU\enrichment_agent\data\companies_enriched_FINAL_CLEAN.xlsx"
PITAGONE_FILE = r"C:\Users\joeid\Downloads\Wesco Anixter\ICU\תערוכות וגנטים 2026\Pitagone mailinglist.xlsx"
OUTPUT_FILE = r"C:\Users\joeid\Projects\ICU\enrichment_agent\data\companies_merged_FINAL.xlsx"


def extract_domain(url):
    if not isinstance(url, str):
        return None
    if "://" not in url:
        url = "http://" + url
    return urlparse(url).netloc.replace("www.", "").lower()


def main():
    df_main = pd.read_excel(COMPANIES_FILE)
    df_ext = pd.read_excel(PITAGONE_FILE, header=None)
    df_ext.columns = ["Domain", "Email"]

    # normalize
    df_main["Domain"] = df_main["Website"].apply(extract_domain)
    df_ext["Domain"] = df_ext["Domain"].str.lower().str.strip()
    df_ext["Email"] = df_ext["Email"].str.lower().str.strip()

    # group emails per domain
    email_map = (
        df_ext.groupby("Domain")["Email"]
        .apply(lambda x: ", ".join(sorted(set(x))))
        .to_dict()
    )

    # attach emails to existing rows
    df_main["Email"] = df_main["Domain"].map(email_map)

    # find domains missing in main file
    missing_domains = set(email_map.keys()) - set(df_main["Domain"].dropna())

    # add new rows for missing domains
    new_rows = []
    for d in missing_domains:
        new_rows.append({
            "Company Name": d,
            "Website": d,
            "Country": "",
            "Email": email_map[d]
        })

    if new_rows:
        df_main = pd.concat([df_main, pd.DataFrame(new_rows)], ignore_index=True)

    df_main.drop(columns=["Domain"], inplace=True)
    df_main.to_excel(OUTPUT_FILE, index=False)
    print("✔ Finished:", OUTPUT_FILE)


if __name__ == "__main__":
    main()
