# Prompt 7 - Master Outreach Skill

Paste this into Claude Code after building all 6 individual skills:

---

Now let's consolidate everything into one clean master command.

**Architecture decision:** Delete the individual skill SKILL.md files (scrape, find-emails, enrich, save-to-sheets, write-emails, push-to-instantly). Keep the Python scripts - they contain the real logic. The master `/outreach` skill replaces all 6 entry points via `/outreach <step>`.

Result: one command in the menu instead of 7. No confusion.

## Step 1 - Cleanup

Delete these files (keep the .py scripts):
```
.claude/skills/scrape/SKILL.md
.claude/skills/find-emails/SKILL.md
.claude/skills/enrich/SKILL.md
.claude/skills/save-to-sheets/SKILL.md
.claude/skills/write-emails/SKILL.md
.claude/skills/push-to-instantly/SKILL.md
```

## Step 2 - Create the master skill

IMPORTANT: Create relative to THIS project directory (the one containing this CLAUDE.md).

### `.claude/skills/outreach/SKILL.md`

Frontmatter:
```yaml
---
name: outreach
description: Full cold email outreach pipeline. Runs all 6 steps in sequence or jump to any step. Usage: /outreach [step] [args]
user-invocable: true
argument-hint: [step] [args] - steps: scrape, find-emails, enrich, sheets, write, push, status, or "all"
---
```

### Body

The body should contain the full pipeline knowledge:

## The Pipeline

```
Step 1: scrape        -> data/leads_raw.json           (APIFY_API_KEY)
Step 2: find-emails   -> data/leads_with_emails.json   (no API key needed)
Step 3: enrich        -> data/leads_enriched.json      (ANTHROPIC_API_KEY)
Step 4: save-to-sheets -> Google Sheet URL              (GOOGLE_SERVICE_ACCOUNT_JSON)
Step 5: write-emails  -> data/sequence.json             (ANTHROPIC_API_KEY)
Step 6: push          -> Instantly campaign             (INSTANTLY_API_KEY)
```

## Usage Modes

- **`/outreach` or `/outreach all`**: Run all 6 steps in sequence. After each step, show a brief summary and ask "Continuer vers l'étape suivante ? (O/n)" before proceeding.
- **`/outreach <step>`** (e.g. `/outreach scrape "gyms Paris"`): Run only that step. Pass extra args to the script.
- **`/outreach from <step>`** (e.g. `/outreach from enrich`): Run from that step onward. Check required input files exist first.
- **`/outreach status`**: Show which data files exist and their lead counts.

## Step Details

### Step 1: Scrape
- Script: `python .claude/skills/scrape/scrape.py --search "<query>" --limit <N>`
- Requires: `APIFY_API_KEY`
- Ask for search query and limit if not provided

### Step 2: Find Emails
- Script: `python .claude/skills/find-emails/find_emails.py`
- Requires: nothing (requests + beautifulsoup4)
- Needs: `data/leads_raw.json`

### Step 3: Enrich
- Script: `python .claude/skills/enrich/enrich.py`
- Requires: `ANTHROPIC_API_KEY`
- Needs: `data/leads_with_emails.json`
- After: "Relisez les icebreakers ! Est-ce qu'un vrai humain enverrait ça ?"

### Step 4: Save to Sheets
- Script: `python .claude/skills/save-to-sheets/save_to_sheets.py`
- Requires: `GOOGLE_SERVICE_ACCOUNT_JSON`
- Needs: `data/leads_enriched.json`
- After: "Ouvrez le Google Sheet, relisez, modifiez les icebreakers qui sonnent faux, supprimez les leads sans personnalisation."

### Step 5: Write Emails
- Script: `python .claude/skills/write-emails/email_writer.py --niche "<niche>" --offer "<offer>"`
- Requires: `ANTHROPIC_API_KEY`
- Ask for niche and offer if not provided
- After: display all 4 emails and ask the user to review

### Step 6: Push to Instantly
- Script: `python .claude/skills/push-to-instantly/push_to_instantly.py --campaign "<name>"`
- Requires: `INSTANTLY_API_KEY`
- Needs: `data/leads_enriched.json` + `data/sequence.json`
- Ask for campaign name if not provided
- Prints deliverability checklist before launch prompt

## Pre-flight Checks

Before each step:
1. Check required `.env` key is set
2. Check required input file exists
3. If missing, tell user exactly what to fix

Missing key messages:
- `APIFY_API_KEY` -> "Ajoutez APIFY_API_KEY dans .env (apify.com > Settings > Integrations > API Token)"
- `ANTHROPIC_API_KEY` -> "Ajoutez ANTHROPIC_API_KEY dans .env (console.anthropic.com)"
- `GOOGLE_SERVICE_ACCOUNT_JSON` -> "Configurez Google Sheets API (voir prompts/04-save-to-sheets.md)"
- `INSTANTLY_API_KEY` -> "Ajoutez INSTANTLY_API_KEY dans .env (app.instantly.ai > Settings > API)"
- Missing input file -> "Lancez d'abord /outreach <previous_step>"

## Status Command

When `/outreach status`, read each JSON file and count entries:
```
Pipeline status:
  [x] data/leads_raw.json          (5 leads)
  [x] data/leads_with_emails.json  (5 leads)
  [x] data/leads_enriched.json     (3 leads enrichis)
  [x] data/sequence.json           (4 emails)
  [ ] Campagne Instantly           (pas encore lancée)

Prochaine étape recommandée : /outreach push
```

## Instantly API Hard-Won Rules

Discovered through testing - never ignore these:

- **Timezone**: `Europe/Paris` is NOT valid. Use `Europe/Belgrade` (same CET).
- **Lead creation**: POST /leads does NOT support batch. One request per lead, flat JSON object.
- **Days format**: string keys `{"0": true, "1": true, ...}` (0=Monday, 6=Sunday).
- **campaign_schedule**: required on creation - cannot create a campaign without it.

## Cold Email Principles (reference)

- **4-part formula**: `{{personalization}}`, preuve sociale, offre + inversion du risque, CTA avec horaire précis
- **Test litmus**: "Est-ce qu'un vrai humain enverrait ça par texto ?" Si non, réécrire.
- **Règle critique icebreaker**: jamais citer les stats Google Maps brutes. Référencer ce qu'ils FONT.
- **Word counts**: E1 75-100, E2 60-80, E3 50-70, E4 30-40
- **Sujets**: moins de 4 mots, jamais {{companyName}}, E2 = même sujet (fil), E3 = nouveau
- **Benchmarks**: 1% réponse positive = ça marche, 1-3% = solide, 3%+ = exceptionnel
- **Délivrabilité**: SPF/DKIM/DMARC, 14 jours warmup minimum, 20-30 emails/jour/compte, domaine dédié
- **Jamais écrire**: "J'espère que vous allez bien", "Notre solution", "ROI", "synergie", em dashes

---

After creating the skill and deleting the individual SKILL.md files:
1. Update the project CLAUDE.md to replace the 6 individual skill entries with just `/outreach`
2. Run `/outreach status` to confirm the pipeline state
3. Then tell me: "Pipeline complet ! Une seule commande : /outreach. Tapez /outreach all pour lancer le pipeline complet, ou /outreach status pour voir où vous en êtes."
