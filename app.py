"""
app.py -- Borrower Copilot UI (Streamlit)

This file contains ONLY UI/flow code: collecting answers, calling rules.py, and
rendering results. It does not compute anything itself -- every number on screen
comes from rules.run_assessment(). If a rule needs to change, edit rules.py, not
this file.
"""

import streamlit as st
import rules

st.set_page_config(page_title="Borrower Copilot", page_icon=None, layout="centered")

# -------------------------------------------------------------------------
# Styling -- ledger/passbook design system. See PROJECT_PLAN.md Part 1.2.
# -------------------------------------------------------------------------
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=IBM+Plex+Serif:wght@400;500;600&family=IBM+Plex+Sans:wght@400;500;600&display=swap');

:root {
    --paper: #EEF0E4;
    --ink: #1C2A44;
    --gold: #B98A2E;
    --brick: #9C3B29;
    --forest: #2E5233;
    --line: #C9CBB8;
}

.stApp { background-color: var(--paper); font-family: 'IBM Plex Sans', sans-serif; color: var(--ink); }
h1, h2, h3 { font-family: 'IBM Plex Serif', serif !important; color: var(--ink) !important; }

.ledger-rule { border: none; border-top: 1px solid var(--line); margin: 1.2rem 0; }

.output-row { display: flex; justify-content: space-between; align-items: baseline;
              padding: 0.5rem 0; border-bottom: 1px solid var(--line); }
.output-label { font-family: 'IBM Plex Sans', sans-serif; font-size: 0.95rem; color: var(--ink); }
.output-value { font-family: 'IBM Plex Serif', serif; font-size: 1.15rem; font-weight: 600; text-align: right; }

.verdict-borrow { color: var(--forest); }
.verdict-borrow-less { color: var(--gold); }
.verdict-dont { color: var(--brick); }

