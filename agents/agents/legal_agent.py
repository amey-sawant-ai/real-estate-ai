import os
from utils.groq_client import groq_manager

def analyze_legal_logic(query: str, budget: str, risk: str, context: str = "") -> dict:
    try:
        
        system_prompt = """You are an International Real Estate Legal and Tax Specialist.
Your role is to:
1. Explain foreign ownership rules for this country (can foreigners buy property freely, restricted, or banned?)
2. List all taxes involved: stamp duty, registration, capital gains tax, rental income tax, inheritance tax
3. Explain any visa or residency benefits from buying property (golden visa, investor visa etc)
4. Explain rules for repatriating rental income and sale proceeds back to home country
5. Flag any legal risks specific to this location
6. Give a Legal Friendliness Score: Friendly, Moderate or Restrictive for foreign investors

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
            "agent": "legal_analysis",
            "output": output_content
        }
    except Exception as e:
        return {
            "agent": "legal_analysis",
            "output": f"Error running Legal Analysis Agent: {str(e)}"
        }
