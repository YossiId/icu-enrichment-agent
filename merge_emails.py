import pandas as pd

# =========================
# Configuration
# =========================
COMPANIES_FILE = "data/companies_enriched.xlsx"
EMAILS_FILE = "data/exhibition_emails.xlsx"
OUTPUT_FILE = "data/companies_enriched_final.xlsx"

# =========================
# Helpers
# =========================
def normalize_company(name):
    if not isinstance(name, str):
        return ""
    return (
        name.lower()
        .replace("&", "and")
        .replace(".", "")
        .replace(",", "")
        .strip()
    )

def normalize_email(email):
    if not isinstance(email, str):
        return None
    return email.strip().lower()

# =========================
# Main
# =========================
def main():
    df_companies = pd.read_excel(COMPANIES_FILE)
    df_emails = pd.read_excel(EMAILS_FILE)

    # Normalize
    df_companies["Company_norm"] = df_companies["Company Name"].apply(normalize_company)
    df_emails["Company_norm"] = df_emails["Company Name"].apply(normalize_company)
    df_emails["Email"] = df_emails["Email"].apply(normalize_email)

    # Merge
    df = df_companies.merge(
        df_emails[["Company_norm", "Email"]],
        on="Company_norm",
        how="left"
    )

    df.rename(columns={"Email": "External_Email"}, inplace=True)

    # Final email logic
    def choose_email(row):
        if pd.notna(row.get("Inferred_Email")):
            return row["Inferred_Email"]
        return row.get("External_Email")

    df["Final_Email"] = df.apply(choose_email, axis=1)

    # Drop helper column
    df.drop(columns=["Company_norm"], inplace=True)

    # Save
    df.to_excel(OUTPUT_FILE, index=False)
    print(f"✔ Final file created: {OUTPUT_FILE}")

if __name__ == "__main__":
    main()
