# Borrower Copilot

A self-assessment tool for Indian borrowers: answer questions about your income, existing debt,
and what you want to borrow, and get four things back — a Borrow/Don't Borrow verdict, a max
loan amount (split into what a lender would sanction vs. what's actually safe to carry), a fair
interest rate band, and a safe monthly EMI ceiling — plus a one-page Negotiation Card.

No login. No credit bureau pull. Nothing you enter is stored anywhere. Everything runs from what
you tell the app.

## Run it (under 2 minutes)

```
pip install streamlit
streamlit run app.py
```

This opens the app in your browser automatically (usually at `http://localhost:8501`). To use it
from a phone on the same network, use the "Network URL" Streamlit prints in the terminal.

No backend, no database, no build step. Closing the terminal stops the app.

## Files

- `app.py` — the UI. Contains no calculation logic — only collects answers and displays results.
- `rules.py` — every rule, threshold, and formula the app uses. This is the file to read (or
  edit) to understand or change how a number is calculated.
- `RULES.md` — human-readable documentation of every rule in `rules.py`: what it is, its value,
  why that value, and whether it's a published/verifiable figure or a documented judgement call.

## Changing a rule

Every constant that matters (FOIR caps, the income haircut, LTV assumptions, rate bands, stress
test sizing, etc.) is a named constant near the top of its section in `rules.py`, with a comment
explaining what it does and pointing to the matching row in `RULES.md`. Change the constant, save,
and Streamlit reruns the app automatically — no rebuild step.
