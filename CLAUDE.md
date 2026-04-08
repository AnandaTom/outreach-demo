# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## What this repo is

A set of prompts that build a cold email outreach pipeline step by step. Each `.md` file at the root is a prompt to paste into Claude Code — it builds one Python skill.

## Guardrails

- All Python scripts: use `argparse`, load `.env` with `python-dotenv`, print progress to stdout
- All scripts read from / write to `data/` directory (create if missing)
- Never hardcode API keys — always `os.environ`
- SKILL.md frontmatter: only `name`, `description`, `user-invocable`, `argument-hint`

## Skill structure

```
.claude/skills/<name>/
  SKILL.md        # frontmatter + instructions for Claude
  <script>.py     # Python script with the actual logic
```

## Data flow

```
scrape        -> data/leads_raw.json
find-emails   -> data/leads_with_emails.json
enrich        -> data/leads_enriched.json
save-to-sheets -> Google Sheet
write-emails  -> data/sequence.json
push          -> Instantly campaign
```

## Stack

- Python 3.9+, deps in `requirements.txt`
- AI model: `claude-haiku-4-5-20251001`
- Instantly API v2 — Bearer auth, base URL `https://api.instantly.ai/api/v2`

## Hard-Won Rules

- `Europe/Paris` is NOT in Instantly's timezone allowlist → use `Europe/Belgrade` (same CET)
- POST /leads does NOT support batch → one request per lead, flat JSON object
- Campaign creation requires `campaign_schedule` in the body or it returns 400
