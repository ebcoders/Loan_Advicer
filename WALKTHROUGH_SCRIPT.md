# 5-Minute Walkthrough — Script/Outline

This is a speaking outline, not a word-for-word script — the brief explicitly says you must be
able to defend every rule without AI help, so the goal here is a structure you can talk through
naturally, using numbers you already understand, not lines to memorize.

Total: ~5 minutes. Timestamps are a guide, not a hard rule — better to go slightly over on the
live demo than to rush it.

---

### 0:00–0:20 — The gap, in one breath

Say, in your own words: every lender has a model that decides what a borrower gets. The borrower
has nothing — they walk in blind and find out years later they overpaid. This app is a
self-assessment that makes the borrower the best-informed person in the room before they even
talk to a lender.

*(Don't over-explain this — 20 seconds, then move to the app.)*

---

### 0:20–0:50 — Quick tour: how it adapts

Open the app. Point out, without dwelling:
- No login, nothing stored — everything comes from what you type in this session.
- The flow starts the same for everyone (purpose, amount, income type, existing debt, age, credit
  status) — but show how selecting **self-employed** immediately adds the ITR question that a
  salaried person never sees. This is the concrete answer to "a salaried IT employee and a kirana
  owner shouldn't see the same questions" — it's not a separate path, it's built into Tier 1 itself.

---

### 0:50–2:30 — Walk one borrower live: Ravi

Ravi is the richest example — use him, not Priya or Anita, because he touches the most mechanics
in one pass: income blending, collateral routing, and the ROI credit.

Fill in his answers live (from THREE_RUNTHROUGHS.md if you want exact numbers, or just recall
them):
- Self-employed, ₹40k–80k cash income, ITR shows ₹4,20,000/year, no credit history, owns his shop
  outright (₹45L, unencumbered), wants ₹15L for a second stock line + delivery vehicle.

As the outputs render, narrate what's happening, not just what the numbers say:
- **Assessed income (₹45,600):** point out this isn't his ITR (₹35k) or his optimistic
  self-declared figure — it's a blended, discounted number, because neither extreme is trustworthy
  on its own.
- **The routing:** he asked for a business loan, the app redirects him to Loan Against Property.
  Say why in one sentence: no credit history to price an unsecured loan against, but he owns
  collateral — that changes his rate from an 18-24% band to 9-11.5%.
- **The verdict (Borrow Less, ₹12,00,000 not ₹15,00,000):** the property alone would support
  nearly ₹25L — it's his *income*, the stricter constraint, that caps him lower. Say this
  explicitly: the app always uses whichever constraint binds, not whichever is bigger.
- **The Negotiation Card:** show it. This is what he'd actually hold up to a lender.

---

### 2:30–3:15 — Explainability: show one "why," traced

Open RULES.md briefly. Pick one number from Ravi's case (e.g. the 55% LTV on his commercial
property, or the 0.70 income haircut) and show the matching row: value, why, and whether it's a
published figure or your own judgement call. Say plainly: not every number here is externally
verified, and the document says so on purpose — that's the point, not a gap to hide.

---

### 3:15–4:15 — What I'd build next

Speak from the genuinely open list (PROJECT_PLAN.md Part 3 / OPEN_QUESTIONS.md) — pick 2-3, not
all of them:
- A real counting rule for co-applicant income (currently collected, not yet used — flagged
  honestly in the app itself).
- Household-distress signals beyond debt ratios (single income earner, dependents, no savings) —
  right now these only show up qualitatively in Anita's case, not as a formal rule.
- Letting the borrower choose their own tenure instead of always assuming the maximum — currently
  hardcoded.
- Product bands beyond personal loan and LAP (home loan, gold loan, two-wheeler) — deliberately
  out of scope so far, since the three borrowers didn't need them.

---

### 4:15–4:50 — What I'd cut, on purpose

This matters as much as what you'd build — it shows judgement, not just ambition. Say plainly:
- Pixel-perfect visual polish — the brief itself says this isn't scored.
- Any real credit bureau integration or ML-based scoring — explicitly out of scope, and honestly,
  a self-assessment tool is more useful *because* it doesn't need bureau access — that's what lets
  someone check their situation before walking in anywhere.
- Full breadth of loan products — better to be right about personal loans and LAP for these three
  borrowers than shallow across ten product types nobody asked about.

---

### 4:50–5:00 — Close

One sentence: the goal wasn't to build a lending calculator, it was to turn lending judgement into
rules a borrower can see and a machine can run — and to be honest, in the document and in the app
itself, about where that judgement is solid and where it's still a reasoned guess.

---

## Before recording — a rehearsal check

Pick one constant in `rules.py` (e.g. `MARGIN_ABOVE_CURRENT`, or the `0.70` income haircut) and
change it, then re-run Ravi. If you can explain in one sentence why his numbers moved the way they
did, you're ready. If you can't, re-read the matching section of PROJECT_PLAN.md Part 1.3 before
you record — this is exactly what the live follow-up will ask you to do in front of someone.
