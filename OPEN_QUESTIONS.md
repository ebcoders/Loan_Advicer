# Open Questions — To Be Discussed

Unresolved design decisions, logged as they came up, with the tradeoffs on each side rather than
a forced answer. Each item should eventually move into RULES.md once decided, with its final
value and reasoning.

---

### 1. ~~Should "existing debt already at 30%+ interest" be its own hard stop?~~ RESOLVED
**Soft flag, not a hard stop.** Implemented in `rules.py` as `PREDATORY_RATE_SAFE_CAP_PENALTY`
(5 points shaved off the safe cap) plus a `predatory_debt_flag` surfaced on the output regardless
of verdict. Reasoning: a hard stop should reflect *behavior* (a missed payment — already covered
by the bounce hard stop) rather than *price paid*, since a borrower can carry an expensive
short-term loan and still be current on it. Verified: Anita with predatory-rate debt but no
bounce now correctly gets `borrow_less` (heavily constrained, not auto-blocked) rather than an
automatic Don't Borrow.

---

### 2. Household distress signals beyond debt ratios
Anita's profile has other red flags the ratio math doesn't touch at all: single income earner,
two dependents, husband unemployed 8 months, no stated savings/buffer.

- Should any of these become their own rule (e.g. "single earner + dependents + zero stated
  savings = confidence penalty"), or is that over-engineering for signals we can't consistently
  collect across all borrower types?
- If yes: does it adjust the *verdict*, or just widen the confidence band / add a caveat line?

---

### 3. Co-applicant / spousal income
Flagged first on Ravi (wife earns ₹18,000, currently excluded from his numbers) and cuts the
opposite way on Anita (husband unemployed, so household income is *more* fragile than her
individual number suggests).

- Do we ever count a spouse's income without them being a formal co-applicant?
- If not counted: should the app still *surface* the option ("adding a co-applicant could raise
  your eligibility") as an actionable note on the card?
- For Anita specifically: should a non-earning dependent spouse actively *worsen* her assessed
  affordability (one income supporting more people), even though FOIR as defined doesn't have a
  dependents term at all?

---

### 4. ~~"Borrow Less" — how much less?~~ RESOLVED
Round the safe ceiling down to a clean number (step size scales with magnitude — nearest ₹5,000
under ₹1L, nearest ₹25,000 under ₹10L, nearest ₹1,00,000 above that) and present as a ceiling
("up to ₹X"), not a single false-precision target. Implemented as `round_down_ceiling()` in
`rules.py`. Avoids implying more certainty than the underlying model actually has.

---

### 5. ~~Self-employed/informal income haircut — should it scale with range width?~~ RESOLVED
Superseded by RULES.md §7: rather than inferring a haircut from how wide the self-declared range
is (a proxy we'd be guessing at), Tier-2 now asks "what share of your income is variable/seasonal"
directly. The flat 0.70 multiplier in §1 should eventually be replaced by a formula driven by
this answer instead of a single constant. Still needs: the actual formula mapping "variable share"
to haircut size — right now we know the *input* changed, not yet the *function*.

---

### 6. ~~Existing-debt tenure assumption (Anita)~~ RESOLVED
Superseded by RULES.md §7: "existing loan detail" is now a Tier-2 question (shown whenever Tier-1
records ≥1 existing EMI), asking for actual rate/tenure/EMI instead of estimating. The 6-month
assumption used in Anita's walkthrough stands only as a stand-in for what happens when a borrower
skips this Tier-2 question — in that fallback case, the confidence band should widen rather than
silently keeping a fixed 6-month guess. Fallback behavior (widen band vs. keep a point estimate)
still needs to be written into RULES.md explicitly.

---

### 7. Loan tenure — assumed max, or borrower's choice?
All calculations so far assume maximum available tenure (5yr personal, 10yr LAP) to show
best-case affordability.

- Does the app ask the borrower's preferred tenure as a must-question, or always show max-tenure
  as the anchor and let shorter tenures be an optional "what if" toggle on the card?

---

### 8. Rate band — connecting credit score to the actual quoted band
Right now rate bands (e.g. Priya's 10.5-12.5%) are profile-level judgment calls based on general
market research, not a formula that scales continuously with credit score.

- Worth building an explicit score-to-rate adjustment (e.g. every 20 points below 750 shifts the
  band up by X%), or is a small number of discrete tiers (e.g. 750+, 700-749, <700, NTC) enough
  and more defensible than a fake-precise continuous formula?

---

### 9. Not yet built at all
- Full Tier-1 (must) and Tier-2 (additional) question lists, mapped to which output each question moves
- Explicit EMI-ceiling output rule (currently implicit inside the FOIR section of RULES.md)
- Product bands beyond personal loan / LAP: home loan, gold loan, two-wheeler, business loan
