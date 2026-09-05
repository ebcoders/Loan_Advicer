# Borrower Copilot — Full Project Context & Step-by-Step Plan

This document exists so that anyone (a human, or a new AI agent with no memory of prior
conversation) can pick up this project and continue it exactly as it was being built, without
re-deriving any of the reasoning already done. Read this whole file before touching any code.

---

## PART 0 — The assignment (source: Lokta Borrower Copilot Build Challenge)

**What to build:** A personal assistant/app that helps an Indian borrower answer four questions
*before* they walk into a lender:
1. Should I borrow at all?
2. How much am I really eligible for?
3. What is a fair rate for me?
4. What EMI should I agree to?

...and hand them a one-page **Negotiation Card** they can use with a lender.

**Constraints:** No login, no credit bureau pull, no personal data stored. Everything runs from
what the borrower tells the app. Must run locally from a README in under 5 minutes. No backend
required. Must work on a phone.

**The four required outputs, precisely:**
| # | Output | What "good" looks like |
|---|---|---|
| 1 | Borrow / Don't borrow / Borrow less | A verdict with a reason. "Don't borrow" must be a reachable answer, not just theoretically possible. |
| 2 | Maximum amount | **Two numbers, clearly separated**: what a lender will likely sanction, and what the borrower can safely carry. State which one the borrower should actually use. |
| 3 | Fair interest rate | A **band**, not a point. Show what to expect AND the all-in APR (including processing fee) so a lender's quote can be compared honestly. |
| 4 | EMI / outflow ceiling | A monthly ceiling not to cross, with tenure trade-off shown, and **one stress case** (income drops or rate rises). |
| + | Negotiation Card | One screen the borrower can hold up to a lender. E.g. "Lender quotes 14%, card says fair for your profile is 11-12.5%, because…" |

**Question design (two tiers, exact intent from the brief):**
- **Must questions (~8-10):** app must work with wide ranges/low confidence if this is all that's
  answered. Think: purpose, amount wanted, loan type, net monthly income + type
  (salaried/self-employed/informal), existing EMIs, household expenses, age, credit score if known.
- **Additional questions:** as many as earn their place, but **every one must move an output** —
  if a question never changes a number, cut it. Candidates: income stability/history,
  variable-income share, existing loan detail, card utilisation, past bounces, emergency savings
  (months), collateral value, co-applicant, upcoming large expenses, what the loan will earn if
  productive, offers already received.

**Five rules the brief explicitly judges on:**
1. **Adaptive** — a salaried IT employee and a kirana owner should not see the same questions.
2. **Confidence widens with silence** — fewer answers, wider band, and the app says so.
3. **Unknown is never zero** — "I don't know my credit score" ≠ a 300 score. Model it as unknown
   and show the consequence.
4. **Every number has a why** — the borrower must be able to read, in one sentence, why a ceiling
   is ₹22,000 and not ₹30,000.
5. **India, in rupees** — FOIR-style affordability, RBI-style all-in APR disclosure, real product
   bands (home, LAP, personal, gold, two-wheeler, business). Use what you know; document what you
   assumed.

**Three borrowers the app is scored against** (their own reasoning, not matching a hidden answer key):

- **Priya, 29, Bengaluru, salaried.** Software engineer, MNC, 5 years. Net ₹1,10,000/month. One
  car loan, EMI ₹14,000, 2 years left. Credit score 780. Rents at ₹28,000. **Wants ₹8,00,000
  personal loan for a wedding.**
- **Ravi, 42, Mysuru, self-employed.** Kirana store, 14 years. Cash income ₹40,000-80,000/month;
  ITR shows ₹4,20,000/year. Owns the shop premises, unencumbered, ~₹45,00,000. Never taken a
  formal loan — no credit score. Wife earns ₹18,000 teaching. **Wants ₹15,00,000 for a second
  stock line and a delivery vehicle.**
