# Prompt 3 - Enricher Skill (Name + Icebreaker)

Paste this into Claude Code:

---

Now let's enrich our leads with personalized icebreakers using AI.

Before building, ask me:
1. What's my offer in one sentence? (so the AI knows the context but does NOT mention it in the icebreaker)
2. What language? (default: French. Just confirm or tell me otherwise)

Then create a Claude Code skill called `enrich` that shortens company names and generates personalized icebreakers.

## Skill structure

IMPORTANT: Create all files relative to THIS project directory (the one containing this CLAUDE.md). Do NOT create them in a parent repository.

Create these two files:

### `.claude/skills/enrich/SKILL.md`

Frontmatter:
```yaml
---
name: enrich
description: Casualize company names + generate icebreakers. Reads data/leads_with_emails.json, outputs data/leads_enriched.json
user-invocable: true
argument-hint: [--leads path] [--output path]
---
```

Body: instructions telling Claude to run the Python script, then display the summary.

### `.claude/skills/enrich/enrich.py`

Python script that:
- Reads a JSON file of leads (--leads, default `data/leads_with_emails.json`)
- Writes enriched leads to --output (default `data/leads_enriched.json`)
- For each lead: uses Claude (claude-haiku-4-5-20251001) to do TWO things in one API call:
  1. Shorten the company name -> field: `shortened_name`
  2. Generate a 1-sentence icebreaker -> field: `personalization`
- Returns JSON: `{"shortened_name": "...", "personalization": "...", "verdict": true/false}`
- If `verdict` is false (data too thin), set `personalization` to ""

**Available data per lead (tell the model exactly what it receives):**
The model receives these fields for each lead:
- `company_name` - full business name from Google Maps
- `city`, `address` - location
- `phone`, `website` - contact info
- `rating` - Google Maps rating (e.g. 4.2)
- `reviews_count` - number of Google reviews (e.g. 187)
- `website_intel.title` - the `<title>` tag from their website
- `website_intel.meta_description` - their site's meta description
- `website_intel.body_preview` - first ~300 chars of their homepage

The website_intel fields are the RICHEST and MOST IMPORTANT source. The icebreaker MUST reference what the business actually does, their specialty, or their positioning - NOT their Google review stats.

**Casualize name rules (bake into system prompt):**
- Remove legal suffixes: SAS, SARL, SA, EURL, SCI, LLC, Inc, Ltd
- Shorten location names: "Paris République" -> "Répu", "Bordeaux Centre" -> "Bordeaux"
- Remove generic words: "Salle de Sport", "Centre de", "Club de"
- Example: "Basic-Fit Paris République SAS" -> "Basic-Fit Répu"
- Example: "Salle de Sport Liberty Gym Paris 10e" -> "Liberty Gym"

**Icebreaker rules (IMPORTANT - bake into system prompt):**

The Litmus Test: "Would a real person text this to a friend?" If yes, keep it. If it reads like a LinkedIn recommendation, rewrite it.

CRITICAL RULE: NEVER write an icebreaker that just cites Google review numbers. "Vous avez X avis avec une note de Y" is LAZY and GENERIC. Anyone can see that. The prospect knows their own stats. Reference what they DO, not their metrics.

What to reference (strict priority order - use the HIGHEST available):
1. **Their specialty or unique service** (from website_intel) - what makes them different from competitors. THIS IS THE BEST SIGNAL.
2. **Their positioning or target audience** (from website_intel) - who they serve, their approach
3. **Something concrete from their site** (from body_preview) - a specific program, method, or offering
4. **Their niche combined with a market insight** - connect what they do to a trend
5. **Google reviews as SUPPORTING detail only** - never as the main point. OK to combine: "Spécialisés en implanto avec 4.8 sur Google, le bouche-à-oreille fait clairement le job." NOT OK alone: "1073 avis avec une 4.6"
6. If ALL data is thin (no website_intel, no useful info): set verdict to false

Format template (follow this structure):
```
{observation casual sur leur business}. {réaction courte positive}.
```
Examples of the pattern:
- "J'ai vu que..." / "Cool le..." / "Sympa l'..." -> observation
- "...beau créneau." / "...ça change." / "...on voit pas ça souvent." -> réaction

Rules:
- 1 sentence max (2 short fragments OK). Casual grammar. Slightly imperfect = more human.
- No greeting (no "Bonjour", no "Hey"). No hollow compliments. Never mention your product/service.
- Reference something concrete and specific to THIS lead.
- NEVER use em dashes. Use hyphens, commas, or periods instead.
- Abbreviations OK: "implanto" not "implantologie", "perso" not "personnalisé", "co" not "collectifs"

Good examples (include in system prompt):
- "Cool le concept coaching perso + cours co, on voit pas ça souvent."
- "J'ai vu que vous faites de l'implanto à Lyon, beau créneau."
- "Le côté salle + espace bien-être c'est top, ça change."
- "Sympa l'approche cours adaptés seniors, y'a clairement un truc là."
- "J'ai regardé votre site, le positionnement haut de gamme ça se voit direct."

The pattern: casual observation + short positive reaction. Like you'd text a friend after checking out their business. No analysis, no market commentary.

Bad examples (include as "never write"):
- "1073 avis Google avec une 4.6, c'est impressionnant." (LAZY - just citing stats anyone can see)
- "460 avis avec une 4.6, c'est rare pour un cabinet dentaire." (still just stats)
- "J'admire la passion que vous mettez dans votre travail." (hollow, LinkedIn slop)
- "J'ai lu votre mission d'entreprise et je trouve votre approche inspirante." (AI slop)
- "Votre entreprise fait un travail incroyable dans le secteur." (useless)
- "C'est un segment qui décolle vraiment en ce moment." (sounds like a market analyst, not a human)
- "C'est un marché énorme en ce moment." (same - too analytical)

**Technical:**
- Filter: only process leads that have a non-empty `email` field
- Reads `ANTHROPIC_API_KEY` from environment (load .env if present)
- Prints progress: `[1/5] Liberty Gym -> "342 avis Google avec une 4.1..."` or `[1/5] Gym XYZ -> skipped (thin data)`
- Prints summary at end: "Done. X/Y icebreakers generated (Z skipped - thin data)"

After creating both files:
1. Update the project CLAUDE.md to document the new `/enrich` skill
2. Run a test: `/enrich`
3. Then tell me: "Step 3 done! Your leads now have personalized icebreakers in data/leads_enriched.json. Ready for step 4? Paste prompt 04-save-to-sheets.md to save everything to a Google Sheet for review."
