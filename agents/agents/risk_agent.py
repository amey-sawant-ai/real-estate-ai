import json
import os
from utils.groq_client import groq_manager

def analyze_risk_logic(query: str, budget: str, risk: str, context: str = "") -> dict:
    try:
        system_prompt = """You are a Real Estate Risk Scoring Specialist.
Your task is to produce a single investment score from 0-100 with a breakdown across exactly these 6 dimensions:

1. Market Score (0-100)
   Based on: GDP growth, inflation, property demand, price trends
2. Safety Score (0-100)
   Based on: Numbeo safety index, crime, political stability
3. Climate Score (0-100)
   Based on: flood risk, heat risk, natural disaster exposure
4. Infrastructure Score (0-100)
   Based on: metro stations, hospitals, schools, banks nearby
5. Legal Score (0-100)
   Based on: foreign ownership rules, tax burden, ease of repatriation
6. Economic Score (0-100)
   Based on: GDP per capita, unemployment, urban growth, purchasing power

Then calculate a final OVERALL SCORE as weighted average:
- Market: 25%
- Safety: 20%
- Climate: 15%
- Infrastructure: 15%
- Legal: 15%
- Economic: 10%

Return the output in this exact format:
{
  "overall_score": 0,
  "rating": "Excellent/Good/Moderate/Risky/Avoid",
  "scores": {
    "market": 0,
    "safety": 0,
    "climate": 0,
    "infrastructure": 0,
    "legal": 0,
    "economic": 0
  },
  "summary": "2 sentence explanation of the score"
}

The agent must return ONLY this JSON, no extra text.
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
            "overall_score": 0,
            "rating": "Error",
            "scores": {
                "market": 0,
                "safety": 0,
                "climate": 0,
                "infrastructure": 0,
                "legal": 0,
                "economic": 0
            },
            "summary": f"Error running Risk Scoring Agent: {str(e)}"
        }
