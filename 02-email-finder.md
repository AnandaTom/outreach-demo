# Prompt 2 - Email Finder + Website Intel

Paste this into Claude Code:

---

Now let's find email addresses for our scraped leads by crawling their websites. This step doesn't need any API key - it just visits each website and looks for emails.

BONUS: while we're on the site, we'll also extract useful info for generating better icebreakers in step 3.

Create a Claude Code skill called `find-emails` that crawls lead websites to find emails AND extract business context.

## Skill structure

IMPORTANT: Create all files relative to THIS project directory (the one containing this CLAUDE.md). Do NOT create them in a parent repository.

Create these two files:

### `.claude/skills/find-emails/SKILL.md`

Frontmatter:
```yaml
---
name: find-emails
description: Find emails + extract website intel from lead websites. Reads data/leads_raw.json, outputs data/leads_with_emails.json
user-invocable: true
argument-hint: [--leads path] [--output path]
---
```

Body: instructions telling Claude to run the Python script, then display the summary.

### `.claude/skills/find-emails/find_emails.py`

Python script that does TWO things per website (in parallel if possible with ThreadPoolExecutor):

**1. Find email:**
- Visit the homepage
- Try common contact page paths: /contact, /nous-contacter, /contactez-nous, /contact.html, /nous-joindre
- Extract all email addresses using regex `[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}`
- Keep the first valid email found -> add as `email` field
- Prefer emails with "contact", "info", "hello", "bonjour" in the local part
- FILTER OUT junk emails: ignore emails containing "dataprivacy", "cookie", "rgpd", "dpo", "noreply", "no-reply", "unsubscribe". These are not business contact emails.

**2. Extract website intel (for icebreaker generation in step 3):**

Try multiple pages to find useful business content. Don't stop at the homepage if it's empty or junk.

Pages to crawl (in order, stop when you have good content):
1. Homepage `/`
2. About page: `/a-propos`, `/about`, `/qui-sommes-nous`, `/notre-equipe`
3. Services page: `/services`, `/nos-services`, `/prestations`, `/nos-activites`
4. Contact page (already visited for email): `/contact`, `/nous-contacter`

From each page, extract:
- `<title>` tag
- `<meta name="description">` content
- Visible body text (strip HTML tags)

Cleaning rules (IMPORTANT - filter out junk):
- SKIP content that matches: cookie consent, RGPD/GDPR notices, privacy policy text, Doctolib/booking platform boilerplate, "Accepter les cookies", "Politique de confidentialité"
- SKIP if the domain redirects to a booking platform (doctolib.fr, planity.com, treatwell.fr, etc.) - set `website_intel` to null and note "redirects to booking platform"
- Only keep the first ~300 chars of USEFUL visible text (after removing junk)

Save in a `website_intel` field on the lead:
```json
"website_intel": {
  "title": "Liberty Gym - Salle de sport Paris 10e",
  "meta_description": "Votre salle de musculation et fitness ouverte 7j/7...",
  "body_preview": "Cours collectifs, coaching perso, musculation libre, espace cardio...",
  "source_page": "/nos-services"
}
```

If no useful content found on any page, set:
```json
"website_intel": null
```

**Technical:**
- Reads a JSON file of leads (--leads, default `data/leads_raw.json`)
- Writes enriched leads to --output (default `data/leads_with_emails.json`)
- Timeout: 8 seconds per request. Skip silently on error.
- Uses `requests` + `beautifulsoup4`. No JavaScript rendering.
- Prints progress:
  - `[1/20] libertygym.fr -> email: info@libertygym.fr | intel: ok (from /nos-services)`
  - `[2/20] doctolib-redirect.fr -> email: not found | intel: null (booking platform redirect)`
  - `[3/20] example.fr -> email: contact@example.fr | intel: ok (from /a-propos)`
- After all leads: summary "Done. X/Y emails found. Z/Y websites with useful intel. W/Y had no useful content."

After creating both files:
1. Update the project CLAUDE.md to document the new `/find-emails` skill
2. Run a test: `/find-emails`
3. Then tell me: "Étape 2 terminée ! Leads avec emails dans data/leads_with_emails.json. Prêt pour l'étape 3 ? Ouvrez 03-enricher.md, copiez tout le contenu, et collez-le ici."
