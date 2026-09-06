# RULES.md — Borrower Copilot

This document is the source of truth for every threshold, band, and assumption the app uses.
If a number appears in the app and isn't in this table, that's a bug in this document, not
an excuse in the code.

Every row states: **what it is · the value · why · where it came from**. "My judgement" means
no published source exists for this exact figure — it's a reasoned assumption, and the reasoning
is the point, not the number.

---

## 1. Income assessment

| Rule | Value | Why | Source |
|---|---|---|---|
| Salaried income basis | Net (take-home) monthly income, as stated | This is what's actually available to service EMIs — lenders and borrowers should use the same number | Standard practice |
| Self-employed / informal income basis | Blend of self-declared cash income and ITR, **not** either alone | ITR is often understated for tax reasons; self-declared cash is unverifiable and often optimistic. Neither alone is trustworthy. | My judgement — real lenders solve this with bank statement analysis (6-12mo average credits) or GST turnover, which this app cannot do since it has no bureau/bank pull |
| Self-employed blend formula | `assessed_income = midpoint(self-declared range) × 0.70` | The 30% haircut prices in the fact we cannot verify the self-declared figure. It's not derived from any published lender formula. | My judgement — **explicitly flagged as the weakest assumption in the model.** In a production version this row is replaced entirely by verified bank-statement data. |
| Unknown / not provided income | Never defaulted to zero or to the lowest band | Treating missing data as the worst case punishes honest "I don't know" answers and produces false "don't borrow" verdicts | Rule required by brief ("Unknown is never zero") |

---

## 2. Affordability — FOIR (Fixed Obligation to Income Ratio)

**Definition used:** `FOIR = (existing EMIs + proposed EMI + rent) ÷ net monthly income`

