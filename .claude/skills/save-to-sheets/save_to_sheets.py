#!/usr/bin/env python3
"""Save enriched leads to a new Google Sheet."""

import argparse
import json
import os
import sys
from datetime import date
from pathlib import Path

from dotenv import load_dotenv

load_dotenv()

SCOPES = [
    "https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/drive",
]

HEADERS = ["#", "Company", "Short Name", "Email", "Phone", "Website", "City", "Personalization"]


def get_credentials():
    sa_path = os.environ.get("GOOGLE_SERVICE_ACCOUNT_JSON")
    if not sa_path:
        print("ERROR: GOOGLE_SERVICE_ACCOUNT_JSON not set in .env")
        print()
        print("Setup required:")
        print("  1. console.cloud.google.com > create/select project")
        print("  2. Enable Google Sheets API + Google Drive API")
        print("  3. IAM & Admin > Service Accounts > Create Service Account")
        print("  4. Keys tab > Add Key > JSON > download file")
        print("  5. Add to .env: GOOGLE_SERVICE_ACCOUNT_JSON=/path/to/key.json")
        sys.exit(1)

    if not Path(sa_path).exists():
        print(f"ERROR: Service account file not found: {sa_path}")
        print("Check the path in your .env file.")
        sys.exit(1)

    try:
        from google.oauth2.service_account import Credentials
        return Credentials.from_service_account_file(sa_path, scopes=SCOPES)
    except Exception as e:
        print(f"ERROR: Failed to load credentials: {e}")
        sys.exit(1)


def main():
    parser = argparse.ArgumentParser(description="Save enriched leads to Google Sheet")
    parser.add_argument("--leads", default="data/leads_enriched.json", help="Input leads JSON")
    args = parser.parse_args()

    input_path = Path(args.leads)
    if not input_path.exists():
        print(f"ERROR: {args.leads} not found. Run /enrich first.")
        sys.exit(1)

    with open(input_path, encoding="utf-8") as f:
        leads = json.load(f)

    if not leads:
        print("No leads found in input file.")
        sys.exit(1)

    try:
        import gspread
    except ImportError:
        print("ERROR: gspread not installed.")
        print("Run: pip install gspread google-auth")
        sys.exit(1)

    creds = get_credentials()
    gc = gspread.authorize(creds)

    title = f"Outreach - {date.today().strftime('%Y-%m-%d')}"
    print(f"Creating Google Sheet: {title}...")

    sheet = gc.create(title)
    ws = sheet.get_worksheet(0)

    # Bold headers
    ws.append_row(HEADERS)
    ws.format("A1:H1", {"textFormat": {"bold": True}})

    # Freeze row 1
    sheet.batch_update({
        "requests": [{
            "updateSheetProperties": {
                "properties": {
                    "sheetId": ws.id,
                    "gridProperties": {"frozenRowCount": 1}
                },
                "fields": "gridProperties.frozenRowCount"
            }
        }]
    })

    # Populate rows
    rows = []
    for i, lead in enumerate(leads, 1):
        website = lead.get("website", "")
        website_formula = f'=HYPERLINK("{website}","site")' if website else ""
        rows.append([
            i,
            lead.get("company_name", ""),
            lead.get("shortened_name", ""),
            lead.get("email", ""),
            lead.get("phone", ""),
            website_formula,
            lead.get("city", ""),
            lead.get("personalization", ""),
        ])

    ws.append_rows(rows, value_input_option="USER_ENTERED")

    # Auto-resize columns
    sheet.batch_update({
        "requests": [{
            "autoResizeDimensions": {
                "dimensions": {
                    "sheetId": ws.id,
                    "dimension": "COLUMNS",
                    "startIndex": 0,
                    "endIndex": len(HEADERS),
                }
            }
        }]
    })

    sheet_url = f"https://docs.google.com/spreadsheets/d/{sheet.id}"

    # Share if SHARE_EMAIL is set
    share_email = os.environ.get("SHARE_EMAIL")
    if share_email:
        sheet.share(share_email, perm_type="user", role="writer")
        print(f"Sheet shared with {share_email}")
    else:
        print("NOTE: SHARE_EMAIL not set. The sheet is owned by the service account.")
        print("You can access it by opening the URL below while logged into Google as the service account,")
        print("or set SHARE_EMAIL=your@email.com in .env and re-run.")

    print(f"\nSheet created: {sheet_url}")
    print(f"{len(leads)} leads saved")


if __name__ == "__main__":
    main()
