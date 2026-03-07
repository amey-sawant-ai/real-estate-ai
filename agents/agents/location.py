import os
from utils.groq_client import groq_manager

def analyze_location_logic(query: str, budget: str, risk: str, context: str = "") -> str:
    
    system_prompt = """You are a Location Intelligence Specialist for real estate investment.
Your goal is to perform historical and locational analysis based on the user's query.
Please do the following:
1. Extract the exact location from the user query.
2. Research that location's history over the last 10-20 years.
3. Identify what infrastructure or economic events transformed it.
4. Identify key turning points that affected property values.
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