This includes rent. Earlier drafts of this doc excluded rent from the lender-side view — that
was wrong. Most published lender-facing FOIR formulas (e.g. L&T Finance's own worked example)
include rent as a fixed obligation. Corrected here.

| Rule | Value | Why | Source |
|---|---|---|---|
| Lender-view FOIR cap (salaried, good credit) | 50% | Commonly cited industry range is 40-60%, scaling up with income and credit strength. 50% is a defensible mid-point for a salaried, prime-credit borrower like Priya. | Published range (multiple lender-facing sources); specific point chosen by judgement |
| Lender-view FOIR cap (self-employed / informal) | 45% | Lenders apply a stricter cap to volatile/unverified income than to salaried income | My judgement, directionally consistent with published guidance that self-employed income is treated more conservatively |
| Safe-view cap | Lender cap **minus a margin**, not a different obligations formula | The gap between "lender will approve" and "borrower should take" isn't about what counts as an obligation — it's about margin for error. Both views should count the same things. | My judgement |
| Safe-view cap — sanity floor | Must be **higher** than the borrower's current (pre-new-loan) obligation ratio | A safe cap below what someone is already living at is a broken formula, not conservatism — see Priya's case, where a flat 40% cap nonsensically implied she could barely afford her *existing* rent+EMI | Derived / logic check, not a published figure |
| Stress test (required output) | Recompute the safe loan's EMI at **rate +2 percentage points** and **income −10%**; verdict must still hold under lender's cap | Directly required by the brief ("include one stress case: income drops or rate rises") | Brief requirement; magnitude (+2%, −10%) is my judgement — reasonable single-shock sizing, not a regulatory figure |

---

## 3. Credit score & credit history

| Rule | Value | Why | Source |
|---|---|---|---|
| CIBIL weighting cited to borrower (for explainability only, not recomputed) | ~30-35% payment history, ~25-30% credit utilization, ~15-25% credit mix/history length, ~10-20% inquiries/other | Explains *why* score matters and what improves it — we do not and cannot recompute an actual CIBIL score, the real algorithm is proprietary | Approximate figures published by multiple lender/aggregator sites; exact CIBIL algorithm is not public — treat as directionally correct, not exact |
| Score stated but "I don't know it" | Treated as unknown → widens confidence band on rate output, does not default to a poor-credit assumption | Same "unknown ≠ zero" principle as income | Brief requirement |
| NTC (New-to-Credit) — never taken formal credit, not just "unknown" | Treated as a **distinct case from "unknown score"**, not scored numerically | There is no published NTC risk premium — real lenders price this from proprietary historical default data we don't have. Inventing a numeric penalty here would be a fabricated number with no grounding. | My judgement — deliberately avoided a number I couldn't defend |
| NTC handling rule | If borrower is NTC **and** owns unencumbered collateral → route to secured product evaluation (see §4) before evaluating unsecured options | Turns an unanswerable pricing question ("how much should NTC cost him?") into an answerable routing question ("does collateral make his credit history irrelevant?") | My judgement |

---

## 4. Secured product routing (Loan Against Property)

| Rule | Value | Why | Source |
|---|---|---|---|
| Trigger condition | Borrower owns unencumbered property AND is NTC or has thin/unverifiable income | These are exactly the profiles where unsecured lending is expensive or unavailable, and where collateral changes the outcome most | My judgement, following from the Ravi case |
| LTV — commercial property | 55% | Multiple lenders (SBI, Aditya Birla, Poonawalla, others) publish commercial LAP LTV in the 55-60% range, vs 65-75% for residential | Published, cited |
| LTV — residential property | 65% | Conservative point within the commonly published 65-75% residential range | Published range, point chosen by judgement |
| Collateral-based ceiling | `property_value × LTV` | Defines the absolute maximum regardless of income | Formula standard across sources |
| Binding constraint rule | Actual max loan = **lower of** (collateral-based ceiling, income-based safe ceiling) | A collateral ceiling that exceeds what income can service is not actually usable — both constraints must hold | Standard underwriting logic |
| Indicative rate — commercial LAP | 9-11.5% p.a. | Within the range published across major LAP lenders as of 2025-26 | Published, cited |
| Indicative rate — unsecured business loan (NTC, informal income) | 18-24% p.a. | Reflects NBFC/fintech pricing for higher-risk, undocumented-income borrowers | Market-typical range, not a single published source — treat as directional |

---

## 5. Output behavior when verdict = Don't Borrow

A "Don't Borrow" verdict cannot mean the other three outputs go blank — the brief requires every
borrower walks away with something actionable. But what's actionable is different in kind, not
just degree, from a Borrow/Borrow Less verdict.

| Output | Borrow / Borrow Less | Don't Borrow |
|---|---|---|
| Max amount | A number to negotiate with | ₹0 new borrowing now, **plus the specific, checkable conditions** that would change this (e.g. "no missed payments for 3 consecutive months") |
| Fair rate | A band to compare a lender's quote against | Redirected to **existing debt**, if any: is the borrower already paying above a fair rate on what they owe? (Tested on Anita — see below: this can be a weak lever if existing debt is small/short, and the app should say so honestly rather than force a finding) |
| EMI ceiling | A ceiling for new debt | The **shortfall**, quantified: how far current obligations already sit from a sustainable ratio, framed as "fix this before adding anything" |
| Negotiation Card | A card to negotiate a lender's quote down | A card to **decline** a lender's offer with a reason, not negotiate it — e.g. "Not now, because—" instead of "11-12.5%, because—" |

This was tested against Anita: refinancing her existing ₹35,000 at a fair MFI rate (19-24%,
grounded in MFIN's Feb-2026 member data) instead of her current 30%+ only saves ~₹100-200/month,
because the debt is small and short-tenure — the rate gap doesn't have time to compound into
real money. The honest output here is not a forced "you'd save X," it's flagging that the real
problem is being trapped in a repeated-borrowing pattern, not the rate on any single loan.

---

## 6. Verdict logic (two-layer)

**Layer 1 — Hard stops, checked first, independent of ratio math:**

| Rule | Value | Why | Source |
|---|---|---|---|
| Recent missed/bounced payment | Any bounce in trailing 3 months → verdict is Don't Borrow, full stop | Matches real underwriting: delinquency is typically a hard rejection criterion for most lenders, not just a ratio input. Validated on Anita — her ratio check alone (32.4%) would have passed her; the bounce is what correctly blocks her. | My judgement, consistent with standard underwriting practice |
| Existing debt already at predatory rate (~30%+) | **Resolved: soft flag, not a hard stop.** Shaves 5 points off the safe cap (quantifiable tightening) and surfaces as a visible warning on the card, regardless of verdict. | A hard stop should reflect *behavior* (a missed payment), not just *price paid* — a borrower can carry an expensive short-term loan and still be current. A blanket hard stop here risks a false Don't-Borrow for someone actually managing their debt. | My judgement |

**Layer 2 — Ratio check, only runs if no hard stop fired:**

| Rule | Value | Why |
|---|---|---|
| Borrow | Required EMI for desired amount ≤ safe ceiling (§2) | Borrower can service the full ask within a safe margin |
| Borrow Less | Required EMI > safe ceiling, but safe ceiling itself is meaningfully > 0 | Ask is a stretch, not a red flag — recommend the safe ceiling instead, **rounded down to a clean number and framed as "up to ₹X"** rather than a false-precision figure like ₹3,25,947 |
| Don't Borrow (ratio-driven) | Safe ceiling is at or near ₹0 even before adding a new loan | Existing obligations alone already consume the safe margin |

**Validated against all three borrowers:**
- Priya: no hard stop → ratio check fails at full ₹8L ask, safe ceiling >0 → **Borrow Less** ✓
- Ravi: no hard stop → ratio check passes via secured (LAP) route → **Borrow** ✓
- Anita: hard stop fires (bounce) → **Don't Borrow** — and confirmed the ratio layer alone (32.4%) would have missed this, proving both layers are load-bearing, not redundant

---

## 7. Question design

**Tier 1 — Must-ask (8-9 questions, produces all four outputs at wide/low confidence):**

| # | Question | Type | If skipped |
|---|---|---|---|
| 1 | Purpose of loan | Categorical | Defaults to "general", widens confidence; also drives which Tier-2 questions unlock |
| 2 | Amount wanted | Number | Required — outputs can't be produced without it |
| 3 | Loan type initially wanted | Categorical | Inferred from purpose if skipped (e.g. wedding → personal loan guess); may be overridden by the app's own routing (see Ravi) |
| 4 | Net monthly income + income type (salaried / self-employed / informal-gig) | Number + categorical | Required — this is the branch point for the entire rest of the flow |
| 5 | *(conditional — only if self-employed/informal)* Do you file ITR? Declared annual income? | Bool + number | If skipped, ITR treated as unavailable; rely on self-declared income with the standard haircut (§1) alone |
| 6 | Existing EMIs (amount + rough purpose, per loan) | List | If none, record zero; skips Tier-2 "existing loan detail" question |
| 7 | Household expenses / rent | Number | If unknown, widen confidence band rather than defaulting to zero — **no defensible city-tier expense benchmark has been sourced yet; using one as a fallback is still open** |
| 8 | Age | Number | Required — feeds tenure-cap logic (age + tenure vs. typical lending age ceilings) |
| 9 | Credit score | **Three-way**: known number / unknown / never taken formal credit | This three-way split (not just known/unknown) is what operationalizes the NTC-vs-unknown distinction in §3 |

Question 5 being conditional is the actual mechanism behind the brief's "a salaried IT employee
and a kirana owner should not see the same questions" rule — the branch happens inside Tier 1,
not just in which Tier-2 questions appear later.

**Tier 2 — Additional (adaptive, each row must move an output or it's cut):**

| Question | Shown when | Output(s) it moves | Evidence |
|---|---|---|---|
| Income stability (job tenure / years in business) | Always | Narrows confidence on income; can shift which end of the FOIR cap range applies | Priya's 5yr MNC tenure, Ravi's 14yr shop — both used as informal stability signals |
| Variable-income share (% irregular/seasonal/commission) | Self-employed / informal only | **Replaces the flat 30% haircut in §1 with a borrower-specific figure** | Resolves OPEN_QUESTIONS.md #5 — don't scale the haircut by range-width heuristics, just ask directly |
| Existing loan detail (rate, remaining tenure, EMI) | Only if Tier-1 Q6 has ≥1 existing EMI | Replaces estimated tenure/EMI with real figures | **Resolves OPEN_QUESTIONS.md #6** — Anita's assumed 6-month tenure becomes unnecessary once asked directly |
| Card utilization | Only if credit score is known | Nudges rate band within the published range (§3) | — |
| Past bounces (any missed payment, last 3-6mo) | Always | Feeds Layer-1 hard stop directly | Anita's verdict |
| Emergency savings (months of expenses covered) | Always | Widens/narrows the safe-cap margin in §2 | — |
| Collateral value & encumbrance status | Self-employed/informal, or NTC, or large ask relative to income-only eligibility | Triggers §4 secured-product routing | Ravi's case |
| Co-applicant income | Always, optional | Feeds household income **if confirmed joint application** | Addresses OPEN_QUESTIONS.md #3 — still needs the counting rule decided, but the question itself is what surfaces it |
| Upcoming large expenses | Always | Temporarily reduces safe ceiling for the near-term window | — |
| What will the loan earn (expected ROI) | Only if purpose = business / income-generating | Can offset EMI capacity if a credible figure is given; potentially shifts verdict itself | Relevant to both Ravi and Anita's scooter ask |
| Offers already received (existing lender quote) | Always, optional | Doesn't change computed numbers — sharpens the **Negotiation Card** comparison specifically | — |

---

## 8. What's still TODO in this draft

- [x] Anita's case (over-indebted / "don't borrow" trigger) — derived, §6
- [x] Explicit verdict thresholds — derived, §6, validated against all three borrowers
- [x] Full must-question list (Tier 1) and additional-question list (Tier 2) — derived, §7
- [ ] EMI ceiling output — currently implicit in §2, needs its own explicit rule + one-sentence "why" template
- [ ] Household/co-applicant income counting rule — Tier-2 question now surfaces this (§7), but the actual rule for *how* co-applicant income gets folded into the numbers is still open — OPEN_QUESTIONS.md #3
- [ ] Product bands beyond personal loan / LAP: home loan, gold loan, two-wheeler, business loan specifics
- [ ] City-tier household expense fallback — needed for Tier-1 Q7 when household expenses are unknown; no defensible benchmark sourced yet
- [x] "Borrow Less" recommended-amount presentation — resolved: round down to a clean number, frame as "up to ₹X"

---

## Change log

- v0.3 — Found and fixed two verdict-logic bugs, both caught by deep-dive testing after the app
  was built, not before:
  - **The verdict boundary check was comparing a borrower's desired loan against the wrong
    product's rate.** It always used a generic unsecured rate (e.g. 21% for Ravi) even for
    borrowers who get routed to a secured loan (Ravi's actual LAP rate: 9-11.5%). This made Ravi's
    verdict say "Borrow Less" when, under his real routed terms, his full ₹15,00,000 ask actually
    fit. Fixed: routing (secured vs unsecured, and which rate/tenure) is now decided *before* the
    verdict check runs, and the check uses those actual terms.
  - **Fixing the above then exposed a second bug**: once Ravi's verdict flipped to "Borrow" for
    the full amount, his recommended amount stopped being checked against the stress test at
    all — "Borrow" verdicts had never been passed through the stress-consistent ceiling from
    v0.2's fix, only "Borrow Less" ones had. Fixed by computing one unified, stress-consistent
    safe ceiling *before* the verdict decision, and using that same number both to decide the
    verdict boundary and to cap the recommended amount — so every verdict (not just Borrow Less)
    now provably survives its own stress test by construction.
  - Net effect on Ravi's case: verdict is Borrow Less at ₹12,00,000 (not the full ₹15,00,000) —
    this is now the *correct*, stress-tested answer, not a workaround.
- v0.2 — Corrected FOIR to include rent in both lender and safe views (previous draft incorrectly
  excluded rent from the lender view). Replaced "different obligation definitions" mechanism with
  "margin + stress test" mechanism for the lender/safe split.
- v0.1 — Initial draft from Priya and Ravi walkthroughs.
