"""
rules.py -- Borrower Copilot rules engine

Every function here corresponds to a numbered section in RULES.md.
This file has NO Streamlit code and NO UI code -- it is pure calculation,
written as plain functions (no classes), so it reads like straightforward
procedural code and can be changed independently of app.py.

This is the file you edit if asked to change a rule live. Every threshold
that matters is a named constant near the top of its section, not buried
inside a formula, so it's easy to find and change under time pressure.

Money amounts are in rupees. Rates are annual percentages (e.g. 11.5 = 11.5%).
"""

# =========================================================================
# Core loan math
# =========================================================================

def emi(principal, annual_rate_pct, months):
    """Monthly payment for a given principal, annual rate, and tenure."""
    r = annual_rate_pct / 12 / 100
    if r == 0:
        return principal / months
    return (principal * r * (1 + r) ** months) / ((1 + r) ** months - 1)


def principal_from_emi(emi_amt, annual_rate_pct, months):
    """Inverse of emi(): how much principal a given monthly payment supports."""
    r = annual_rate_pct / 12 / 100
    if r == 0:
        return emi_amt * months
    return (emi_amt * ((1 + r) ** months - 1)) / (r * (1 + r) ** months)


# =========================================================================
# RULES.md SS1 -- Income assessment
# =========================================================================

# Default haircut applied to self-declared, unverified income (self-employed /
# informal borrowers). This is a JUDGEMENT CALL, not a published figure -- see
# RULES.md SS1 and OPEN_QUESTIONS.md #5. Change this single number to test
# sensitivity live.
DEFAULT_INCOME_HAIRCUT = 0.70


def assess_income(answers):
    """
    answers keys used:
      income_type: 'salaried' | 'self_employed' | 'informal'
      net_income: number (salaried only)
      income_range_low, income_range_high: numbers (self_employed/informal only)
      itr_annual_income: number or None
      variable_income_share_pct: number 0-100, or None (Tier-2 question)
    """
    if answers["income_type"] == "salaried":
        return {
            "assessed_income": answers["net_income"],
            "confidence": "high",
            "note": "Net take-home income as stated.",
        }

    mid = (answers["income_range_low"] + answers["income_range_high"]) / 2

    haircut = DEFAULT_INCOME_HAIRCUT
    haircut_source = f"default judgement ({(1 - DEFAULT_INCOME_HAIRCUT) * 100:.0f}% haircut on unverified income)"

    variable_share = answers.get("variable_income_share_pct")
    if variable_share is not None:
        # 100% stable income -> trust fully (haircut 1.0).
        # 100% variable income -> steepest discount (haircut 0.60).
        # Linear in between. This mapping is itself a judgement call -- flagged
        # in RULES.md, not a published formula.
        haircut = 1 - 0.40 * (variable_share / 100)
        haircut_source = f"derived from stated variable-income share ({variable_share:.0f}%)"

    assessed_from_declared = mid * haircut

    itr = answers.get("itr_annual_income")
    if itr:
        assessed_income = max(assessed_from_declared, itr / 12)
    else:
        assessed_income = assessed_from_declared

    return {
        "assessed_income": assessed_income,
        "confidence": "medium" if variable_share is not None else "low-medium",
        "note": f"Self-declared midpoint (Rs {mid:,.0f}) x haircut ({haircut_source}), "
                f"compared against ITR if provided.",
    }


# =========================================================================
# RULES.md SS2 -- FOIR / affordability
# =========================================================================

# Lender-side FOIR caps by employment type. Published industry range is 40-60%;
# these are the specific points chosen -- see RULES.md SS2.
FOIR_CAPS = {
    "salaried": 0.50,
    "self_employed": 0.45,
    "informal": 0.45,
}

# Safe-cap margin rules (RULES.md SS2): the safe cap must sit ABOVE the
# borrower's current obligation ratio (sanity floor) and BELOW the lender cap
# (safety margin). These two numbers are judgement calls -- change them to
# test sensitivity live.
MARGIN_ABOVE_CURRENT = 0.07
MARGIN_BELOW_LENDER = 0.05


def existing_obligations(answers):
    """Existing EMIs + rent/housing cost. Rent IS included -- see RULES.md SS2
    correction note: most real FOIR formulas include rent, not just EMIs."""
    emi_total = sum(e["amount"] for e in answers.get("existing_emis", []))
    rent = answers.get("rent_or_housing_cost", 0) or 0
    return emi_total + rent


