# Video Talking Points - Outreach Pipeline Demo

Notes for Tom on camera. Reference these between building each step.

## Opening - Why This Works

- This is NOT spray-and-pray. Each email is personalized by AI to feel handwritten.
- The 3 questions that matter (in this order):
  1. **How** are you going to send? (Deliverability)
  2. **Who** are you going to send to? (List quality)
  3. **What** are you going to say? (Copy)
- Bad copy with a great list beats great copy with a bad list. List > Copy.

## Step 1 - Scrape (mention)

- Google Maps = goldmine for local businesses
- We only keep leads with a website (no website = no way to find email)
- Apify costs ~$5 for 1000 leads

## Step 2 - Find Emails (mention)

- We crawl the website, not buy from a database
- Check /contact, /nous-contacter, /contactez-nous pages
- Prefer info@, contact@, hello@ (decision-maker emails are better if you can find them)

## Step 3 - Enrich (KEY TEACHING MOMENT)

**The Litmus Test:** "Would a real person text this to a friend?"
- If yes -> keep it
- If it sounds like LinkedIn -> rewrite

**Priority order for icebreakers:**
1. Specific event (new opening, hiring, growth)
2. Industry signal (regulation, trend)
3. City context (not just "a Paris")
4. Company niche
5. Website/review signal

**Show good vs bad examples on screen:**
- GOOD: "J'ai vu que vous avez ouvert une 2e salle a Bordeaux -- belle acceleration."
- BAD: "J'admire la passion que vous mettez dans votre travail." (hollow, AI slop)

## Step 4 - Google Sheet (PRACTICAL MOMENT)

- This is where you review the data before sending
- Check icebreakers manually (5+ samples minimum)
- Edit anything that sounds off
- Delete leads with empty personalization
- Show how to connect Google Sheets API (service account setup)

## Step 5 - Write Emails (KEY TEACHING MOMENT)

**The 4-Part Formula (show on screen):**
1. PERSONALIZATION - {{personalization}} variable
2. SOCIAL PROOF - specific client + specific number (3.7x, not "nearly 4x")
3. OFFER + RISK REVERSAL - prospect risks nothing
4. CTA - specific time ("mardi 10h ou mercredi 14h ?")

**The 4-Email Arc:**
- E1 (Day 1): Full formula, 75-100 words
- E2 (Day 4): Threaded reply, different angle, 60-80 words
- E3 (Day 9): New subject, different value prop, 50-70 words
- E4 (Day 14): Breakup, 30-40 words, "je devrais contacter qui chez vous ?"

**Copywriting levers to mention:**
- Poke the Bear: "Comment vous gerez les creneaux perdus ?" (not "Vous avez des no-shows ?")
- Risk Reversal: "Garanti ou vous ne payez pas"
- "So What?" test: push claims to second-order effects

**What never to write:**
- "J'espere que vous allez bien" (screams mass email)
- "Notre solution" (use "je" not "nous")
- Corporate jargon (ROI, synergie, optimisation)

## Step 6 - Push to Instantly (mention)

**Deliverability basics (explain briefly):**
- SPF, DKIM, DMARC = DNS records that prove you're legit
- Warmup: 14 days minimum before sending at scale
- Volume: start at 20-30 emails/day/account, max 50
- Never send from your main domain (use a dedicated sending domain)

**Before launching:**
- Read every email out loud
- Preview 3+ random leads
- Check {{personalization}} renders correctly

## Closing - Benchmarks

- 1% positive reply rate = campaign is working
- 1-3% = solid
- 3%+ = exceptional
- "No" replies are good - confirms you're in primary inbox
- Test one variable at a time: list, then copy, then offer

## Demo-specific reminders

- Niche: gyms in Paris
- Offer: Anti No-Show System (SMS/email reminders, 50%+ reduction guaranteed)
- Language: French
- Each prompt creates a Claude Code **skill** (SKILL.md + Python script)
- After building each skill, demo it live with the slash command:
  - `/scrape "salle de sport Paris" --limit 5`
  - `/find-emails`
  - `/enrich`
  - `/save-to-sheets`
  - `/write-emails gyms no-show`
  - `/push-to-instantly "Gyms Paris Test"`
- The "wow moment": type `/scrape`, watch Claude run the pipeline, see results
