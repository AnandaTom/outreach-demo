#!/usr/bin/env python3
"""Scrape leads from Google Maps via Apify (compass/crawler-google-places)."""

import argparse
import json
import os
import random
import sys
from pathlib import Path

from dotenv import load_dotenv

load_dotenv()


def get_api_key():
    key = os.environ.get("APIFY_API_KEY")
    if not key:
        print("ERROR: APIFY_API_KEY not found in environment.")
        print()
        print("Setup instructions:")
        print("  1. Go to https://apify.com and sign up (free tier available)")
        print("  2. Navigate to Settings > Integrations > API Token")
        print("  3. Copy your API token")
        print("  4. Add it to your .env file: APIFY_API_KEY=your_token_here")
        sys.exit(1)
    return key


def normalize_lead(item, industry):
    def first(*values):
        for v in values:
            if v:
                return v
        return ""

    website = first(item.get("website"), item.get("url"), "")
    if website:
        website = website.rstrip("/")

    address = first(
        item.get("address"),
        item.get("street"),
        "",
    )
    city = first(item.get("city"), "")
    if not city and address:
        # Try to extract city from address (last meaningful token)
        parts = [p.strip() for p in address.split(",")]
        if len(parts) >= 2:
            city = parts[-1].strip()

    return {
        "company_name": first(item.get("title"), item.get("name"), ""),
        "phone": first(item.get("phone"), item.get("phoneNumber"), ""),
        "website": website,
        "city": city,
        "address": address,
        "rating": item.get("totalScore") or item.get("rating") or 0,
        "reviews_count": item.get("reviewsCount") or item.get("reviews") or 0,
        "industry": industry,
    }


def quality_report(leads):
    sample = random.sample(leads, min(25, len(leads)))
    has_website = sum(1 for l in sample if l["website"])
    has_phone = sum(1 for l in sample if l["phone"])
    has_city = sum(1 for l in sample if l["city"])
    has_reviews = sum(1 for l in sample if l["reviews_count"])

    n = len(sample)
    print()
    print("=== Quality Report ===")
    print(f"Sample size: {n} leads")
    print(f"  Website:  {has_website}/{n} ({has_website/n*100:.0f}%)")
    print(f"  Phone:    {has_phone}/{n} ({has_phone/n*100:.0f}%)")
    print(f"  City:     {has_city}/{n} ({has_city/n*100:.0f}%)")
    print(f"  Reviews:  {has_reviews}/{n} ({has_reviews/n*100:.0f}%)")

    min_pct = min(has_website, has_phone, has_city, has_reviews) / n * 100
    if min_pct < 80:
        print()
        print(f"WARNING: Quality below 80% threshold on at least one field ({min_pct:.0f}%).")
        print("Consider refining your search query or increasing the limit.")

    print()
    print("=== 3 Random Samples ===")
    for lead in random.sample(leads, min(3, len(leads))):
        print(f"  {lead['company_name']}")
        print(f"    Phone:   {lead['phone'] or '(none)'}")
        print(f"    Website: {lead['website'] or '(none)'}")
        print(f"    City:    {lead['city'] or '(none)'}")
        print(f"    Rating:  {lead['rating']} ({lead['reviews_count']} reviews)")
        print()


def main():
    parser = argparse.ArgumentParser(description="Scrape leads from Google Maps via Apify")
    parser.add_argument("--search", required=True, help="Search query (e.g. 'salles de sport Paris')")
    parser.add_argument("--limit", type=int, default=50, help="Max number of leads (default: 50)")
    parser.add_argument("--output", default="data/leads_raw.json", help="Output file path")
    args = parser.parse_args()

    api_key = get_api_key()

    # Ensure output directory exists
    output_path = Path(args.output)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    try:
        from apify_client import ApifyClient
    except ImportError:
        print("ERROR: apify-client not installed.")
        print("Run: pip install apify-client")
        sys.exit(1)

    client = ApifyClient(api_key)

    print(f"Running Apify actor compass/crawler-google-places...")
    print(f"  Search: {args.search}")
    print(f"  Limit:  {args.limit}")

    run_input = {
        "searchStringsArray": [args.search],
        "maxCrawledPlacesPerSearch": args.limit,
        "language": "fr",
        "maxImages": 0,
        "exportPlaceUrls": False,
        "additionalInfo": False,
        "reviewsSort": "newest",
        "maxReviews": 0,
    }

    run = client.actor("compass/crawler-google-places").call(run_input=run_input)

    raw_items = list(client.dataset(run["defaultDatasetId"]).iterate_items())
    print(f"Actor finished. {len(raw_items)} raw results.")

    # Extract industry from search (first word(s) before city)
    industry = args.search

    # Normalize
    normalized = [normalize_lead(item, industry) for item in raw_items]

    # Filter: keep only leads with a website
    before = len(normalized)
    leads = [l for l in normalized if l["website"]]
    removed = before - len(leads)
    print(f"After filtering: {len(leads)} leads with website ({removed} removed)")

    if not leads:
        print("No leads with websites found. Try a broader search query or higher limit.")
        sys.exit(1)

    quality_report(leads)

    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(leads, f, ensure_ascii=False, indent=2)

    print(f"Saved {len(leads)} leads to {args.output}")


if __name__ == "__main__":
    main()
