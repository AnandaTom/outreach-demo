#!/usr/bin/env python3
"""Push leads + email sequence to an Instantly campaign."""

import argparse
import json
import os
import sys
from pathlib import Path

import requests
from dotenv import load_dotenv

load_dotenv()

BASE_URL = "https://api.instantly.ai/api/v2"

CAMPAIGN_SCHEDULE = {
    "schedules": [
        {
            "name": "Default",
            "timing": {"from": "08:00", "to": "18:00"},
            "days": {"0": True, "1": True, "2": True, "3": True, "4": True, "5": False, "6": False},
            "timezone": "Europe/Belgrade",  # CET - Europe/Paris not in Instantly allowed list
        }
    ]
}

CHECKLIST = """
--- Pre-launch checklist ---
Avant de lancer, vérifiez :
[ ] DNS configurés : SPF, DKIM, DMARC sur votre domaine d'envoi
[ ] Domaine warmup : au moins 14 jours de warmup avant d'envoyer à grande échelle
[ ] Volume d'envoi : commencez à 20-30 emails/jour/compte, max 50
[ ] Lisez chaque email à voix haute (le cerveau corrige silencieusement)
[ ] Prévisualisez 3+ leads au hasard : vérifiez les {{variables}} cassées, noms en MAJUSCULES, icebreakers IA
[ ] Notifications de réponses configurées dans Instantly
"""


def get_headers(api_key):
    return {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
    }


def api_get(api_key, path, params=None):
    resp = requests.get(f"{BASE_URL}{path}", headers=get_headers(api_key), params=params, timeout=15)
    resp.raise_for_status()
    return resp.json()


def api_post(api_key, path, body):
    resp = requests.post(f"{BASE_URL}{path}", headers=get_headers(api_key), json=body, timeout=15)
    resp.raise_for_status()
    return resp.json()


def api_patch(api_key, path, body):
    resp = requests.patch(f"{BASE_URL}{path}", headers=get_headers(api_key), json=body, timeout=15)
    resp.raise_for_status()
    return resp.json()


def find_or_create_campaign(api_key, name):
    print(f"Looking for existing campaign: '{name}'...")
    try:
        data = api_get(api_key, "/campaigns", params={"limit": 100})
        campaigns = data.get("items", data) if isinstance(data, dict) else data
        for c in campaigns:
            if c.get("name") == name:
                print(f"Found existing campaign (ID: {c['id']})")
                return c["id"]
    except Exception as e:
        print(f"Warning: could not list campaigns: {e}")

    print(f"Creating new campaign: '{name}'...")
    body = {
        "name": name,
        "campaign_schedule": CAMPAIGN_SCHEDULE,
    }
    result = api_post(api_key, "/campaigns", body)
    campaign_id = result.get("id")
    print(f"Campaign created (ID: {campaign_id})")
    return campaign_id


def set_sequence(api_key, campaign_id, sequence):
    print("Setting email sequence...")
    steps = []
    for key in ["email1", "email2", "email3", "email4"]:
        if key not in sequence:
            continue
        email = sequence[key]
        steps.append({
            "type": "email",
            "delay": email["delay"],
            "variants": [
                {
                    "subject": email["subject"],
                    "body": email["body"],
                }
            ],
        })

    api_patch(api_key, f"/campaigns/{campaign_id}", {"sequences": [{"steps": steps}]})
    print(f"Sequence set: {len(steps)} emails")


def add_leads(api_key, campaign_id, leads):
    qualified = [l for l in leads if l.get("email") and l.get("personalization")]
    skipped = len(leads) - len(qualified)
    if skipped:
        print(f"Filtered out {skipped} leads (no email or no personalization)")

    if not qualified:
        print("No qualified leads to add.")
        return 0

    print(f"Adding {len(qualified)} leads (one request each)...")
    added = 0
    for lead in qualified:
        body = {
            "email": lead.get("email", ""),
            "first_name": "",
            "last_name": "",
            "company_name": lead.get("shortened_name") or lead.get("company_name", ""),
            "personalization": lead.get("personalization", ""),
            "website": lead.get("website", ""),
            "phone": lead.get("phone", ""),
            "campaign_id": campaign_id,
            "skip_if_in_workspace": True,
        }
        try:
            api_post(api_key, "/leads", body)
            added += 1
            print(f"  + {body['email']}")
        except Exception as e:
            print(f"  ! {body['email']} -> skipped ({e})")
    return added


def launch_campaign(api_key, campaign_id):
    print("Launching campaign...")
    api_post(api_key, f"/campaigns/{campaign_id}/launch", {})
    print("Campaign launched! Emails will send Mon-Fri, 08:00-18:00 (Europe/Paris).")


def main():
    parser = argparse.ArgumentParser(description="Push leads + sequence to Instantly")
    parser.add_argument("--campaign", required=True, help="Campaign name")
    parser.add_argument("--leads", default="data/leads_enriched.json", help="Enriched leads JSON")
    parser.add_argument("--sequence", default="data/sequence.json", help="Email sequence JSON")
    args = parser.parse_args()

    api_key = os.environ.get("INSTANTLY_API_KEY")
    if not api_key:
        print("ERROR: INSTANTLY_API_KEY not found in environment.")
        print("Add it to .env: INSTANTLY_API_KEY=your_key")
        print("Get it at: app.instantly.ai > Settings > API")
        sys.exit(1)

    leads_path = Path(args.leads)
    if not leads_path.exists():
        print(f"ERROR: {args.leads} not found. Run /enrich first.")
        sys.exit(1)

    with open(leads_path, encoding="utf-8") as f:
        leads = json.load(f)

    sequence = None
    sequence_path = Path(args.sequence)
    if sequence_path.exists():
        with open(sequence_path, encoding="utf-8") as f:
            sequence = json.load(f)
    else:
        print(f"Note: {args.sequence} not found. Skipping sequence setup.")

    # Step 1-2: find or create campaign
    campaign_id = find_or_create_campaign(api_key, args.campaign)

    # Step 3: set sequence (if available)
    if sequence:
        set_sequence(api_key, campaign_id, sequence)

    # Step 4-5: add leads
    added = add_leads(api_key, campaign_id, leads)
    print(f"\nAdded {added} leads to campaign '{args.campaign}' (ID: {campaign_id})")

    # Step 6: checklist
    print(CHECKLIST)

    # Step 7: launch prompt
    answer = input("Lancer la campagne maintenant ? (o/N) ").strip().lower()
    if answer in ("o", "oui", "y", "yes"):
        launch_campaign(api_key, campaign_id)
    else:
        print("Campagne non lancée. Lancez manuellement dans Instantly quand vous êtes prêt.")


if __name__ == "__main__":
    main()
