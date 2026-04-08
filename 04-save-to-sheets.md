# Prompt 4 - Save to Google Sheet Skill

Paste this into Claude Code:

---

Now let's save our enriched leads to a Google Sheet so we can review and edit them before sending.

Before building the skill, I need to set up Google Sheets API access. Walk me through it step by step. Wait for me to confirm each step before moving to the next.

## Step-by-step setup (guide me through each one)

**Step 1 - Google Cloud Console**
Tell me to go to https://console.cloud.google.com and either create a new project or select an existing one. Wait for my confirmation.

**Step 2 - Enable Google Sheets API**
Tell me to go to APIs & Services > Library, search for "Google Sheets API", and click Enable. Wait for my confirmation.

**Step 3 - Enable Google Drive API**
Same thing for "Google Drive API". This is required - without it, gspread can't create new spreadsheets. Wait for my confirmation.

**Step 4 - Create OAuth credentials (Desktop app)**
Walk me to APIs & Services > Credentials > Create Credentials > OAuth 2.0 Client ID. Tell me to:
- Application type: "Desktop app"
- Name: anything (e.g. "outreach-desktop")
- Click Create
Wait for my confirmation.

> NOTE: Do NOT use Service Account keys. Many Google Workspace orgs block service account key creation via org policy (`iam.disableServiceAccountKeyCreation`). OAuth Desktop App always works.

**Step 5 - Download and place the JSON**
Tell me to:
- Click the download icon next to the credential I just created
- A JSON file downloads (name starts with `client_secret_...`)
- Move it into the project folder (same level as `.env`)
Wait for me to confirm and tell me the filename.

**Step 6 - Add to .env**
Tell me to add these two lines to my `.env` file (use the actual filename from step 5):
```
GOOGLE_OAUTH_JSON=client_secret_XXXXX.apps.googleusercontent.com.json
SHARE_EMAIL=my@email.com
```
Wait for my confirmation.

**Step 7 - Set up OAuth consent screen (if prompted)**
If Google asks for a consent screen, tell me to:
- Go to APIs & Services > OAuth consent screen
- User type: External
- Fill app name + support email (anything)
- Skip scopes, skip test users
- Click Save
This is a one-time setup. Wait for my confirmation.

**Step 8 - Verify by running the skill**
After the skill is built, we'll verify by running `/save-to-sheets`. On first run, it opens a browser for OAuth authorization. This is normal - tell me to authorize and then confirm it worked.

---

Once setup steps 1-7 are confirmed, create a Claude Code skill called `save-to-sheets`.

## Skill structure

IMPORTANT: Create all files relative to THIS project directory (the one containing this CLAUDE.md). Do NOT create them in a parent repository.

Create these two files:

### `.claude/skills/save-to-sheets/SKILL.md`

Frontmatter:
```yaml
---
name: save-to-sheets
description: Save enriched leads to a new Google Sheet. Reads data/leads_enriched.json
user-invocable: true
argument-hint: [--leads path]
---
```

Body: instructions telling Claude to run the Python script, then display the sheet URL.

### `.claude/skills/save-to-sheets/save_to_sheets.py`

Python script that:
- Reads a JSON file of enriched leads (--leads, default `data/leads_enriched.json`)
- Only saves leads that have a non-empty `email` field
- Creates a brand new Google Sheet with title "Outreach - {YYYY-MM-DD}"
- Uses `gspread.oauth(credentials_filename=path)` for authentication (OAuth Desktop App)
  - `path` = value of `GOOGLE_OAUTH_JSON` env var (load .env with python-dotenv)
  - On first run: opens browser for authorization. Token cached automatically after.

Sheet structure:
- Headers in row 1 (bold): #, Company, Short Name, Email, Phone, Website, City, Personalization
- Column A (#): row number starting at 1
- Column F (Website): store as plain URL string (NOT a HYPERLINK formula - formulas use locale-specific separators and break on French locale Sheets)
- Auto-resize columns to fit content
- Freeze row 1 (headers)

**CRITICAL - Encoding workaround (gspread 6.x + Python 3.14 bug):**
gspread's `update()` method double-encodes UTF-8 strings as Latin-1 (é -> Ã©). Bypass it completely by writing values directly to the Sheets API v4 REST endpoint using the `requests` library:
```python
import requests as http_requests
from google.auth.transport.requests import Request as GoogleRequest

creds = gc.http_client.auth
if not creds.valid:
    creds.refresh(GoogleRequest())
resp = http_requests.put(
    f"https://sheets.googleapis.com/v4/spreadsheets/{sh.id}/values/A1",
    params={"valueInputOption": "RAW"},
    json={"values": [HEADERS] + rows},
    headers={"Authorization": f"Bearer {creds.token}"},
)
resp.raise_for_status()
```
Never use `ws.update()` or `ws.append_rows()` - they trigger the encoding bug.

**CRITICAL - Mojibake fixer for source data:**
Apify sometimes returns strings where UTF-8 bytes were decoded as Latin-1 ("Ã©" instead of "é"). Fix this in the `clean()` helper that sanitizes all values before writing:
```python
def clean(val):
    if not isinstance(val, str):
        return val
    # Fix Mojibake: UTF-8 bytes decoded as Latin-1
    try:
        val = val.encode("latin-1").decode("utf-8")
    except (UnicodeDecodeError, UnicodeEncodeError):
        pass
    return val.replace("\ufffd", "").replace("\xa0", " ").strip()
```
Apply `clean()` to every string field before building the rows array.

After creating and populating the sheet:
- If `SHARE_EMAIL` is set in .env: share the sheet with that email (as editor, notify=False)
- Print: "Sheet created: https://docs.google.com/spreadsheets/d/{id}"
- Print: "X leads saved"

If authentication fails, print clear instructions pointing back to the setup steps above.

After creating both files:
1. Update the project CLAUDE.md to document the new `/save-to-sheets` skill
2. Run a test: `/save-to-sheets`
3. Then tell me: "Etape 4 terminee ! Ouvrez le Google Sheet, relisez vos leads, modifiez les icebreakers qui sonnent faux. Quand c'est bon, ouvrez 05-email-writer.md, copiez tout le contenu, et collez-le ici."
