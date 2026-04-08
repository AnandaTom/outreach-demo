# Prompt 1 - Lead Scraper Skill

Paste this into Claude Code:

---

I want to create a cold email outreach pipeline. Let's start with step 1: scraping leads.

Before building anything, ask me:
1. What's my niche?
2. What city or region should we target?
3. How many leads do I want to start with? (recommend 20-50 for a first test)

Also check: do I have `APIFY_API_KEY` set in my `.env` file? If not, walk me through getting one at apify.com (sign up > Settings > Integrations > API Token).

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
- Uses the Apify client (`pip install apify-client`) to run the Google Places scraper (actor ID: `compass/crawler-google-places`)
- Accepts CLI args: `--search` (the query, built from my niche + city), `--limit` (default 50), `--output` (default `data/leads_raw.json`)
- Reads `APIFY_API_KEY` from environment (load .env if present)
- If APIFY_API_KEY is missing, print clear setup instructions: where to get the key, how to add it to .env

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
  "industry": "from user input"
}
```

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
1. Update the project CLAUDE.md to document the new `/scrape` skill (add it to the available commands)
2. Test it with my niche and city
3. Then tell me: "Step 1 done! You now have leads in data/leads_raw.json. Ready for step 2? Paste prompt 02-email-finder.md to find email addresses for these leads."
