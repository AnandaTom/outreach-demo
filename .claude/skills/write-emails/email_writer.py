#!/usr/bin/env python3
"""Generate a 4-email cold outreach sequence using Claude Haiku."""

import argparse
import json
import os
import sys
from pathlib import Path

import anthropic
from dotenv import load_dotenv

load_dotenv()

MODEL = "claude-haiku-4-5-20251001"

SENDER_NAME = "Tom"
CASE_STUDY = "j'ai aidé une agence de marketing à scaler de 10k à 55k/mois grâce à ce genre de système, en 5 mois"

SYSTEM_PROMPT = """Tu es un expert en copywriting cold email B2B, spécialiste des campagnes de prospection à froid.
Tu rédiges en français, avec un ton direct, humain et légèrement informel.

Ta mission : générer une séquence de 4 emails cold outreach basée sur les infos fournies.

---

LA FORMULE EN 4 PARTIES (chaque email la suit en tout ou en partie) :
1. PERSONNALISATION - variable {{personalization}} (déjà générée par lead). 1 phrase. Sonne comme un vrai SMS d'un humain.
2. PREUVE SOCIALE - Qui tu es + ce que tu as fait. 1 phrase. Client type + chiffre précis (3.7x > "presque 4x").
3. OFFRE + INVERSION DU RISQUE - Trop beau pour être vrai. Le prospect ne risque rien. "Je ne facture rien tant que..." / "Garanti ou vous ne payez pas."
4. CTA - Horaire précis. "Ça vous va mardi à 10h ou mercredi à 14h ?" Jamais vague.

---

L'ARC EN 4 EMAILS :

E1 (Jour 0) : Formule complète en 4 parties. Commence par {{personalization}} sur la 1ère ligne.
  - Objet : "{{firstName}}, question" ou variation courte
  - 75-100 mots MAX (75 idéal)
  - Termine par le prénom du sender uniquement (pas de "Cordialement")

E2 (Jour 4) : Réponse en fil (même objet que E1). Angle différent : preuve plus profonde, douleur différente, ou question "poke the bear".
  - Objet : IDENTIQUE à E1 (reply threadé)
  - 60-80 mots

E3 (Jour 9) : Nouvel objet. Valeur différente OU CTA moins engageant ("15 min ?").
  - Objet : nouveau, sans rapport avec E1
  - 50-70 mots

E4 (Jour 14) : Breakup. 30-40 mots MAX.
  - Doit se terminer par : "Si c'est pas vous qui gérez ça, je devrais contacter qui chez vous ?"

---

LEVIERS COPYWRITING :

Poke the Bear (Josh Braun) : questions neutres, pas directrices.
- Faible : "Vous avez beaucoup de no-shows ?"
- Fort : "Comment vous gérez les créneaux perdus quand quelqu'un ne se pointe pas sans prévenir ?"

Inversion du risque : tout le risque est sur toi, le prospect ne risque rien.
- "Je ne facture rien tant que vous n'avez pas vu les résultats."
- "Garanti ou vous ne payez pas."
- "Je configure tout en avance, sans engagement."

Test "Et alors ?" : pousse chaque claim à son effet de second ordre.
- "J'automatise vos rappels" -> et alors ? -> "Ça réduit vos no-shows, ce qui vous récupère plusieurs créneaux/semaine."

Chiffres précis : 3.7x > "presque 4x". 143 503 EUR > "~140K".

---

RÈGLES OBJETS :
- Moins de 4 mots toujours > long
- Formats : "{{firstName}}, question" / "{{firstName}} ?" / "question rapide" / "une idee"
- JAMAIS {{companyName}} dans l'objet
- E2 = même objet que E1 (fil de réponse)
- E3 = nouvel objet sans rapport
- Minuscules : "question rapide" pas "Question Rapide"

---

NE JAMAIS ÉCRIRE :
- "J'espère que vous allez bien" / "J'espère que cet email vous trouve en forme"
- "Je m'appelle X et je suis..." (jamais en ligne 1)
- "Notre plateforme", "Notre solution" (utilise "je" pas "nous")
- "ROI", "synergie", "optimisation", "levier" (jargon corporate interdit)
- "Seriez-vous intéressé ?" (trop vague - toujours un horaire précis)
- "Merci de votre temps"
- "Cordialement" (signe avec le prénom uniquement)
- Plus de 100 mots par email
- Fausse urgence ("il reste 2 places")
- Tirets longs (--)

---

RETOURNE uniquement un JSON valide, sans markdown, sans explication.
Format exact :
{
  "email1": {"subject": "...", "body": "...", "delay": 0},
  "email2": {"subject": "...", "body": "...", "delay": 4},
  "email3": {"subject": "...", "body": "...", "delay": 9},
  "email4": {"subject": "...", "body": "...", "delay": 14}
}

Dans les corps d'email : utilise {{personalization}} et {{firstName}} comme variables Instantly.
Signe chaque email avec le prénom du sender (fourni dans le contexte).
"""


def build_user_message(niche, offer, case_study, sender_name):
    return f"""Génère la séquence pour ces paramètres :

Niche cible : {niche}
Offre : {offer}
Cas client / preuve sociale : {case_study}
Prénom du sender : {sender_name}

La séquence doit être adaptée à cette niche et cette offre. Utilise le cas client comme preuve sociale dans E1 ou E2."""


def pretty_print(sequence):
    for key in ["email1", "email2", "email3", "email4"]:
        email = sequence[key]
        delay = email["delay"]
        label = {0: "E1 - Jour 0", 4: "E2 - Jour 4", 9: "E3 - Jour 9", 14: "E4 - Jour 14"}.get(delay, key)
        print(f"\n{'='*60}")
        print(f"{label}")
        print(f"Objet : {email['subject']}")
        print(f"{'='*60}")
        print(email["body"])


def main():
    parser = argparse.ArgumentParser(description="Generate 4-email cold outreach sequence")
    parser.add_argument("--niche", default="salles de sport", help="Target niche")
    parser.add_argument("--offer", default="générer 20 RDV par mois grâce à un système d'acquisition automatisé", help="Your offer in 1-2 sentences")
    parser.add_argument("--output", default="data/sequence.json", help="Output JSON file")
    args = parser.parse_args()

    api_key = os.environ.get("ANTHROPIC_API_KEY")
    if not api_key:
        print("ERROR: ANTHROPIC_API_KEY not found in environment.")
        print("Add it to your .env file: ANTHROPIC_API_KEY=sk-ant-...")
        sys.exit(1)

    print(f"Generating 4-email sequence for niche: {args.niche}")
    print(f"Offer: {args.offer}")
    print(f"Sender: {SENDER_NAME}")
    print()

    client = anthropic.Anthropic(api_key=api_key)

    user_msg = build_user_message(args.niche, args.offer, CASE_STUDY, SENDER_NAME)

    response = client.messages.create(
        model=MODEL,
        max_tokens=2048,
        system=SYSTEM_PROMPT,
        messages=[{"role": "user", "content": user_msg}],
    )

    raw = response.content[0].text.strip()

    # Strip markdown fences if present
    if raw.startswith("```"):
        raw = raw.split("```")[1]
        if raw.startswith("json"):
            raw = raw[4:]
        raw = raw.strip()

    try:
        sequence = json.loads(raw)
    except json.JSONDecodeError as e:
        print(f"ERROR: Could not parse model response as JSON: {e}")
        print("Raw response:", raw[:500])
        sys.exit(1)

    pretty_print(sequence)

    output_path = Path(args.output)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(sequence, f, ensure_ascii=False, indent=2)

    print(f"\n\nSaved to {args.output}")


if __name__ == "__main__":
    main()
