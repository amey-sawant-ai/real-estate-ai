import os
from utils.groq_client import groq_manager

def analyze_strategy_logic(query: str, budget: str, risk: str, context: str = "") -> str:
    
    system_prompt = """You are a Senior Real Estate Investment Strategist.
Your goal is to give the investor a final actionable strategy based on the location and budget.
Please provide the following:
- Exactly what to buy or build (property type, size, configuration)
- Expected returns in 3, 5 and 10 years in actual numbers
- Exit strategy with timing
- Top 3 risks and how to mitigate each one
- One final verdict: Buy, Wait, or Avoid — with a reason
Write out a concise but informative analysis answering these points.

You will be given real data about this location. 
You MUST explicitly reference and cite the actual 
numbers from this data in your analysis. 
For example say 'According to World Bank data, 
GDP growth is 3.99%' or 'Numbeo rates the safety 
index at 83.88 out of 100' or 'With annual rainfall 
of 2438mm the flood risk is rated High'.
Never ignore the real data provided to you.
Always quote specific numbers from the data."""

    user_prompt = f"Query: {query}\nBudget: {budget}\nRisk Profile: {risk}"
    if context:
        user_prompt += f"\n\nContext from previous analysis:\n{context}"

    return groq_manager.safe_call(
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ],
        model="llama-3.3-70b-versatile"
    )
