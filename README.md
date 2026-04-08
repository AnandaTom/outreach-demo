# Cold Email Outreach Pipeline

Prompts to build a full cold email pipeline with Claude Code — step by step.

Each prompt builds one skill. Paste them in order into Claude Code.

## The Pipeline

| Prompt | Skill built | Output |
|--------|-------------|--------|
| `01-scraper.md` | `/outreach scrape` | `data/leads_raw.json` |
| `02-email-finder.md` | `/outreach find-emails` | `data/leads_with_emails.json` |
| `03-enricher.md` | `/outreach enrich` | `data/leads_enriched.json` |
| `04-save-to-sheets.md` | `/outreach sheets` | Google Sheet |
| `05-email-writer.md` | `/outreach write` | `data/sequence.json` |
| `06-push-to-instantly.md` | `/outreach push` | Instantly campaign |
| `07-outreach-master.md` | `/outreach` | Master command |

## How to use

1. Open Claude Code in any directory
2. Copy the content of `prompts/01-scraper.md`
3. Paste into Claude Code — it handles the rest
4. Repeat for each prompt in order

## API Keys needed

- `APIFY_API_KEY` — lead scraping (apify.com, free tier available)
- `ANTHROPIC_API_KEY` — AI icebreakers + emails (console.anthropic.com)
- `GOOGLE_SERVICE_ACCOUNT_JSON` — save to Google Sheets
- `INSTANTLY_API_KEY` — send emails (app.instantly.ai)