- **Anita, 35, Hubballi, informal.** Delivery-platform rider + home tailoring, ₹26,000-30,000/month.
  Two children, husband unemployed 8 months. Three app loans, ₹35,000 outstanding at 30%+, one
  EMI bounced last month. **Wants ₹1,50,000 for an electric scooter to double delivery runs.**

**Four deliverables required for submission:**
1. The working app (runs locally in <5 min, no backend, works on a phone)
2. `RULES.md` — every rule/threshold/band/assumption in a table: what · value · why · source or "my judgement"
3. Three full run-throughs (questions asked, four outputs, Negotiation Card) for Priya, Ravi, Anita
4. A five-minute walkthrough (recording or written) — what you'd build next, what you'd cut

**Scoring (100 pts):** Domain reasoning 30 · Question design 20 · Explainability & the Card 20 ·
Product craft 15 · Engineering 10 · Honesty about limits 5. Not scored: pixel perfection, real
bureau integration, an ML model, breadth of products beyond what the three borrowers need.

**The trap to design around:** a 60-minute live follow-up where the evaluator changes one
assumption/rule and watches the builder change the app, live, without AI assistance in that
moment. Every rule must be something the builder can explain and edit from memory.

---

## PART 1 — Decisions already made, and why (read before changing anything)

### 1.1 Tech stack: Python + Streamlit, with hand-editable custom CSS
- Builder's background: strong in C++, minimal experience in JS/HTML/DOM, some CSS/HTML
  familiarity via browser dev tools (can read/find things, not confident writing from scratch).
- Streamlit was chosen over plain HTML/JS or React because: (a) it's pure Python, closest
  language to C++ that the builder already knows; (b) Streamlit reruns the *entire script*
  top-to-bottom on every interaction, which behaves like an ordinary imperative program — no
  DOM/event-model mental shift; (c) live rule changes = edit one Python function, save, done —
  no separate "wire it to the UI" step; (d) `pip install streamlit && streamlit run app.py` is a
  trivially reliable "runs in under 5 minutes, no backend" story for a judge on any machine.
- Trade-off accepted: Streamlit's default visual polish is generic. Mitigated by injecting custom
  CSS via `st.markdown(..., unsafe_allow_html=True)` — this part IS real HTML/CSS the builder can
  inspect-element and edit directly, since that's a skill they already have. The rules logic
  (what must be defended live) stays pure, simple Python with no CSS/HTML mixed in.
- **A `rules.js` file exists in the project folder from an earlier (abandoned) plain-JS attempt.
  It is superseded by `rules.py` and should be deleted or ignored — do not build on it.**

