# Prompt 1 - Lead Scraper Skill

Paste this into Claude Code:

---

I want to build a cold email outreach pipeline. Let's start with step 1: scraping leads.

## Step 0 — Get all the prompts

Clone the repo into a temp location and copy the prompt files into this project:
```bash
rm -rf /tmp/outreach-demo-prompts && git clone https://github.com/AnandaTom/outreach-demo.git /tmp/outreach-demo-prompts && cp /tmp/outreach-demo-prompts/0*.md .
```
This copies all 7 prompt files (`01-scraper.md` through `07-outreach-master.md`) directly into your current project directory.

## Setup (run this first, before anything else)

**1. Create `requirements.txt`** in the current directory with these dependencies:
```
apify-client
requests
beautifulsoup4
anthropic
gspread
google-auth
google-auth-oauthlib
python-dotenv
```

**2. Install dependencies:**
```bash
python3 -m pip install -r requirements.txt
```
Run this now and wait for it to finish before continuing.

**3. Create `.env`** if it doesn't already exist. Check first — if it exists, leave it as-is. If not, create it with this content:
```
# Apify - lead scraping (apify.com)
APIFY_API_KEY=

# Anthropic - AI icebreakers + emails (console.anthropic.com)
ANTHROPIC_API_KEY=

# Google Sheets - save leads for review
GOOGLE_SERVICE_ACCOUNT_JSON=
SHARE_EMAIL=

# Instantly - email sending (app.instantly.ai/settings/api)
INSTANTLY_API_KEY=
```

**4. Check `APIFY_API_KEY`:** Read the `.env` file and check if `APIFY_API_KEY` has a value. If it's empty, walk me through getting one:
- Go to apify.com and sign up (free tier available)
- Settings > Integrations > API Token
- Copy the token and add it to `.env`: `APIFY_API_KEY=your_token_here`

Wait for me to confirm the key is set before continuing.

---

## Step 1 - Scrape leads

Once setup is done, ask me:
1. What's my niche?
2. What city or region should we target?
3. How many leads do I want to start with? (recommend 20-50 for a first test)

Once I answer, create a Claude Code skill called `scrape` that scrapes leads from Google Maps via Apify.

## Skill structure

IMPORTANT: Create all files relative to THIS project directory (the one containing this CLAUDE.md). Do NOT create them in a parent repository.

Create these two files:

### `.claude/skills/scrape/SKILL.md`

Frontmatter:
```yaml
---
name: scrape
description: Scrape leads from Google Maps via Apify. Usage: /scrape <search query> [--limit N]
user-invocable: true
argument-hint: <search_query> [--limit N]
---
```

Body: instructions telling Claude to run the Python script below with the user's arguments, then display the quality report.

### `.claude/skills/scrape/scrape.py`

Python script that:
- Uses the Apify client to run the Google Places scraper (actor ID: `compass/crawler-google-places`)
- Accepts CLI args: `--search` (the query, built from niche + city), `--limit` (default 50), `--output` (default `data/leads_raw.json`)
- Reads `APIFY_API_KEY` from environment (load .env with python-dotenv)
- If `APIFY_API_KEY` is missing or empty, print clear setup instructions and exit

Normalization - map each Apify result to this standard schema:
```json
{
  "company_name": "Business Name",
  "phone": "+33145678900",
  "website": "https://example.com",
  "city": "Paris",
  "address": "12 Rue Example, 75010 Paris",
  "rating": 4.2,
  "reviews_count": 187,
  "industry": "set from --industry arg"
}
```

The script must accept a `--industry` CLI arg (e.g. `--industry "gyms"`) and stamp every normalized lead with that value. Derive it from the user's niche answer if not explicitly passed.

Filtering:
- Only keep leads with a non-empty `website` field (no website = can't find email in step 2)
- Strip trailing slashes from website URLs

Quality audit (run automatically after scraping):
- Sample 25 random leads (or all if fewer than 25)
- Print a quality report: how many have website, phone, city, reviews
- Print 3 random lead samples so the user can eyeball quality
- Print warning if <80% of leads pass all fields

Progress output:
- "Running Apify actor compass/crawler-google-places..."
- "Actor finished. X raw results."
- "After filtering: Y leads with website (Z removed)"
- Quality report + 3 samples
- "Saved Y leads to data/leads_raw.json"

After creating both files:
1. Update `CLAUDE.md` in the project root to add the `/scrape` skill to the Available Skills table (create it if it doesn't exist)
2. Test it with my niche and city
3. Then tell me: "Étape 1 terminée ! Leads dans data/leads_raw.json. Prêt pour l'étape 2 ? Ouvrez 02-email-finder.md, copiez tout le contenu, et collez-le ici."