.why-line { font-size: 0.88rem; color: #55594d; font-style: italic; margin-top: -0.3rem; margin-bottom: 0.8rem; }

.nego-card { background: #FFFFFF; border: 2px solid var(--ink); border-radius: 4px;
             padding: 1.3rem 1.5rem; position: relative; margin-top: 1rem; }
.nego-card::before { content: "NEGOTIATION CARD"; position: absolute; top: -0.7rem; left: 1rem;
             background: var(--gold); color: #FFF; font-family: 'IBM Plex Sans', sans-serif;
             font-size: 0.7rem; font-weight: 600; letter-spacing: 0.05em; padding: 0.15rem 0.6rem; }
.nego-card p { font-family: 'IBM Plex Serif', serif; font-size: 1.05rem; margin: 0.4rem 0 0 0; }

.flag-note { background: #FBEFE4; border-left: 3px solid var(--gold); padding: 0.6rem 0.8rem;
             font-size: 0.88rem; margin: 0.6rem 0; }
</style>
""", unsafe_allow_html=True)

st.title("Borrower Copilot")
st.caption("Answer what you can. Fewer answers means wider ranges, not wrong ones.")
st.markdown('<hr class="ledger-rule">', unsafe_allow_html=True)

# -------------------------------------------------------------------------
# TIER 1 -- must-answer questions
# -------------------------------------------------------------------------
st.subheader("About the loan")

purpose_options = {
    "Wedding": "wedding", "Medical": "medical", "Education": "education",
    "Business / income-generating": "business", "Vehicle to increase income (e.g. delivery)": "vehicle_for_income",
    "Vehicle (personal use)": "vehicle_personal", "Home improvement": "home_improvement",
    "Debt consolidation": "debt_consolidation", "Other": "other",
}
purpose_label = st.selectbox("What's the loan for?", list(purpose_options.keys()))
purpose = purpose_options[purpose_label]

amount_wanted = st.number_input("How much do you want to borrow (Rs)?", min_value=0, step=10000, value=100000)

loan_type_options = ["Personal loan", "Business loan", "Loan Against Property", "Gold loan",
                      "Vehicle loan", "Home loan", "Not sure"]
loan_type_wanted = st.selectbox("What kind of loan were you thinking of?", loan_type_options)

st.subheader("About your income")

income_type_label = st.radio("How would you describe your income?",
                              ["Salaried", "Self-employed", "Informal / gig work"])
income_type = {"Salaried": "salaried", "Self-employed": "self_employed",
               "Informal / gig work": "informal"}[income_type_label]

net_income = None
income_range_low = income_range_high = None
itr_annual_income = None

if income_type == "salaried":
    net_income = st.number_input("Net (take-home) monthly income (Rs)", min_value=0, step=1000, value=50000)
else:
    st.write("What does your monthly income typically range between?")
    c1, c2 = st.columns(2)
    with c1:
        income_range_low = st.number_input("Low end (Rs)", min_value=0, step=1000, value=20000)
    with c2:
        income_range_high = st.number_input("High end (Rs)", min_value=0, step=1000, value=40000)

    files_itr = st.checkbox("Do you file an ITR (Income Tax Return)?")
    if files_itr:
        itr_annual_income = st.number_input("Declared annual income on your ITR (Rs)", min_value=0, step=10000)

st.subheader("Existing loans")
num_existing = st.number_input("How many existing loans/EMIs do you currently have?", min_value=0, max_value=10, step=1, value=0)
existing_emis = []
add_loan_detail = False
if num_existing > 0:
    add_loan_detail = st.checkbox("Add detail on rate/tenure for more accurate results (recommended)")
    for i in range(int(num_existing)):
        st.markdown(f"**Existing loan {i+1}**")
        c1, c2 = st.columns(2)
        with c1:
            amt = st.number_input(f"Monthly EMI (Rs) — loan {i+1}", min_value=0, step=500, key=f"emi_amt_{i}")
        rate = None
        if add_loan_detail:
            with c2:
                rate = st.number_input(f"Interest rate (% p.a.) — loan {i+1}", min_value=0.0, step=0.5, key=f"emi_rate_{i}")
        existing_emis.append({"amount": amt, "rate_pct": rate})

rent_or_housing_cost = st.number_input("Monthly rent / housing cost (Rs) — enter 0 if none or unsure",
                                        min_value=0, step=500, value=0)

age = st.number_input("Your age", min_value=18, max_value=75, step=1, value=30)

st.subheader("Credit history")
credit_choice = st.radio("Do you know your credit score?",
                          ["Yes, I know it", "No, not sure", "I've never taken formal credit before"])
credit_status = None
credit_score = None
if credit_choice == "Yes, I know it":
    credit_status = "known"
    credit_score = st.number_input("Credit score (CIBIL, 300-900)", min_value=300, max_value=900, step=10, value=700)
elif credit_choice == "No, not sure":
    credit_status = "unknown"
else:
    credit_status = "ntc"

st.markdown('<hr class="ledger-rule">', unsafe_allow_html=True)

# -------------------------------------------------------------------------
# TIER 2 -- adaptive additional questions
# -------------------------------------------------------------------------
st.subheader("A few more questions (optional, but they sharpen your numbers)")

years_in_income = st.number_input(
    "Years at this job / running this business/income source", min_value=0, step=1, value=1)

variable_income_share_pct = None
if income_type in ("self_employed", "informal"):
    variable_income_share_pct = st.slider(
        "What share of your income is irregular or seasonal? (0 = fully stable, 100 = fully unpredictable)",
        0, 100, 50)

card_utilization_pct = None
if credit_status == "known":
    card_utilization_pct = st.slider("Roughly what % of your credit card limits do you typically use?", 0, 100, 30)

bounced_payment_last_3mo = st.checkbox("Have you missed or bounced a payment on any existing loan in the last 3 months?")

emergency_savings_months = st.number_input(
    "How many months of expenses do you have in savings? (enter 0 if none/unsure)", min_value=0, step=1, value=0)

show_collateral = (income_type in ("self_employed", "informal")) or (credit_status == "ntc")
collateral = None
if show_collateral:
    owns_property = st.checkbox("Do you own any property (shop, home, land) free of any existing loan against it?")
    if owns_property:
        prop_type = st.radio("Property type", ["Commercial", "Residential"])
        prop_value = st.number_input("Approximate market value (Rs)", min_value=0, step=100000, value=1000000)
        collateral = {"owned": True, "unencumbered": True,
                      "type": "residential" if prop_type == "Residential" else "commercial",
                      "value": prop_value}

co_applicant_income = st.number_input(
    "Co-applicant's monthly income, if applying jointly (Rs) — enter 0 if not applicable",
    min_value=0, step=1000, value=0)

upcoming_large_expense = st.number_input(
    "Any large expense coming up in the next few months (Rs)? Enter 0 if none.", min_value=0, step=1000, value=0)

loan_earn_estimate_monthly = None
if purpose in rules.PRODUCTIVE_PURPOSES:
    loan_earn_estimate_monthly = st.number_input(
        "If this loan is for income generation, how much extra could it earn you per month (Rs)?",
        min_value=0, step=500, value=0)

offers_received = st.text_input("Have you already been quoted a rate by a lender? (optional, e.g. '14%')")

st.markdown('<hr class="ledger-rule">', unsafe_allow_html=True)

# -------------------------------------------------------------------------
# Run assessment
# -------------------------------------------------------------------------
if st.button("Get my numbers", type="primary"):
    answers = {
        "purpose": purpose,
        "amount_wanted": amount_wanted,
        "loan_type_wanted": loan_type_wanted,
        "income_type": income_type,
        "net_income": net_income,
        "income_range_low": income_range_low,
        "income_range_high": income_range_high,
        "itr_annual_income": itr_annual_income,
        "existing_emis": existing_emis,
        "rent_or_housing_cost": rent_or_housing_cost,
        "age": age,
        "credit_status": credit_status,
        "credit_score": credit_score,
        "years_in_income": years_in_income,
        "variable_income_share_pct": variable_income_share_pct,
        "card_utilization_pct": card_utilization_pct,
        "bounced_payment_last_3mo": bounced_payment_last_3mo,
        "emergency_savings_months": emergency_savings_months if emergency_savings_months > 0 else None,
        "collateral": collateral,
        "co_applicant_income": co_applicant_income,
        "upcoming_large_expense": upcoming_large_expense,
        "loan_earn_estimate_monthly": loan_earn_estimate_monthly if loan_earn_estimate_monthly else None,
        "offers_received": offers_received,
        "tenure_months": 60,
    }

    result = rules.run_assessment(answers)

    st.markdown('<hr class="ledger-rule">', unsafe_allow_html=True)
    st.subheader("Your assessment")

    verdict_map = {
        "borrow": ("BORROW", "verdict-borrow"),
        "borrow_less": ("BORROW LESS", "verdict-borrow-less"),
        "dont_borrow": ("DON'T BORROW", "verdict-dont"),
    }
    label, css_class = verdict_map[result["verdict"]]
    st.markdown(f'<h2 class="{css_class}">{label}</h2>', unsafe_allow_html=True)
    st.markdown(f'<div class="why-line">{result["verdict_reason"]}</div>', unsafe_allow_html=True)

    if result["ceilings"].get("predatory_debt_flag"):
        st.markdown(
            '<div class="flag-note">Note: some of your existing debt is priced at 30%+ interest — '
            'above even India\'s regulated microfinance segment. This has narrowed your safe borrowing room.</div>',
            unsafe_allow_html=True)

    if result["verdict"] == "dont_borrow":
        st.markdown(f"""
        <div class="output-row"><span class="output-label">Amount to borrow now</span><span class="output-value">Rs 0</span></div>
        """, unsafe_allow_html=True)
        st.write(f"**Path back:** {result['path_back']}")
        if result.get("existing_debt_rate_note"):
            st.write(f"**On your existing debt:** {result['existing_debt_rate_note']}")
    else:
        income = result["income"]
        st.markdown(f"""
        <div class="output-row"><span class="output-label">A lender would likely sanction</span><span class="output-value">Rs {result['max_amount_lender']:,.0f}</span></div>
        <div class="output-row"><span class="output-label">You can safely carry</span><span class="output-value">Rs {result['max_amount_safe']:,.0f}</span></div>
        <div class="output-row"><span class="output-label">Recommended amount</span><span class="output-value">Rs {result['recommended_amount']:,.0f}</span></div>
        <div class="output-row"><span class="output-label">Fair rate for your profile</span><span class="output-value">{result['rate_band'][0]:.1f}% - {result['rate_band'][1]:.1f}%</span></div>
        <div class="output-row"><span class="output-label">Recommended product</span><span class="output-value">{result['routed_product']}</span></div>
        <div class="output-row"><span class="output-label">Safe monthly EMI ceiling</span><span class="output-value">Rs {result['emi_ceiling']:,.0f}</span></div>
        """, unsafe_allow_html=True)

        stress = result["stress"]
        holds_text = "holds" if stress["holds"] else "does NOT hold — reconsider the amount"
        st.write(f"**Stress check** (rate +2 pts, income −10%): monthly payment would become "
                 f"Rs {stress['stressed_emi']:,.0f} — this {holds_text}.")

        st.write(f"*Income basis: {income['note']}*")

    st.markdown('<div class="nego-card">', unsafe_allow_html=True)
    st.markdown(f"<p>{result['negotiation_card']['text']}</p>", unsafe_allow_html=True)
    if offers_received:
        st.markdown(f"<p style='font-size:0.85rem; color:#55594d;'>Lender's quote: {offers_received}</p>", unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

    with st.expander("What this doesn't account for yet"):
        st.write("""
        - Years at your job/business and card utilisation are collected but not yet factored
          into the numeric bands above — they inform confidence, not the calculation, today.
        - Co-applicant income and upcoming large expenses are collected but not yet wired into
          the ceiling calculations.
        - Household expenses beyond rent (food, school fees, etc.) are not separately asked —
          if you left rent as 0 because you're unsure, your safe ceiling above may be optimistic.
        """)
