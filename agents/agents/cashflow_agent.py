import json
import os
from utils.groq_client import groq_manager

def analyze_cashflow_logic(query: str, budget: str, risk: str, context: str = "") -> dict:
    try:
        system_prompt = """You are a Senior Real Estate Cash Flow and Financial Modelling Analyst.
Your task is to produce a pro-forma style financial analysis based on the user's budget and location, utilizing the real data provided in the context.

You must explicitly use the real data from the context:
- Use forex rates to convert the budget to local currency
- Use GDP growth as a proxy for the rental growth rate
- Use inflation rate to adjust future cash flows
- Use Numbeo cost of living and property price indicators to calibrate your rent and price estimates

Provide your analysis covering these exact sections:

1. ASSUMPTIONS
   - Estimated property price (derived from budget and context)
   - Estimated rent per month (derived from Numbeo/market data in context)
   - Occupancy rate (%)
   - Holding period (years, based on risk profile)
   - Estimated interest rate for mortgage (%)
   - Capex reserve per year (%)
   - Property tax rate (%)
   - Management fee (%)

2. MONTHLY CASH FLOW PROJECTION
   - Gross monthly rental income
   - Minus: vacancy loss
   - Minus: property management fee
   - Minus: maintenance/capex reserve
   - Minus: property tax (monthly)
   - Minus: mortgage payment (if leveraged at 70% LTV)
   - = Net monthly cash flow

3. ANNUAL RETURNS
   - Year 1, Year 3, Year 5, Year 10 cash flow
   - Cumulative cash flow over holding period

4. IRR CALCULATION
   - Calculate Internal Rate of Return over holding period
   - Show the formula inputs used

5. EQUITY MULTIPLE
   - Total returns / initial investment
   - What this means in plain English

6. BREAK-EVEN ANALYSIS
   - How many months until investment breaks even
   - Break-even year

7. VERDICT
   - Is this a cash-flow positive or negative investment?
   - What yield does this represent?
   - One sentence recommendation

You must return EXACTLY and ONLY a JSON object in the following format:
{
  "assumptions": {},
  "monthly_cashflow": {},
  "annual_returns": {},
  "irr": "calculated IRR and formula inputs used",
  "equity_multiple": "total returns / initial investment and meaning in plain English",
  "breakeven_months": 0,
  "verdict": "is this cash-flow positive or negative? yield? one sentence recommendation"
}
"""

        user_content = f"Query: {query}\nBudget: {budget}\nRisk Profile: {risk}\n\nContext Data:\n{context}"
        
        output_content = groq_manager.safe_call(
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_content}
            ],
            model="llama-3.3-70b-versatile",
            temperature=0.3,
            response_format={"type": "json_object"}
        )
        
        return json.loads(output_content)
    except Exception as e:
        return {
            "error": f"Error running Cash Flow Agent: {str(e)}"
        }
