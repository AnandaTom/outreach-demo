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
Same thing for "Google Drive API". Wait for my confirmation.

**Step 4 - Create a Service Account**
Walk me to IAM & Admin > Service Accounts > Create Service Account. Tell me to:
- Name it (e.g. "outreach-sheets")
- Click "Create and Continue"
- Skip the optional role/permissions steps
- Click "Done"
Wait for my confirmation.

**Step 5 - Download the JSON key**
Tell me to:
- Click on the service account I just created
- Go to the "Keys" tab
- Click "Add Key" > "Create New Key" > select JSON
- A file will download automatically - save it somewhere safe (NOT inside the project folder)
Wait for my confirmation.

**Step 6 - Add to .env**
Tell me to add these two lines to my `.env` file:
```
GOOGLE_SERVICE_ACCOUNT_JSON=/full/path/to/the/downloaded/file.json
SHARE_EMAIL=my@email.com
```
Wait for my confirmation.

**Step 7 - Verify**
Run a quick Python test to check the authentication works:
```python
python -c "
from google.oauth2.service_account import Credentials
from dotenv import load_dotenv
import os
load_dotenv()
creds = Credentials.from_service_account_file(
    os.environ['GOOGLE_SERVICE_ACCOUNT_JSON'],
    scopes=['https://www.googleapis.com/auth/spreadsheets', 'https://www.googleapis.com/auth/drive']
)
print(f'Service account: {creds.service_account_email}')
print('Google Sheets API access OK!')
"
```
If it fails, help me debug. If it passes, move on to building the skill.

---

Once setup is verified, create a Claude Code skill called `save-to-sheets`.

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
- Creates a brand new Google Sheet with title "Outreach - {YYYY-MM-DD}"
- Uses `gspread` + `google.oauth2.service_account` for authentication
- Reads `GOOGLE_SERVICE_ACCOUNT_JSON` from environment (path to the service account JSON file, load .env if present)

Sheet structure:
- Headers in row 1 (bold): #, Company, Short Name, Email, Phone, Website, City, Personalization
- Column A (#): row number starting at 1
- Column F (Website): use HYPERLINK formula so URLs are clickable: `=HYPERLINK(url_value, "site")` - generate this per row from the lead's website field
- Auto-resize columns to fit content
- Freeze row 1 (headers)

After creating and populating the sheet:
- If `SHARE_EMAIL` is set in .env: share the sheet with that email (as editor)
- If not set: just print the URL. Note: the user will need to open the link and the sheet will be accessible since it's created by the service account. Mention this clearly in the output.
- Print the share URL: "Sheet created: https://docs.google.com/spreadsheets/d/{id}"
- Print lead count: "X leads saved"

If authentication fails at runtime, print clear setup instructions pointing back to the 7 steps above.

After creating both files:
1. Update the project CLAUDE.md to document the new `/save-to-sheets` skill
2. Run a test: `/save-to-sheets`
3. Then tell me: "Étape 4 terminée ! Ouvrez le Google Sheet, relisez vos leads, modifiez les icebreakers qui sonnent faux. Quand c'est bon, ouvrez outreach-demo/05-email-writer.md, copiez tout le contenu, et collez-le ici."
