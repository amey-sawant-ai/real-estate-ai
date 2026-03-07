import os
from utils.groq_client import groq_manager

def analyze_news_logic(query: str, budget: float, risk: str, context: str = "") -> dict:
    try:
        
        system_prompt = """You are a Real Estate News Analyst.
Your role is to:
1. Analyse the news headlines provided in the context.
2. Extract investment signals from each headline.
3. Identify if the news is positive, negative or neutral for real estate investment in this location.
4. Highlight any government policy changes, infrastructure announcements or market shifts.
5. Give an overall news sentiment score: Bullish, Neutral or Bearish.
6. Flag any urgent risks or opportunities found in the news.

You will be given real data about this location. You MUST explicitly reference and cite the actual numbers from this data in your analysis. For example say 'According to World Bank data, GDP growth is 3.99%' or 'Numbeo rates the safety index at 83.88 out of 100' or 'With annual rainfall of 2438mm the flood risk is rated High'. Never ignore the real data provided to you. Always quote specific numbers from the data.
"""

        user_content = f"Query: {query}\nBudget: {budget}\nRisk Profile: {risk}\n\nContext Data:\n{context}"
        
        output_content = groq_manager.safe_call(
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_content}
            ],
            model="llama-3.3-70b-versatile",
            temperature=0.3
        )
        
        return {
            "agent": "news_analysis",
            "output": output_content
        }
    except Exception as e:
        return {
            "agent": "news_analysis",
            "output": f"Error running News Analysis Agent: {str(e)}"
        }
