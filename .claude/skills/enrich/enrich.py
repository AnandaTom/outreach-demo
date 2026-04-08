#!/usr/bin/env python3
"""Casualize company names + generate icebreakers via Claude Haiku."""

import argparse
import json
import os
import sys
from pathlib import Path

import anthropic
from dotenv import load_dotenv

load_dotenv()

MODEL = "claude-haiku-4-5-20251001"

# Context: what we sell (never mention in icebreaker)
OFFER_CONTEXT = "lead scraping (automated prospection de leads pour les pros)"

SYSTEM_PROMPT = f"""Tu es un expert en copywriting cold email B2B.
Tu aides à préparer une campagne de prospection pour ce service : {OFFER_CONTEXT}.

Tu NE mentionnes JAMAIS l'offre ou le service dans l'icebreaker. L'icebreaker est 100% centré sur le prospect.

Ta mission : pour chaque lead, faire DEUX choses en un seul appel :
1. Casualiser le nom de l'entreprise (shortened_name)
2. Générer un icebreaker personnalisé (personalization)

---

RÈGLES POUR LE NOM COURT (shortened_name) :
- Supprimer les suffixes légaux : SAS, SARL, SA, EURL, SCI, LLC, Inc, Ltd
- Raccourcir les noms de lieux : "Paris République" -> "Répu", "Paris 16e" -> "Paris 16"
- Supprimer les mots génériques : "Salle de Sport", "Centre de", "Club de", "Fitness Club"
- Exemples :
  - "Basic-Fit Paris République SAS" -> "Basic-Fit Répu"
  - "Salle de Sport Liberty Gym Paris 10e" -> "Liberty Gym"
  - "Aqualoft Fitness Club - Salle de sport PARIS 16" -> "Aqualoft Paris 16"

---

RÈGLES POUR L'ICEBREAKER (personalization) :

TEST LITMUS : "Est-ce qu'un vrai humain enverrait ça par texto à un ami ?" Si oui, garde. Si ça ressemble à une recommandation LinkedIn, réécris.

RÈGLE CRITIQUE : NE JAMAIS citer les statistiques Google Maps brutes. "Vous avez X avis avec une note de Y" = PARESSEUX et GÉNÉRIQUE. Le prospect connaît déjà ses propres stats. Référence ce qu'ils FONT, pas leurs métriques.

PRIORITÉ DES SIGNAUX (utilise le plus haut disponible) :
1. Leur spécialité ou service unique (depuis website_intel) - ce qui les différencie des concurrents. MEILLEUR SIGNAL.
2. Leur positionnement ou audience cible (depuis website_intel) - qui ils servent, leur approche
3. Quelque chose de concret sur leur site (body_preview) - un programme, méthode ou offre spécifique
4. Leur niche combinée à un insight marché - relie ce qu'ils font à une tendance
5. Avis Google uniquement comme DÉTAIL DE SUPPORT - jamais comme point principal
6. Si TOUTES les données sont pauvres (pas de website_intel, rien d'utile) : verdict = false

FORMAT : {{observation casual sur leur business}}. {{réaction courte positive}}.

BONS EXEMPLES :
- "Cool le concept coaching perso + cours co, on voit pas ça souvent."
- "J'ai vu que vous faites de la muscu libre + électrostim, beau créneau."
- "Le côté salle + espace bien-être c'est top, ça change."
- "Sympa l'approche cours adaptés seniors, y'a clairement un truc là."
- "J'ai regardé votre site, le positionnement haut de gamme ça se voit direct."

MAUVAIS EXEMPLES (ne JAMAIS écrire) :
- "1073 avis Google avec une 4.6, c'est impressionnant." (stats brutes = interdit)
- "460 avis avec une 4.6, c'est rare pour une salle." (pareil)
- "J'admire la passion que vous mettez dans votre travail." (LinkedIn slop)
- "J'ai lu votre mission et je trouve votre approche inspirante." (IA slop)
- "C'est un segment qui décolle vraiment en ce moment." (analytique, pas humain)
- "C'est un marché énorme en ce moment." (pareil)

RÈGLES DE FORMAT :
- 1 phrase max (2 courts fragments OK). Grammaire casual. Légèrement imparfait = plus humain.
- Pas de salutation (pas de "Bonjour", pas de "Hey"). Pas de compliments vides.
- Référence quelque chose de CONCRET et SPÉCIFIQUE à ce lead.
- JAMAIS de tirets longs (em dash). Utilise des tirets courts, virgules, ou points.
- Abréviations OK : "perso" pas "personnalisé", "co" pas "collectifs"

---

RETOURNE uniquement un JSON valide, sans markdown, sans explication :
{{"shortened_name": "...", "personalization": "...", "verdict": true}}

Si les données sont trop pauvres pour un icebreaker spécifique :
{{"shortened_name": "...", "personalization": "", "verdict": false}}
"""