### 1.2 Visual design plan (for the custom CSS layer)
Grounded in the subject matter (Indian bank passbook/ledger), not generic AI-tool aesthetics.
- **Palette:** paper `#EEF0E4` (cool sage-cream, deliberately not the clichéd warm `#F4F1EA`),
  ink `#1C2A44` (deep navy for text/headlines), gold `#B98A2E` (turmeric accent for key figures &
  primary actions), brick `#9C3B29` (Don't-Borrow/caution states only), forest `#2E5233`
  (Borrow/go-ahead states only), rule-line `#C9CBB8` (faint sage, for ledger-style dividers).
- **Type:** IBM Plex Serif for numbers/headlines (passbook-printed-numeral feel), IBM Plex Sans
  for body/UI. Same type family, different roles — deliberate, not a random pairing.
- **Layout:** mobile-first single column, left-aligned text, numbers right-aligned like a bank
  statement's amount column. Faint horizontal ledger-rules between sections instead of
  card/shadow UI kit look.
- **One deliberate motif, used once:** the Negotiation Card renders like an actual stamped card.
  Nothing else on the page competes with it visually.
- Explicitly avoid: centered hero sections, generic SaaS card grids, ALL-CAPS eyebrow labels,
  emoji as icons, purple/violet AI-generic gradients.

### 1.3 Core methodology corrections made during design (do not revert these)
- **FOIR must include rent.** An early draft assumed lenders exclude rent from FOIR and only the
  app's "safe" view would count it. This was checked against real published lender formulas
  (e.g. L&T Finance's own worked example) and found wrong — most real FOIR formulas already
  include rent. Both the lender-view and safe-view now use the same obligations definition
  (existing EMIs + rent); they differ by margin, not by definition.
- **The lender/safe split is a margin + stress test, not a different obligations formula.**
  Correct mental model: same inputs, different tolerance for risk.
- **Self-employed/informal income is never taken at face value or from ITR alone.** It's a blend:
  midpoint of self-declared range × a haircut (default 0.70, i.e. 30% discount), compared against
  ITR-derived monthly income, taking the higher of the two. The haircut is explicitly a judgement
  call (no published formula exists for this), and should ideally be replaced by the borrower's
  answer to the Tier-2 "variable income share" question when available (see `assess_income()` in
  rules.py — this substitution is already implemented).
- **NTC (New-to-Credit) ≠ "unknown credit score."** Never having taken formal credit is a distinct
  case from not knowing one's score. NTC is handled by *routing* (steer toward secured lending if
  collateral exists) rather than by inventing a numeric risk premium, because no defensible public
  number exists for pricing NTC risk without real default data.
- **Collateral-based secured routing (LAP):** if a borrower is NTC or has thin/unverifiable income
  AND owns unencumbered property, evaluate a Loan Against Property alongside any unsecured option,
  and default to whichever is safe *and* cheaper. LTV assumptions: 55% commercial, 65% residential
  (grounded in published lender ranges, e.g. SBI/Aditya Birla/Poonawalla).
- **Verdict logic is two layers, not one ratio check:**
  - **Layer 1 (hard stops, checked first, independent of ratio math):** any bounced/missed
    payment in the trailing 3 months → automatic Don't Borrow. (A second candidate hard stop —
    "existing debt already at 30%+ interest" — is still an open, undecided question; see Part 3.)
  - **Layer 2 (ratio check, only runs if no hard stop fired):** compute the safe ceiling; if the
    desired amount's EMI fits within it → Borrow; if it doesn't but the safe ceiling is still
    meaningfully > 0 → Borrow Less (recommend the safe ceiling amount); if the safe ceiling is at
    or near ₹0 even before any new loan → Don't Borrow.
  - This was validated against all three borrowers: Priya and Ravi both correctly fall through to
    Layer 2 and land on Borrow Less (see current numbers in Part 2); Anita is caught by Layer 1
    alone — and critically, her ratio math (32.4%) would NOT have caught her on its own, proving
    both layers are load-bearing.
- **The safe ceiling must survive its own stress test by construction.** Two bugs were found by
  testing the code against the three hand-worked borrowers (see `rules.py` comments tagged
  BUGFIX 1 and BUGFIX 2):
  - BUGFIX 1: the safe-cap formula had `min`/`max` backwards, which collapsed the safe cap to
    near-zero for any borrower with little/no existing debt (caught on Ravi).
  - BUGFIX 2: the safe loan ceiling and the required stress test (rate +2 pts, income −10%) were
    two independent mechanisms that could disagree — a recommended amount could pass the margin
    check yet fail its own stress test (caught on Priya). Fixed by computing a
    stress-survival ceiling directly and taking the stricter of the two ceilings, so the
    stress test now holds by construction for every case.
- **Don't Borrow verdict reshapes the other three outputs, it doesn't blank them:**
  | Output | Borrow / Borrow Less | Don't Borrow |
  |---|---|---|
  | Max amount | A number to negotiate with | ₹0 now, plus the specific checkable conditions that would change this |
  | Fair rate | A band to compare a lender's quote against | Redirected to existing debt: is the borrower already overpaying? (Tested on Anita: refinancing her small, short-tenure existing debt only saved ~₹100-200/month — the app should say this honestly rather than force a bigger finding than exists) |
  | EMI ceiling | A ceiling for new debt | The shortfall — how far current obligations already sit from sustainable |
  | Negotiation Card | Negotiate a lender's quote down | Decline a lender's offer, with a reason |

