# Three Run-Throughs — Priya, Ravi, Anita

Every number below is the actual output of `rules.py` for the answers shown — nothing here was
hand-recomputed or approximated for presentation. Run `rules.run_assessment()` with the same
answers dict to reproduce any of these exactly.

---

## Priya — 29, Bengaluru, salaried software engineer

### Questions asked and answers given

**Tier 1:**
| Question | Answer |
|---|---|
| Purpose | Wedding |
| Amount wanted | ₹8,00,000 |
| Loan type wanted | Personal loan |
| Income type | Salaried |
| Net monthly income | ₹1,10,000 |
| Existing EMIs | ₹14,000 (car loan) |
| Rent / housing cost | ₹28,000 |
| Age | 29 |
| Credit score | Known — 780 |

*(The ITR question was skipped — it only applies to self-employed/informal income.)*

**Tier 2 (adaptive — shown because she's salaried with a known score):**
| Question | Answer |
|---|---|
| Years at this job | 5 |
| Card utilisation | 25% |
| Missed a payment in last 3 months? | No |
| Emergency savings | Not provided |
| Offer already received? | 14% |

*(Variable-income-share and collateral questions did not appear — not applicable to a stable
salaried profile with no stated property.)*

### Outputs

**Verdict: BORROW LESS**
> *"The amount you want is more than a lender would sanction safely — a smaller amount fits your safe capacity."*

| Output | Value |
|---|---|
| A lender would likely sanction | ₹5,91,108 |
| You can safely carry | ₹3,25,947 |
| **Recommended amount** | **₹3,25,000** |
| Fair rate for her profile | 10.5% – 12.5% |
| Recommended product | Unsecured personal loan |
| Safe monthly EMI ceiling | ₹7,700 |
| Stress check (rate +2pts, income −10%) | EMI becomes ₹7,478 — still holds |

**Why the ceiling is ₹3,25,000 and not ₹8,00,000, in one sentence:** her rent and existing car
EMI already use 38.2% of her income, and a safe margin above that (45.2%) only leaves ₹7,700/month
for a new loan — nowhere near the ~₹17,600/month her full ask would need.

**Negotiation Card:**
> *"Lender quote too high? Fair for your profile is 10.5-12.5%."*
> Her stated lender quote was 14% — this card gives her room to push back with a number, not just a feeling.

---

## Ravi — 42, Mysuru, self-employed (kirana store)

### Questions asked and answers given

**Tier 1:**
| Question | Answer |
|---|---|
| Purpose | Business / income-generating |
| Amount wanted | ₹15,00,000 |
| Loan type wanted | Business loan |
| Income type | Self-employed |
| Income range | ₹40,000 – ₹80,000/month |
| Files ITR? | Yes — ₹4,20,000/year declared |
| Existing EMIs | None |
| Rent / housing cost | ₹0 (owns premises) |
| Age | 42 |
| Credit score | Never taken formal credit (NTC) |

*(The ITR sub-question appeared specifically because he selected self-employed — this is the
Tier-1 branch that makes his flow different from Priya's from question 5 onward.)*

**Tier 2 (adaptive — shown because he's self-employed and NTC):**
| Question | Answer |
|---|---|
| Years running the business | 14 |
| Variable income share | 60% |
| Missed a payment in last 3 months? | No |
| Owns unencumbered property? | Yes — commercial, ₹45,00,000 |
| Co-applicant income | ₹18,000 (wife) — *collected, not yet counted, see note below* |
| Expected monthly earning from this loan | ₹8,000 |

### Outputs

**Verdict: BORROW LESS**
> *"The amount you want is more than a lender would sanction safely — a smaller amount fits your safe capacity."*

| Output | Value |
|---|---|
| Assessed income | ₹45,600/month (self-declared midpoint × income-stability-derived haircut, cross-checked against ITR) |
| A lender would likely sanction | ₹18,36,168 |
| You can safely carry | ₹12,74,359 |
| **Recommended amount** | **₹12,00,000** |
| Fair rate for his profile | 9.0% – 11.5% |
| **Recommended product** | **Loan Against Property (commercial) — not unsecured** |
| Safe monthly EMI ceiling | ₹22,240 (includes a ₹4,000/month credit from his own stated earning estimate) |
| Stress check (rate +2pts, income −10%) | EMI becomes ₹17,390 — still holds |

**Why LAP and not the unsecured business loan he initially selected, in one sentence:** he has no
credit history to price an unsecured loan against, but he owns his shop outright — pledging it
drops his rate from an 18-24% unsecured band to 9-11.5%, which is why the app overrides his
initial product choice.

**Why ₹12,00,000 and not his full ₹15,00,000 ask:** even with his property as collateral
(which alone would support up to ₹24,75,000) and credit for his stated business ROI, his
*income* — the stricter of the two constraints — only safely supports ~₹12.7L before rounding.

**Note on his wife's ₹18,000 income:** collected but **not currently added** to his eligibility
figures above, since this isn't confirmed as a joint application (see OPEN_QUESTIONS.md #3). If
he applies jointly with his wife as co-applicant, his eligibility would likely rise — worth raising
with the lender directly.

**Negotiation Card:**
> *"Lender quote too high? Fair for your profile is 9.0-11.5%, via Loan Against Property (commercial) — not unsecured."*

---

## Anita — 35, Hubballi, informal (delivery rider + tailoring)

### Questions asked and answers given

**Tier 1:**
| Question | Answer |
|---|---|
| Purpose | Vehicle to increase income (electric scooter for delivery) |
| Amount wanted | ₹1,50,000 |
| Loan type wanted | Vehicle loan |
| Income type | Informal / gig work |
| Income range | ₹26,000 – ₹30,000/month |
| Files ITR? | No |
| Existing EMIs | ₹6,354 (three app loans, ₹35,000 outstanding, 30%+ rate) |
| Rent / housing cost | ₹0 |
| Age | 35 |
| Credit score | Not sure |

**Tier 2 (adaptive — shown because she's informal-income with existing debt):**
| Question | Answer |
|---|---|
| Years at this income source | 2 |
| Variable income share | 70% |
| Missed a payment in last 3 months? | **Yes** |
| Emergency savings | 0 months |
| Expected monthly earning from this loan | ₹3,000 |

*(Collateral question appeared but she has none to offer — no property.)*

### Outputs

**Verdict: DON'T BORROW**
> *"A payment was already missed on existing debt in the last 3 months — adding a new loan now makes that worse, not better."*

This is a **hard stop** — it fires independently of her ratio math. Worth noting explicitly: her
ratio alone (31.5% obligation ratio before any new loan) would **not** have blocked her under the
45% lender cap for informal income. It's specifically the missed payment that correctly catches
this case — proof the two-layer verdict logic is doing real work, not redundant with the ratio
check.

| Output | Value |
|---|---|
| Amount to borrow now | ₹0 |
| Path back to eligibility | Stay current on all existing payments for 3 consecutive months, with no new bounces, then re-run this assessment |
| On her existing debt | Her three app loans (30%+ APR) are priced above even India's regulated microfinance segment (currently 19-28% APR). Refinancing may or may not meaningfully help depending on the loan's size and remaining tenure — worth checking both, but shouldn't be assumed to be a fix on its own. |
| Existing-debt flag | Yes — 30%+ rate detected, independently of the bounce |

**Negotiation Card (repurposed for a Don't Borrow verdict — a decline script, not a rate to negotiate):**
> *"If offered ₹1,50,000 today: decline. A payment was already missed on existing debt in the last 3 months — adding a new loan now makes that worse, not better."*

**What she still gets to act on tomorrow, even with a "no":** a specific, checkable condition
(3 clean months) rather than a dead end, and an honest note that her real problem is the missed
payment and being in a repeat-borrowing pattern — not primarily the rate she's paying on this
particular ₹35,000.

---

## Cross-borrower summary (for quick reference)

| | Priya | Ravi | Anita |
|---|---|---|---|
| Verdict | Borrow Less | Borrow Less | Don't Borrow |
| Trigger | Ratio check (Layer 2) | Ratio check (Layer 2) | Hard stop (Layer 1) |
| Recommended amount | ₹3,25,000 (of ₹8,00,000 asked) | ₹12,00,000 (of ₹15,00,000 asked) | ₹0 |
| Product routing | Unsecured personal loan (as asked) | **Rerouted** to secured LAP from unsecured business loan | N/A |
| Rate band | 10.5–12.5% | 9.0–11.5% | N/A — existing debt flagged instead |
| Distinguishing mechanism exercised | Safe-margin ceiling below lender ceiling | Collateral routing + ROI credit + income haircut | Hard-stop layer catching what ratio math alone would miss |

Each borrower exercises a genuinely different part of the rules engine — this was by design, not
coincidence (see PROJECT_PLAN.md Part 0: "three borrowers... your app should give each of them
something they could act on tomorrow").