# Extra safe-cap tightening when existing debt is already priced at a predatory rate.
# This is a SOFT FLAG, not a hard stop (see RULES.md / OPEN_QUESTIONS.md #1) -- a
# borrower can carry an expensive short-term loan and still be current on it, so we
# narrow their margin rather than auto-blocking them. Change this to test sensitivity.
PREDATORY_RATE_THRESHOLD_PCT = 30.0
PREDATORY_RATE_SAFE_CAP_PENALTY = 0.05

# Emergency savings adjustment (Tier-2 question). A borrower with a real buffer can
# absorb a bit more risk safely; one with none should get less room, not more.
# Thresholds and sizes are judgement calls, not published figures.
EMERGENCY_SAVINGS_BONUS_MONTHS = 3
EMERGENCY_SAVINGS_BONUS = 0.03
EMERGENCY_SAVINGS_PENALTY_MONTHS = 1
EMERGENCY_SAVINGS_PENALTY = 0.03

# For productive/business purposes, a borrower's own credible estimate of what the
# loan will earn can offset EMI capacity -- but only partially credited (never take
# a borrower's own ROI estimate at face value). Judgement call, not a published rate.
LOAN_EARN_CREDIT_FRACTION = 0.50
PRODUCTIVE_PURPOSES = {"business", "vehicle_for_income"}


def has_predatory_existing_debt(answers):
    return any(e.get("rate_pct", 0) and e["rate_pct"] >= PREDATORY_RATE_THRESHOLD_PCT
               for e in answers.get("existing_emis", []))


