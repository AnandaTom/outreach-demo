---
name: outreach
description: Full cold email outreach pipeline. Runs all 6 steps in sequence or jump to any step. Usage: /outreach [step] [args]
user-invocable: true
argument-hint: [step] [args] - steps: scrape, find-emails, enrich, sheets, write, push, status, or "all"
---

You are orchestrating a 6-step cold email pipeline. You have full knowledge of every step. When invoked, read the args and route accordingly.

---

## The Pipeline

```
Step 1: scrape        -> data/leads_raw.json           (APIFY_API_KEY)
Step 2: find-emails   -> data/leads_with_emails.json   (no API key needed)
Step 3: enrich        -> data/leads_enriched.json      (ANTHROPIC_API_KEY)
Step 4: save-to-sheets -> Google Sheet URL              (GOOGLE_SERVICE_ACCOUNT_JSON)
Step 5: write-emails  -> data/sequence.json             (ANTHROPIC_API_KEY)
Step 6: push          -> Instantly campaign             (INSTANTLY_API_KEY)
```

---

## Usage Modes

### `/outreach` or `/outreach all`
Run all 6 steps in sequence. After each step, show a brief summary and ask "Continuer vers l'étape suivante ? (O/n)" before proceeding.

### `/outreach status`
Check which data files exist and how many leads they contain. Show pipeline state clearly:
```
Pipeline status:
  [x] data/leads_raw.json          (5 leads)
  [x] data/leads_with_emails.json  (5 leads, 3 avec email)
  [x] data/leads_enriched.json     (3 leads enrichis)
  [x] data/sequence.json           (4 emails)
  [ ] Campagne Instantly           (pas encore lancée)

Prochaine étape recommandée : /outreach push
```
Do this by reading the JSON files and counting entries. If a file doesn't exist, mark it `[ ]`.

### `/outreach scrape [query] [--limit N]`
Run step 1 only. If no query provided, ask the user for niche + city + limit before running.
Command: `python .claude/skills/scrape/scrape.py --search "<query>" --limit <N>`

### `/outreach find-emails`
Run step 2 only. Check `data/leads_raw.json` exists first.
Command: `python .claude/skills/find-emails/find_emails.py`

### `/outreach enrich`
Run step 3 only. Check `data/leads_with_emails.json` exists first.
Command: `python .claude/skills/enrich/enrich.py`
After: remind the user "Relisez les icebreakers ! Est-ce qu'un vrai humain enverrait ça ?"

### `/outreach sheets`
Run step 4 only. Check `data/leads_enriched.json` exists first.
Command: `python .claude/skills/save-to-sheets/save_to_sheets.py`
After: "Ouvrez le Google Sheet, relisez vos leads. Modifiez les icebreakers qui sonnent faux. Supprimez les leads sans personnalisation."

### `/outreach write [--niche X] [--offer Y]`
Run step 5 only. If niche/offer not provided, ask the user.
Command: `python .claude/skills/write-emails/email_writer.py --niche "<niche>" --offer "<offer>"`
After: display all 4 emails and ask the user to review before continuing.

### `/outreach push [campaign_name]`
Run step 6 only. Check `data/leads_enriched.json` and `data/sequence.json` exist first.
If no campaign name provided, ask the user.
Command: `python .claude/skills/push-to-instantly/push_to_instantly.py --campaign "<name>"`

### `/outreach from <step>`
Run from the given step onward. Check that required input files exist before starting.
- `from find-emails` needs `data/leads_raw.json`
- `from enrich` needs `data/leads_with_emails.json`
- `from sheets` needs `data/leads_enriched.json`
- `from write` needs nothing (asks niche/offer)
- `from push` needs `data/leads_enriched.json` + `data/sequence.json`

---

## Pre-flight Checks

Before running any step, verify:
1. Required `.env` key is set (check with `os.environ.get`)
2. Required input file exists

If something is missing, tell the user exactly what to fix:
- Missing APIFY_API_KEY -> "Ajoutez APIFY_API_KEY dans .env (apify.com > Settings > Integrations > API Token)"
- Missing ANTHROPIC_API_KEY -> "Ajoutez ANTHROPIC_API_KEY dans .env (console.anthropic.com)"
- Missing GOOGLE_SERVICE_ACCOUNT_JSON -> "Configurez Google Sheets API (voir prompts/04-save-to-sheets.md pour le guide)"
- Missing INSTANTLY_API_KEY -> "Ajoutez INSTANTLY_API_KEY dans .env (app.instantly.ai > Settings > API)"
- Missing input file -> "Lancez d'abord /outreach <previous_step>"

---

## Instantly API Hard-Won Rules (for step 6)

These were discovered through testing - bake them into any code or guidance:

- **Timezone**: `Europe/Paris` is NOT valid. Use `Europe/Belgrade` (same CET, Instantly's allowed equivalent).
- **Lead creation**: POST /leads does NOT support batch. Send one lead per request as a flat JSON object.
- **Days format**: use string keys `{"0": true, "1": true, ...}` (0=Monday, 6=Sunday).
- **Campaign schedule**: `campaign_schedule` is required on creation - cannot create without it.

---

## Cold Email Principles (reference)

Answer questions about the process using this knowledge:

- **4-part formula**: `{{personalization}}`, preuve sociale, offre + inversion du risque, CTA avec horaire précis
- **Test litmus**: "Est-ce qu'un vrai humain enverrait ça par texto ?" Si non, réécrire.
- **Règle critique icebreaker**: jamais citer les stats Google Maps brutes (notes, nombre d'avis). Référencer ce qu'ils FONT.
- **Word counts**: E1 75-100 mots, E2 60-80, E3 50-70, E4 30-40
- **Sujets**: moins de 4 mots, jamais {{companyName}}, E2 = même sujet (fil), E3 = nouveau sujet
- **Benchmarks**: 1% réponse positive = ça marche, 1-3% = solide, 3%+ = exceptionnel
- **Délivrabilité**: SPF/DKIM/DMARC, 14 jours warmup minimum, 20-30 emails/jour/compte max, domaine dédié
- **Quality gate**: relire 5+ icebreakers avant envoi. Si ça sonne LinkedIn, réécrire.
- **Jamais écrire**: "J'espère que vous allez bien", "Notre solution", "ROI", "synergie", "Seriez-vous intéressé ?", em dashes
