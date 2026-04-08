# Prompt 6 - Push to Instantly Skill

Paste this into Claude Code:

---

Final step: push everything to Instantly to start sending.

Before building, check:
1. Do I have an Instantly account? (app.instantly.ai)
2. Do I have my API key? (Settings > API > copy the key, add it as `INSTANTLY_API_KEY` in .env)
3. Do I have at least one sending account connected and warmed up? (at least 14 days of warmup)

If I'm missing anything, walk me through the setup. Then create a Claude Code skill called `push-to-instantly`.

## Skill structure

IMPORTANT: Create all files relative to THIS project directory (the one containing this CLAUDE.md). Do NOT create them in a parent repository.

Create these two files:

### `.claude/skills/push-to-instantly/SKILL.md`

Frontmatter:
```yaml
---
name: push-to-instantly
description: Push leads + email sequence to Instantly campaign. Usage: /push-to-instantly <campaign_name>
user-invocable: true
argument-hint: <campaign_name> [--leads path] [--sequence path]
---
```

Body: instructions telling Claude to run the Python script with the campaign name, then display the results and pre-launch checklist.

### `.claude/skills/push-to-instantly/push_to_instantly.py`

Python script that:
- Reads `INSTANTLY_API_KEY` from environment (load .env if present)
- Uses Instantly API v2: base URL `https://api.instantly.ai/api/v2`, auth via `Authorization: Bearer <api_key>` header on every request
- Accepts CLI args: `--leads` (default `data/leads_enriched.json`), `--campaign` (campaign name), `--sequence` (default `data/sequence.json`)

Steps:
1. List existing campaigns (GET /campaigns?limit=100). Check if campaign with `--campaign` name already exists.
2. If not exists: create it (POST /campaigns) with body: `{"name": "...", "campaign_schedule": {"schedules": [{"name": "Default", "timing": {"from": "08:00", "to": "18:00"}, "days": {"0": true, "1": true, "2": true, "3": true, "4": true, "5": false, "6": false}, "timezone": "Europe/Belgrade"}]}}`
   **IMPORTANT - timezone**: `Europe/Paris` is NOT in Instantly's allowed list. Use `Europe/Belgrade` (same CET timezone, fully equivalent).
3. Set the email sequence on the campaign (PATCH /campaigns/{id}) with `sequences` field - list of steps with type "email", delay (0, 4, 9, 14 days), and variants (subject + body)
4. Filter leads: only those with non-empty `email` AND non-empty `personalization` field
5. Add filtered leads (POST /leads) - **one request per lead** (the API does NOT support batch). For each lead, POST a flat JSON object: `{"email": ..., "first_name": "", "last_name": "", "company_name": shortened_name, "personalization": ..., "website": ..., "phone": ..., "campaign_id": ..., "skip_if_in_workspace": true}`. Print `+ email@domain` on success, `! email@domain -> skipped (reason)` on error.
6. Print: "Added X leads to campaign 'NAME' (ID: xxx)"
7. Print the deliverability checklist (see below)
8. Ask user: "Launch campaign now? (y/N)" - if yes, POST /campaigns/{id}/launch. This starts sending emails according to the schedule (08:00-18:00, Mon-Fri, Europe/Paris).

Deliverability checklist (print before the launch prompt):
```
--- Pre-launch checklist ---
Before launching, make sure:
[ ] DNS records configured: SPF, DKIM, DMARC on your sending domain
[ ] Domain warmed up: at least 14 days of warmup before sending at scale
[ ] Sending volume: start at 20-30 emails/day/account, max 50
[ ] Read every email out loud (brain autocorrects silent reads)
[ ] Preview 3+ random leads - check for broken {{variables}}, ALL CAPS names, AI slop icebreakers
[ ] Reply notifications are set up in Instantly
```

Bonus: if `--sequence` not provided, just create/update the campaign with leads only (no sequence step).

After creating both files:
1. Update the project CLAUDE.md to document the new `/push-to-instantly` skill
2. Run a test with my campaign name
3. Then tell me: "Les 6 skills sont construits ! Pour tout consolider en une seule commande /outreach, ouvrez outreach-demo/07-outreach-master.md, copiez tout le contenu, et collez-le ici."
