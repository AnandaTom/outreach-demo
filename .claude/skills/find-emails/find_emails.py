#!/usr/bin/env python3
"""Find emails + extract website intel from lead websites."""

import argparse
import json
import re
import sys
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path
from urllib.parse import urljoin, urlparse

import requests
from bs4 import BeautifulSoup
from dotenv import load_dotenv

load_dotenv()

TIMEOUT = 8
EMAIL_RE = re.compile(r"[a-zA-Z0-9._%+\-]+@[a-zA-Z0-9.\-]+\.[a-zA-Z]{2,}")

JUNK_EMAIL_PATTERNS = [
    "dataprivacy", "cookie", "rgpd", "dpo", "noreply",
    "no-reply", "unsubscribe", "privacy", "legal",
]

PREFERRED_EMAIL_PARTS = ["contact", "info", "hello", "bonjour", "accueil"]

BOOKING_PLATFORMS = [
    "doctolib.fr", "planity.com", "treatwell.fr", "kiute.com",
    "fresha.com", "mindbodyonline.com", "glofox.com",
]

JUNK_CONTENT_PATTERNS = [
    "accepter les cookies", "politique de confidentialit",
    "rgpd", "gdpr", "cookies nécessaires", "we use cookies",
    "cookie policy", "privacy policy",
]

CONTACT_PATHS = ["/contact", "/nous-contacter", "/contactez-nous", "/contact.html", "/nous-joindre"]

INTEL_PATHS = [
    "/",
    "/a-propos", "/about", "/qui-sommes-nous", "/notre-equipe",
    "/services", "/nos-services", "/prestations", "/nos-activites",
    "/contact", "/nous-contacter",
]

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/120.0.0.0 Safari/537.36"
    ),
    "Accept-Language": "fr-FR,fr;q=0.9,en;q=0.8",
}


def is_junk_email(email):
    local = email.split("@")[0].lower()
    return any(p in local for p in JUNK_EMAIL_PATTERNS)


def rank_email(email):
    local = email.split("@")[0].lower()
    for i, pref in enumerate(PREFERRED_EMAIL_PARTS):
        if pref in local:
            return i
    return len(PREFERRED_EMAIL_PARTS)


def extract_emails(text):
    found = EMAIL_RE.findall(text)
    valid = [e for e in found if not is_junk_email(e)]
    if not valid:
        return None
    valid.sort(key=rank_email)
    return valid[0]


def is_booking_redirect(final_url):
    host = urlparse(final_url).netloc.lower()
    return any(platform in host for platform in BOOKING_PLATFORMS)


def is_junk_content(text):
    lower = text.lower()
    return any(p in lower for p in JUNK_CONTENT_PATTERNS)


def clean_text(soup):
    for tag in soup(["script", "style", "noscript", "header", "footer", "nav"]):
        tag.decompose()
    text = soup.get_text(separator=" ", strip=True)
    # Collapse whitespace
    text = re.sub(r"\s+", " ", text).strip()
    return text


def fetch(url, session):
    try:
        resp = session.get(url, timeout=TIMEOUT, headers=HEADERS, allow_redirects=True)
        resp.raise_for_status()
        return resp
    except Exception:
        return None


def process_lead(index, total, lead):
    base_url = lead.get("website", "")
    if not base_url:
        return lead, "no website", "no website"

    domain = urlparse(base_url).netloc or base_url

    email_found = None
    intel = None
    email_source = "not found"
    intel_source = "no useful content"

    with requests.Session() as session:
        # --- Email: homepage + contact pages ---
        pages_for_email = [base_url] + [urljoin(base_url, p) for p in CONTACT_PATHS]
        for url in pages_for_email:
            resp = fetch(url, session)
            if resp is None:
                continue
            if is_booking_redirect(resp.url):
                intel_source = "booking platform redirect"
                break
            emails = extract_emails(resp.text)
            if emails and not email_found:
                email_found = emails
                email_source = f"email: {email_found}"

        # --- Intel: try pages in order ---
        for path in INTEL_PATHS:
            url = urljoin(base_url, path)
            resp = fetch(url, session)
            if resp is None:
                continue
            if is_booking_redirect(resp.url):
                intel_source = "booking platform redirect"
                break

            soup = BeautifulSoup(resp.text, "html.parser")

            # Also grab emails while we're here
            if not email_found:
                emails = extract_emails(resp.text)
                if emails:
                    email_found = emails
                    email_source = f"email: {email_found}"

            title = soup.title.string.strip() if soup.title and soup.title.string else ""
            meta_desc = ""
            meta = soup.find("meta", attrs={"name": re.compile(r"description", re.I)})
            if meta and meta.get("content"):
                meta_desc = meta["content"].strip()

            body_text = clean_text(soup)

            # Skip junk pages
            if is_junk_content(body_text) and not meta_desc:
                continue

            # Strip junk from start of body
            useful_body = body_text
            for pattern in JUNK_CONTENT_PATTERNS:
                idx = useful_body.lower().find(pattern)
                if idx != -1 and idx < 100:
                    useful_body = useful_body[idx + len(pattern):].strip()

            body_preview = useful_body[:300] if useful_body else ""

            if title or meta_desc or body_preview:
                intel = {
                    "title": title,
                    "meta_description": meta_desc,
                    "body_preview": body_preview,
                    "source_page": path,
                }
                intel_source = f"ok (from {path})"
                break

    lead["email"] = email_found
    lead["website_intel"] = intel

    email_label = email_source if email_found else "not found"
    intel_label = intel_source

    print(f"[{index}/{total}] {domain} -> email: {email_label} | intel: {intel_label}")
    return lead, email_label, intel_label


def main():
    parser = argparse.ArgumentParser(description="Find emails + website intel from lead websites")
    parser.add_argument("--leads", default="data/leads_raw.json", help="Input leads JSON")
    parser.add_argument("--output", default="data/leads_with_emails.json", help="Output JSON")
    parser.add_argument("--workers", type=int, default=5, help="Parallel workers (default: 5)")
    args = parser.parse_args()

    input_path = Path(args.leads)
    if not input_path.exists():
        print(f"ERROR: {args.leads} not found. Run /scrape first.")
        sys.exit(1)

    with open(input_path, encoding="utf-8") as f:
        leads = json.load(f)

    total = len(leads)
    print(f"Processing {total} leads with {args.workers} workers...\n")

    results = [None] * total
    emails_found = 0
    intel_found = 0
    no_content = 0

    with ThreadPoolExecutor(max_workers=args.workers) as executor:
        futures = {
            executor.submit(process_lead, i + 1, total, lead): i
            for i, lead in enumerate(leads)
        }
        for future in as_completed(futures):
            idx = futures[future]
            lead, email_label, intel_label = future.result()
            results[idx] = lead
            if lead.get("email"):
                emails_found += 1
            if lead.get("website_intel"):
                intel_found += 1
            else:
                no_content += 1

    output_path = Path(args.output)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(results, f, ensure_ascii=False, indent=2)

    print()
    print(
        f"Done. {emails_found}/{total} emails found. "
        f"{intel_found}/{total} websites with useful intel. "
        f"{no_content}/{total} had no useful content."
    )
    print(f"Saved to {args.output}")


if __name__ == "__main__":
    main()