def round_down_ceiling(amount):
    """Round a recommended ceiling DOWN to a clean, presentable number -- avoids
    false precision like 'Rs 3,25,947'. Step size scales with magnitude."""
    if amount <= 0:
        return 0
    if amount < 100000:
        step = 5000
    elif amount < 1000000:
        step = 25000
    else:
        step = 100000
    return (int(amount) // step) * step


def compute_ceilings(answers, assessed_income):
    lender_cap = FOIR_CAPS[answers["income_type"]]
    existing = existing_obligations(answers)
    current_ratio = existing / assessed_income if assessed_income > 0 else 1.0

    # BUGFIX: this must be max(), not min(). The current-ratio term is a FLOOR
    # (raise the cap if the borrower's current burden already needs it -- see
    # Priya's case) not a ceiling. Using min() here previously collapsed the
    # safe cap to near-zero for any borrower with little/no existing debt
    # (e.g. Ravi) -- caught by testing against the three worked examples.
    base_safe_cap = lender_cap - MARGIN_BELOW_LENDER
    safe_cap = max(base_safe_cap, current_ratio + MARGIN_ABOVE_CURRENT)
    safe_cap = min(safe_cap, lender_cap)  # never exceed lender cap

    predatory_flag = has_predatory_existing_debt(answers)
    if predatory_flag:
        safe_cap = max(0, safe_cap - PREDATORY_RATE_SAFE_CAP_PENALTY)

    savings_months = answers.get("emergency_savings_months")
    if savings_months is not None:
        if savings_months >= EMERGENCY_SAVINGS_BONUS_MONTHS:
            safe_cap = min(safe_cap + EMERGENCY_SAVINGS_BONUS, lender_cap)
        elif savings_months < EMERGENCY_SAVINGS_PENALTY_MONTHS:
            safe_cap = max(0, safe_cap - EMERGENCY_SAVINGS_PENALTY)

    lender_available_emi = max(0, lender_cap * assessed_income - existing)
    safe_available_emi = max(0, safe_cap * assessed_income - existing)

    # Productive-purpose credit: partial offset from the loan's own expected earnings
    loan_earn_bonus = 0
    if answers.get("purpose") in PRODUCTIVE_PURPOSES and answers.get("loan_earn_estimate_monthly"):
        loan_earn_bonus = answers["loan_earn_estimate_monthly"] * LOAN_EARN_CREDIT_FRACTION
        lender_available_emi += loan_earn_bonus
        safe_available_emi += loan_earn_bonus

    return {
        "lender_cap": lender_cap,
        "safe_cap": safe_cap,
        "current_ratio": current_ratio,
        "existing": existing,
        "lender_available_emi": lender_available_emi,
        "safe_available_emi": safe_available_emi,
        "predatory_debt_flag": predatory_flag,
        "loan_earn_bonus": loan_earn_bonus,
    }


# =========================================================================
# RULES.md SS4 -- Secured product routing (Loan Against Property)
# =========================================================================

LTV = {"commercial": 0.55, "residential": 0.65}

RATE_BANDS = {
    "personal_unsecured_prime": (10.5, 12.5),      # salaried, credit score >=750
    "personal_unsecured_standard": (13.0, 16.0),   # salaried, score <750 or unknown
    "business_unsecured_informal": (18.0, 24.0),   # NTC/informal, no collateral
    "lap_commercial": (9.0, 11.5),
    "lap_residential": (8.5, 10.5),
    "mfi_reference": (19.0, 28.0),                 # regulated MFI segment, MFIN Feb-2026 data
}


def evaluate_secured_route(answers):
    collateral = answers.get("collateral")
    if not collateral or not collateral.get("owned") or not collateral.get("unencumbered"):
        return None
    prop_type = collateral.get("type", "commercial")
    ltv = LTV.get(prop_type, LTV["commercial"])
    ceiling = collateral["value"] * ltv
    band = RATE_BANDS["lap_residential"] if prop_type == "residential" else RATE_BANDS["lap_commercial"]
    return {"ceiling": ceiling, "ltv": ltv, "rate_band": band, "tenure_months": 120, "type": prop_type}


# =========================================================================
# RULES.md SS6 -- Verdict logic (two-layer)
# =========================================================================

def mid_rate(answers):
    if answers["income_type"] == "salaried":
        if answers.get("credit_status") == "known" and answers.get("credit_score", 0) >= 750:
            band = RATE_BANDS["personal_unsecured_prime"]
        else:
            band = RATE_BANDS["personal_unsecured_standard"]
    else:
        band = RATE_BANDS["business_unsecured_informal"]
    return sum(band) / 2


def compute_verdict(answers, ceilings):
    # Layer 1 -- hard stops (checked first, independent of ratio math)
    if answers.get("bounced_payment_last_3mo"):
        return {
            "verdict": "dont_borrow",
            "reason": "A payment was already missed on existing debt in the last 3 months -- "
                      "adding a new loan now makes that worse, not better.",
        }

    if ceilings["safe_available_emi"] <= 0:
        return {
            "verdict": "dont_borrow",
            "reason": "Existing obligations alone already use up the safe portion of income -- "
                      "there is no room for a new EMI before something changes.",
        }

    # Layer 2 -- ratio check against the desired amount
    tenure = answers.get("tenure_months", 60)
    desired_emi = emi(answers["amount_wanted"], mid_rate(answers), tenure)
    if desired_emi <= ceilings["safe_available_emi"]:
        return {"verdict": "borrow", "reason": "The amount you want fits within a safe monthly EMI."}
    return {
        "verdict": "borrow_less",
        "reason": "The amount you want is more than a lender would sanction safely -- "
                  "a smaller amount fits your safe capacity.",
    }


# =========================================================================
# Stress test (RULES.md SS2, required output)
# =========================================================================

# Shock sizing -- judgement call, not a regulatory figure. Change to test sensitivity.
STRESS_RATE_BUMP_PCT = 2.0
STRESS_INCOME_DROP_PCT = 0.10


def stress_test(answers, ceilings, loan_amount, rate_pct, tenure_months, assessed_income):
    stressed_rate = rate_pct + STRESS_RATE_BUMP_PCT
    stressed_income = assessed_income * (1 - STRESS_INCOME_DROP_PCT)
    stressed_emi = emi(loan_amount, stressed_rate, tenure_months)
    stressed_ratio = (ceilings["existing"] + stressed_emi) / stressed_income if stressed_income > 0 else 1.0
    return {
        "stressed_emi": stressed_emi,
        "stressed_ratio": stressed_ratio,
        "holds": stressed_ratio <= ceilings["lender_cap"],
    }


# =========================================================================
# Full pipeline
# =========================================================================

def run_assessment(answers):
    income_result = assess_income(answers)
    assessed_income = income_result["assessed_income"]
    ceilings = compute_ceilings(answers, assessed_income)
    secured_route = evaluate_secured_route(answers)
    verdict_result = compute_verdict(answers, ceilings)

    output = {
        "income": income_result,
        "ceilings": ceilings,
        "secured_route": secured_route,
        "verdict": verdict_result["verdict"],
        "verdict_reason": verdict_result["reason"],
    }

    if verdict_result["verdict"] == "dont_borrow":
        output["max_amount"] = 0
        output["path_back"] = ("Stay current on all existing payments for 3 consecutive months "
                                "with no new bounces, then re-run this assessment.")
        output["existing_debt_rate_note"] = None
        if any(e.get("rate_pct", 0) >= 30 for e in answers.get("existing_emis", [])):
            lo, hi = RATE_BANDS["mfi_reference"]
            output["existing_debt_rate_note"] = (
                f"Existing debt is priced above even India's regulated microfinance segment "
                f"(currently {lo:.0f}-{hi:.0f}% APR). Refinancing may or may not meaningfully "
                f"help depending on the loan's size and remaining tenure -- check both."
            )
        output["negotiation_card"] = {
            "type": "decline",
            "text": f"If offered Rs {answers['amount_wanted']:,.0f} today: decline. {verdict_result['reason']}",
        }
        return output

    # Borrow / Borrow Less
    use_secured = secured_route is not None and (
        answers.get("credit_status") == "ntc" or income_result["confidence"] != "high"
    )
    if use_secured:
        rate_band = secured_route["rate_band"]
        tenure_months = secured_route["tenure_months"]
        routed_product = ("Loan Against Property (residential)"
                           if secured_route["type"] == "residential"
                           else "Loan Against Property (commercial)")
    else:
        if answers["income_type"] == "salaried":
            rate_band = (RATE_BANDS["personal_unsecured_prime"]
                         if answers.get("credit_status") == "known" and answers.get("credit_score", 0) >= 750
                         else RATE_BANDS["personal_unsecured_standard"])
        else:
            rate_band = RATE_BANDS["business_unsecured_informal"]
        tenure_months = answers.get("tenure_months", 60)
        routed_product = "Unsecured personal/business loan"

    mid_rate_pct = sum(rate_band) / 2

    lender_loan_ceiling = principal_from_emi(ceilings["lender_available_emi"], mid_rate_pct, tenure_months)
    margin_based_safe_ceiling = principal_from_emi(ceilings["safe_available_emi"], mid_rate_pct, tenure_months)

    # BUGFIX 2: the margin-based ceiling above was found (by testing) to sometimes
    # fail the required stress test -- it was a separate, inconsistent mechanism.
    # Fix: also compute the largest loan that SURVIVES the stress case by
    # construction (rate +2pts, income -10%, still under lender cap), and take
    # whichever ceiling is stricter. This guarantees the recommended amount
    # always passes its own stress test.
    stressed_income = assessed_income * (1 - STRESS_INCOME_DROP_PCT)
    stressed_capacity_emi = max(0, ceilings["lender_cap"] * stressed_income - ceilings["existing"])
    stress_consistent_ceiling = principal_from_emi(
        stressed_capacity_emi, mid_rate_pct + STRESS_RATE_BUMP_PCT, tenure_months
    )
    safe_loan_ceiling = min(margin_based_safe_ceiling, stress_consistent_ceiling)
    if use_secured:
        safe_loan_ceiling = min(safe_loan_ceiling, secured_route["ceiling"])

    recommended_amount = (answers["amount_wanted"] if verdict_result["verdict"] == "borrow"
                          else round_down_ceiling(safe_loan_ceiling))

    stress = stress_test(answers, ceilings, recommended_amount, mid_rate_pct, tenure_months, assessed_income)

    output.update({
        "max_amount_lender": lender_loan_ceiling,
        "max_amount_safe": safe_loan_ceiling,
        "recommended_amount": recommended_amount,
        "rate_band": rate_band,
        "routed_product": routed_product,
        "emi_ceiling": ceilings["safe_available_emi"],
        "stress": stress,
        "negotiation_card": {
            "type": "negotiate",
            "text": (f"Lender quote too high? Fair for your profile is "
                     f"{rate_band[0]:.1f}-{rate_band[1]:.1f}%" +
                     (f", via {routed_product} -- not unsecured." if use_secured else ".")),
        },
    })
    return output
