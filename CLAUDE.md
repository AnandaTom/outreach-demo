# Outreach Demo

Cold email outreach pipeline built as Claude Code skills. Each skill = SKILL.md + Python script.

## Guardrails

- **Always respond to the user in French.** Prompts and code comments stay in English, but all messages, questions, explanations, and summaries must be in French.
- All Python scripts: use `argparse`, load `.env` with `python-dotenv`, print progress to stdout
- All scripts read from / write to `data/` directory (create if missing)
- All emails and icebreakers in **French** (casual tone, "je" not "nous")
- Never hardcode API keys. Always `os.environ`
- SKILL.md frontmatter: only use `name`, `description`, `user-invocable`, `argument-hint` (other fields not supported)

## Skill Structure

When creating a skill, always create two files:
```
.claude/skills/<name>/
  SKILL.md       <- frontmatter + instructions
  <script>.py    <- Python script
```

SKILL.md format:
```yaml
---
name: skill-name
description: What this skill does. Usage: /skill-name [args]
user-invocable: true
argument-hint: <required_arg> [--optional flag]
---

Instructions for Claude on what to do when this skill is invoked.
Include: how to parse arguments, which script to run, what to display after.
```

## Data Flow

Each step produces a JSON file consumed by the next:
```
/scrape         -> data/leads_raw.json           (company_name, phone, website, city, address, rating, reviews_count)
/find-emails    -> data/leads_with_emails.json   (+ email, website_intel)
/enrich         -> data/leads_enriched.json      (+ shortened_name, personalization, verdict)
/save-to-sheets -> Google Sheet URL              (human review step)
/write-emails   -> data/sequence.json            (email1-4 with subject, body, delay)
/push-to-instantly -> Instantly campaign          (live sending)
```

## Target

- Niche: salles de sport / gyms in Paris
- Offer: Anti No-Show System (automated SMS/email reminders, 50%+ no-show reduction guaranteed)
- Language: French
- Sending: Instantly.ai

## Stack

- Python 3.9+ with deps in `requirements.txt` (run `pip install -r requirements.txt` once)
- AI model for icebreakers + emails: `claude-haiku-4-5-20251001`
- Instantly API v2 (Bearer auth, base URL `https://api.instantly.ai/api/v2`)

## Environment

`.env` keys (see `.env.example`):
- `APIFY_API_KEY` - apify.com
- `ANTHROPIC_API_KEY` - console.anthropic.com
- `GOOGLE_SERVICE_ACCOUNT_JSON` - path to service account JSON
- `INSTANTLY_API_KEY` - app.instantly.ai/settings/api

## Available Skills

| Skill | Usage | Output |
|-------|-------|--------|
| `/scrape` | `/scrape <query> [--limit N]` | `data/leads_raw.json` |
| `/find-emails` | `/find-emails [--leads path] [--output path]` | `data/leads_with_emails.json` |

## Cold Email Principles

These principles must be baked into the AI prompts (icebreaker + email writer).

### The 4-Part Formula
1. **PERSONALIZATION** - `{{personalization}}` variable. 1 sentence. "Would a real person text this?"
2. **SOCIAL PROOF** - 1 sentence. Specific client type + specific number (3.7x > "nearly 4x")
3. **OFFER + RISK REVERSAL** - prospect risks nothing. "Garanti ou vous ne payez pas."
4. **CTA** - specific time. "Ça vous va mardi à 10h ou mercredi à 14h ?"

### Icebreaker Priority Order
1. Specific company event (new location, hiring, growth)
2. Industry signal (regulation, known pain)
3. City/region with market context
4. Company specificity (niche, client type)
5. Website/review signal (Google reviews, recent activity)
6. If data too thin: set personalization to "" (skip, don't force)

### Email Sequence
- E1 (Day 1): Full formula, 75-100 words. Subject: "{{firstName}}, question"
- E2 (Day 4): Threaded (same subject). Different angle. 60-80 words.
- E3 (Day 9): New subject. Different value prop. 50-70 words.
- E4 (Day 14): Breakup. 30-40 words. End with: "je devrais contacter qui chez vous ?"

### Copywriting Levers
- **Poke the Bear**: neutral questions, not leading ("Comment vous gérez..." not "Vous avez du mal...")
- **Risk Reversal**: "je ne facture rien tant que...", "garanti ou vous ne payez pas"
- **"So What?" Test**: push claims to second-order effects
- **Real Numbers**: 3.7x, 143 503 EUR (never round, never approximate)

### Never Write
- "J'espère que vous allez bien" / "Je m'appelle X et je suis..."
- "Notre solution" / "Notre plateforme" (use "je")
- "ROI", "synergie", "optimisation", "levier" (corporate jargon)
- "Seriez-vous intéressé ?" (too vague)
- Over 100 words on any email
- More than 4 emails in sequence

### Subject Lines
- Under 4 words. Never {{companyName}} in subject.
- E2 = same as E1 (threaded). E3 = completely new.

### Benchmarks
- 1% positive reply = working. 1-3% = solid. 3%+ = exceptional.
- Quality gate: review 5+ icebreakers. "Would a real person text this?"