### 1.4 Question design (Tier 1 / Tier 2), as designed so far
**Tier 1 (must-ask, ~8-9 questions):** purpose · amount wanted · loan type initially wanted ·
net income + income type (salaried/self-employed/informal) · *(conditional: only if
self-employed/informal)* do you file ITR + declared annual income · existing EMIs (list) ·
household expenses/rent · age · credit score (**three-way: known number / unknown / never taken
formal credit**). The conditional ITR question is the actual mechanism that makes a salaried
employee and a kirana owner see different questions from Tier 1 onward, not just in Tier 2.

**Tier 2 (additional, adaptive — each one must move an output):**
| Question | Shown when | Output(s) it moves |
|---|---|---|
| Income stability (job tenure / years in business) | Always | Narrows income confidence; can shift which end of the FOIR range applies |
| Variable-income share (%) | Self-employed/informal only | Replaces the flat 30% haircut with a borrower-specific figure (already implemented in `assess_income()`) |
| Existing loan detail (rate, remaining tenure, EMI) | If ≥1 existing EMI | Replaces an estimated tenure/EMI with real figures |
| Card utilisation | If credit score known | Nudges rate band within the published range |
| Past bounces (last 3-6mo) | Always | Feeds Layer-1 hard stop directly |
| Emergency savings (months) | Always | Widens/narrows the safe-cap margin |
| Collateral value & encumbrance | Self-employed/informal, or NTC, or large ask | Triggers secured-product routing |
| Co-applicant income | Always, optional | Feeds household income *if* confirmed joint application (counting rule still open, see Part 3) |
| Upcoming large expenses | Always | Temporarily reduces safe ceiling |
| What will the loan earn (ROI) | Only if purpose = business/income-generating | Can offset EMI capacity; can shift verdict itself |
| Offers already received | Always, optional | Doesn't change computed numbers — sharpens the Negotiation Card comparison only |

---

## PART 2 — Current file/build status (as of this handoff)

Project folder: `/home/claude/borrower-copilot/` (working directory — not yet the final
deliverable location; final submission files should go in `/mnt/user-data/outputs/`).

