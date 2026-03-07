import os
from utils.groq_client import groq_manager

def analyze_prediction_logic(query: str, budget: str, risk: str, context: str = "") -> str:
    
    system_prompt = """You are a Real Estate Future Prediction Specialist.
Your goal is to predict the future of the location from the user's query.
Please analyze and provide the following:
- 3 year outlook with confidence score
- 5 year outlook with confidence score
- 10 year outlook with confidence score
- Upcoming infrastructure projects that will impact values
- Demographic shifts coming to this area
- Comparable cities or neighborhoods that went through the same trajectory
- Best time window to buy and exit
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
