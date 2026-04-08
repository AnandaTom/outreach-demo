# Prompt 5 - Email Writer Skill

Paste this into Claude Code:

---

Now let's write the cold email sequence that will be sent to our leads.

Before building, ask me:
1. What's my niche? (e.g. gyms, dental, real estate, agencies...)
2. What's my offer? Describe it in 1-2 sentences (e.g. "I reduce no-shows by 50%+ with automated SMS reminders")
3. What language? (e.g. French, English)
4. What name should we sign the emails with? (your first name)
5. Do I have a case study or result I can mention? (e.g. "helped a gym reduce no-shows from 30% to 12%"). If not, the script will generate credible but generic social proof based on the niche.

Then create a Claude Code skill called `write-emails` that generates a 4-email cold outreach sequence.

## Skill structure

IMPORTANT: Create all files relative to THIS project directory (the one containing this CLAUDE.md). Do NOT create them in a parent repository.

Create these two files:

### `.claude/skills/write-emails/SKILL.md`

Frontmatter:
```yaml
---
name: write-emails
description: Generate a 4-email cold outreach sequence in French. Usage: /write-emails <niche> <offer>
user-invocable: true
argument-hint: <niche> <offer> [--output path]
---
```

Body: instructions telling Claude to run the Python script with the user's niche and offer arguments, then display the generated emails.

### `.claude/skills/write-emails/email_writer.py`

Python script that:
- Accepts CLI args: `--niche` (e.g. "gyms"), `--offer` (e.g. "no-show"), `--output` (default `data/sequence.json`)
- Generates a 4-email cold outreach sequence in French using Claude (claude-haiku-4-5-20251001)
- Reads `ANTHROPIC_API_KEY` from environment (load .env if present)

## The 4-Part Email Formula (bake into the system prompt)

Every cold email follows this structure:

1. **PERSONALIZATION** - `{{personalization}}` variable (pre-generated per lead). 1 sentence. Sounds like a real person texted it.
2. **SOCIAL PROOF** - Who you are + what you've done. 1 sentence. Specific client type + specific number (3.7x beats "nearly 4x").
3. **OFFER + RISK REVERSAL** - Too good to be true. Prospect risks nothing. "Je ne facture rien tant que..." / "Garanti ou vous ne payez pas."
4. **CTA** - Specific time. "Ça vous va mardi à 10h ou mercredi à 14h ?" Never vague.

## The 4-Email Arc (bake into the system prompt)

- **E1 (Day 1):** Full 4-part formula. Start with `{{personalization}}` on first line. Subject: "{{firstName}}, question" or variations. **75-100 words MAX (75 ideal).**
- **E2 (Day 4):** Threaded reply (same subject as E1). Different angle - deeper proof, different pain point, or poke-the-bear question. **60-80 words.**
- **E3 (Day 9):** New subject line. Different value prop OR lower-friction CTA ("15 min?"). **50-70 words.**
- **E4 (Day 14):** Breakup. **30-40 words max.** Must end with: "Si c'est pas vous qui gérez ça, je devrais contacter qui chez vous ?"

## Copywriting Levers (bake into the system prompt)

**Poke the Bear (Josh Braun):** Don't ask leading questions that put them on defense. Ask neutral questions that surface a problem they haven't articulated.
- Weak: "Vous avez beaucoup de no-shows ?"
- Strong: "Comment vous gérez les créneaux perdus quand quelqu'un ne se pointe pas sans prévenir ?"

**Risk Reversal:** All risk on you. Prospect risks nothing.
- "Je ne facture rien tant que vous n'avez pas vu les résultats."
- "Garanti ou vous ne payez pas."
- "Je le configure pour vous en avance, sans engagement."

**"So What?" Test:** Push every claim to its second-order effect.
- "On automatise vos rappels" -> so what? -> "Ça réduit vos no-shows de 50%+, ce qui vous récupère plusieurs heures de créneaux/semaine."

**Social Proof with Real Numbers:** Specific numbers are more credible. 3.7x beats "nearly 4x". 143 503 EUR beats "~140K".

**Chunking Up/Down:**
- Up: "On gère vos relances de RDV" -> "Vous récupérez plusieurs heures de créneaux par semaine"
- Down: "On configure tout, vous ne touchez à rien. Pas de contrat long terme. En place en 48h."

## Subject Line Rules (bake in)

- Under 4 words always outperforms
- Go-to formats: "{{firstName}}, question" / "{{firstName}} ?" / "question rapide" / "une idee"
- NEVER personalize with {{companyName}} in subject (reduces open rates)
- E2 subject = same as E1 (threaded reply)
- E3 subject = new, unrelated to E1
- Keep capitalization minimal - "question rapide" not "Question Rapide"

## Banned Phrases (bake in as "NEVER WRITE")

- "J'espère que vous allez bien" / "J'espère que cet email vous trouve en forme" - bannit
- "Je m'appelle X et je suis..." - never introduce yourself in line 1
- "Notre plateforme", "Notre solution" - use "je" not "nous"
- "ROI", "synergie", "optimisation", "levier" - corporate jargon interdit
- "Seriez-vous intéressé ?" - too vague, always use specific time CTA
- "Merci de votre temps" - never
- "Cordialement" - sign off with first name only
- Plus de 100 mots on any email
- Plus de 4 emails in the sequence
- Fausse urgence ("il reste 2 places")
- Em dashes (--)

## Output format

JSON with keys email1/email2/email3/email4, each with `subject`, `body`, and `delay` (days: 0, 4, 9, 14).
Also pretty-print to terminal so the user can review.

After creating both files:
1. Update the project CLAUDE.md to document the new `/write-emails` skill
2. Run a test with my niche and offer
3. Display all 4 emails so I can review them
4. Then tell me: "Étape 5 terminée ! Séquence 4 emails dans data/sequence.json. Relisez les emails ci-dessus. Ouvrez cette page, copiez tout le contenu, et collez-le ici : https://github.com/AnandaTom/outreach-demo/blob/master/prompts/06-push-to-instantly.md"