def build_user_message(lead):
    intel = lead.get("website_intel") or {}
    lines = [
        f"company_name: {lead.get('company_name', '')}",
        f"city: {lead.get('city', '')}",
        f"address: {lead.get('address', '')}",
        f"website: {lead.get('website', '')}",
        f"rating: {lead.get('rating', '')}",
        f"reviews_count: {lead.get('reviews_count', '')}",
        f"website_intel.title: {intel.get('title', '')}",
        f"website_intel.meta_description: {intel.get('meta_description', '')}",
        f"website_intel.body_preview: {intel.get('body_preview', '')}",
    ]
    return "\n".join(lines)


def enrich_lead(client, lead, index, total):
    name = lead.get("company_name", "?")

    user_msg = build_user_message(lead)
    try:
        response = client.messages.create(
            model=MODEL,
            max_tokens=256,
            system=SYSTEM_PROMPT,
            messages=[{"role": "user", "content": user_msg}],
        )
        raw = response.content[0].text.strip()

        # Strip markdown code fences if present
        if raw.startswith("```"):
            raw = raw.split("```")[1]
            if raw.startswith("json"):
                raw = raw[4:]
            raw = raw.strip()

        result = json.loads(raw)
        shortened = result.get("shortened_name", name)
        personalization = result.get("personalization", "")
        verdict = result.get("verdict", True)

        if not verdict:
            personalization = ""
            print(f"[{index}/{total}] {name} -> skipped (thin data)")
        else:
            preview = personalization[:60] + "..." if len(personalization) > 60 else personalization
            print(f'[{index}/{total}] {shortened} -> "{preview}"')

        lead["shortened_name"] = shortened
        lead["personalization"] = personalization
        lead["verdict"] = verdict

    except Exception as e:
        print(f"[{index}/{total}] {name} -> ERROR: {e}")
        lead["shortened_name"] = name
        lead["personalization"] = ""
        lead["verdict"] = False

    return lead


def main():
    parser = argparse.ArgumentParser(description="Enrich leads with casualized names + icebreakers")
    parser.add_argument("--leads", default="data/leads_with_emails.json", help="Input leads JSON")
    parser.add_argument("--output", default="data/leads_enriched.json", help="Output JSON")
    args = parser.parse_args()

    api_key = os.environ.get("ANTHROPIC_API_KEY")
    if not api_key:
        print("ERROR: ANTHROPIC_API_KEY not found in environment.")
        print("Add it to your .env file: ANTHROPIC_API_KEY=sk-ant-...")
        sys.exit(1)

    input_path = Path(args.leads)
    if not input_path.exists():
        print(f"ERROR: {args.leads} not found. Run /find-emails first.")
        sys.exit(1)

    with open(input_path, encoding="utf-8") as f:
        leads = json.load(f)

    # Filter: only leads with email
    leads_with_email = [l for l in leads if l.get("email")]
    skipped_no_email = len(leads) - len(leads_with_email)

    total = len(leads_with_email)
    if total == 0:
        print("No leads with emails found. Run /find-emails first.")
        sys.exit(1)

    print(f"Enriching {total} leads with emails ({skipped_no_email} skipped - no email)...\n")

    client = anthropic.Anthropic(api_key=api_key)

    enriched = []
    generated = 0
    thin_data = 0

    for i, lead in enumerate(leads_with_email, 1):
        result = enrich_lead(client, lead, i, total)
        enriched.append(result)
        if result.get("verdict"):
            generated += 1
        else:
            thin_data += 1

    output_path = Path(args.output)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(enriched, f, ensure_ascii=False, indent=2)

    print()
    print(f"Done. {generated}/{total} icebreakers generated ({thin_data} skipped - thin data).")
    print(f"Saved to {args.output}")


if __name__ == "__main__":
    main()