| File | Status |
|---|---|
| `rules.py` | **Done and validated.** Pure functions, no UI code. Implements income assessment (§1.3), FOIR ceilings, LAP routing, two-layer verdict logic, stress test, predatory-debt soft flag, emergency-savings adjustment, productive-loan ROI credit. Both known bugs fixed, plus two Part-3 open questions (#1, #4) resolved and wired in. Verified against all three borrowers (numbers below). |
| `rules.js` | Legacy/abandoned — superseded by `rules.py`. Delete or ignore. |
| `app.py` (Streamlit UI) | **Done.** Full Tier 1 + adaptive Tier 2 flow, calls `rules.run_assessment()` directly, renders all four outputs + Negotiation Card. Tested via Streamlit's `AppTest` framework: initial load, default submit flow, and the most complex conditional branch (self-employed + existing loans with rate detail + collateral) all run with zero exceptions. Honestly flags in-app (via an expander) which collected Tier-2 answers aren't yet wired into the calculation (job/business tenure, card utilisation, co-applicant income, upcoming expenses). |
| Custom CSS (ledger/passbook design) | **Done**, inline in `app.py` via `st.markdown(unsafe_allow_html=True)`. Implements the palette/type/layout system from §1.2. Not yet visually reviewed on an actual phone screen — worth doing before final submission. |
| `README.md` (run instructions) | **Done.** `pip install streamlit && streamlit run app.py`, plus a short note on where to edit a rule. |
| `RULES.md` (deliverable) | **Done and in sync with `rules.py`** as of this handoff, including both bugfixes and the two resolved Part-3 items (predatory-rate soft flag, Borrow-Less rounding). |
| `OPEN_QUESTIONS.md` | **Drafted.** Four items resolved total (#1, #4, #5, #6); five still genuinely open (#2, #3, #7, #8, #9). |
| Three formal run-through documents (deliverable #3) | **Not yet written as a standalone deliverable file** — reasoning exists and is validated in code output; next step is assembling it into the actual submission format. |
| Five-minute walkthrough (deliverable #4) | **Not started.** |

**Deliverable location:** all four files above (`app.py`, `rules.py`, `README.md`, `RULES.md`) are
now copied into `/mnt/user-data/outputs/borrower-copilot/` as a self-contained, runnable folder —
this is the actual submission folder, not just working files.

**Current validated output (after both bugfixes and the two resolved Part-3 items), from
`rules.py` directly:**
- **Priya:** verdict `borrow_less`, recommended amount ≈ ₹3,25,000 (rounded), stress test holds ✓
- **Ravi:** verdict `borrow_less` (secured/LAP route), recommended amount ≈ ₹11,00,000 (rounded,
  includes a modest ROI credit if he states expected earnings from the loan) — a refinement from
  an earlier, looser hand-calculation that suggested a plain "Borrow" verdict; the corrected,
  consistent methodology places his safe ceiling below his ₹15,00,000 ask, so the honest verdict
  is Borrow Less, not Borrow. Legitimate finding, not a regression.
- **Anita:** verdict `dont_borrow` (Layer-1 hard stop on bounced payment)

**Constants currently in `rules.py`** (all named, all near the top of their section, all meant to
be easy to find and change live):
`DEFAULT_INCOME_HAIRCUT = 0.70` · `FOIR_CAPS = {salaried: 0.50, self_employed: 0.45,
informal: 0.45}` · `MARGIN_ABOVE_CURRENT = 0.07` · `MARGIN_BELOW_LENDER = 0.05` ·
`LTV = {commercial: 0.55, residential: 0.65}` · `RATE_BANDS` (personal unsecured prime 10.5-12.5%,
personal unsecured standard 13-16%, business unsecured informal 18-24%, LAP commercial 9-11.5%,
LAP residential 8.5-10.5%, MFI reference 19-28%) · `STRESS_RATE_BUMP_PCT = 2.0` ·
`STRESS_INCOME_DROP_PCT = 0.10`.

---

## PART 3 — Genuinely unresolved (do not silently decide these — surface them)

Full detail and discussion points already written up in `/mnt/user-data/outputs/OPEN_QUESTIONS.md`.
Summary:
1. ~~Should "existing debt already at 30%+ interest" be its own Layer-1 hard stop, a ratio input,
   or a soft confidence flag?~~ **Resolved — soft flag**, implemented as a safe-cap penalty plus
   a visible warning on the card.
2. Should household-distress signals beyond debt ratios (single earner + dependents + no stated
   savings) affect the verdict or just widen confidence? Not currently modeled at all.
3. Co-applicant income — question exists in Tier 2 and is collected in `app.py`, but the counting
   rule (how it should change the numbers) is still undecided — currently not wired into `rules.py`
   at all, and `app.py`'s "what this doesn't account for yet" panel says so honestly.
4. ~~"Borrow Less" recommended amount — round vs. exact vs. range?~~ **Resolved** — round down to
   a clean number, present as a ceiling ("up to ₹X").
5. *(Resolved)* Self-employed haircut scaling — resolved by the variable-income-share Tier-2
   question; already implemented in code.
6. *(Resolved)* Existing-debt tenure assumption — resolved by the "existing loan detail" Tier-2
   question; fallback behavior when that question is skipped (widen band vs. keep a point
   estimate) still needs to be written into the code, currently just documented as a gap.
7. Loan tenure — always show max-tenure as the anchor, or ask the borrower's preference as a
   must-question? Currently hardcoded defaults (60mo unsecured, 120mo LAP), not asked.
8. Rate band — currently discrete profile-based judgement (e.g. credit score ≥750 vs not), not a
   continuous formula. Undecided whether to build a finer scale.
9. Not built at all: full product bands beyond personal loan / LAP (home loan, gold loan,
   two-wheeler, business loan specifics) — explicitly not required to be comprehensive per the
   brief ("breadth of loan products... not scored"), but should at least be a documented decision
   to skip, not an oversight.

---

## PART 4 — Step-by-step plan for what's left

Do these in order. Each step assumes the prior ones are done. If picking this up fresh, start by
running the validation script in Part 2 to confirm `rules.py` still behaves as documented above.

### Step 1 — ✅ DONE — Sync RULES.md with the final, bugfixed rules.py
`RULES.md` now reflects both bugfixes and the two resolved Part-3 items (predatory-rate soft
flag, Borrow-Less rounding), with a changelog note.

### Step 2 — ✅ DONE — Decided the Part-3 open questions that affect code
Resolved: #1 (predatory-rate → soft flag) and #4 (Borrow Less → rounded ceiling), both now live
in `rules.py`. Deliberately left open (don't block the UI): #2, #3, #7, #8, #9 — see Part 3.

### Step 3 — ✅ DONE — Built `app.py` (Streamlit UI)
Full Tier 1 flow with the conditional ITR question, adaptive Tier 2 questions per the §1.4 table,
calls `rules.run_assessment()` directly with no duplicated calculation. Tested via `AppTest`
(initial load, default submit, and the self-employed + existing-loans + collateral branch) —
zero exceptions in all three passes.

### Step 4 — ✅ DONE — Applied the custom CSS (design system from §1.2)
Ledger/passbook palette, IBM Plex Serif/Sans pairing, ledger-rule dividers, stamped Negotiation
Card treatment — all inline in `app.py`. **Not yet reviewed on an actual phone screen** — do this
before final submission, since "works on a phone" is directly scored.

### Step 5 — ✅ DONE — Wrote `README.md`
Two-command run instructions (`pip install streamlit`, `streamlit run app.py`), plus a note on
where to edit a rule for the live follow-up.

### Step 6 — ✅ DONE — Assemble the three formal run-throughs (deliverable #3)
`THREE_RUNTHROUGHS.md` written directly from `rules.py` output (not hand-recomputed) — questions
asked, all four outputs, and Negotiation Card text for Priya, Ravi, and Anita, plus a
cross-borrower summary table showing each one exercises a different part of the rules engine.

### Step 7 — ✅ DONE — Record/write the five-minute walkthrough (deliverable #4)
`WALKTHROUGH_SCRIPT.md` — a timed speaking outline (not a verbatim script, deliberately, since the
live follow-up requires real understanding): the gap the app addresses, a live demo of Ravi's case
(chosen because it exercises the most mechanics — income blending, collateral routing, ROI credit),
one traced "why" from RULES.md, an honest "what's next" list pulled from the genuinely open
questions, and an equally honest "what I'd cut" list. Ends with a rehearsal check: change one
constant, re-run a borrower, confirm you can explain the movement in one sentence.

### Step 8 — Final packaging and self-check against the scoring rubric
Confirm all four deliverables sit at the root of the repo as required. Re-read the scoring table
in Part 0 and check each row has a concrete, findable answer in the submission — not just "we
discussed this," but a visible artifact (a RULES.md row, a code comment, a walkthrough line).

### Step 9 — Rehearse the live follow-up
Before submitting, practice: pick one constant from the list in Part 2 (e.g. `MARGIN_ABOVE_CURRENT`,
or a `FOIR_CAPS` value), change it, re-run all three borrowers, and confirm you can explain in one
sentence why each output moved the way it did. If any change produces a result you can't explain
immediately, that's a sign the rule's "why" isn't actually understood yet — go back to Part 1.3
and re-read the reasoning for that rule before the real interview.
