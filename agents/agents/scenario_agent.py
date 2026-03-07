import json
from utils.groq_client import groq_manager

def analyze_scenario_logic(query: str, budget: str, risk: str, context: str = None) -> dict:
    """
    Acts as a Real Estate Scenario Planning and Stress Testing Specialist.
    Produces exactly 3 scenarios using cash flow data from context:
    Bear, Base, Bull, and Sensitivity analysis.
    """
    
    system_prompt = """
    You are a Real Estate Scenario Planning and Stress Testing Specialist.
    Your job is to produce exactly 3 scenarios using the cash flow data and other relevant data provided in the context.
    
    You must output exactly and ONLY a valid JSON object. Do not provide any markdown formatting outside the JSON, and no code blocks.

    Produce the following 3 scenarios:
    
    BEAR SCENARIO (worst case - 20% probability)
    - Triggers: interest rate spike +3%, vacancy jumps to 30%, property values drop 15%, rent drops 10%
    - Recalculate: monthly cash flow, IRR, break-even
    - Time to recovery if market crashes
    - Key trigger events that would cause this scenario
    - Early warning signs to watch for
    - Recommended action if this scenario unfolds
    
    BASE SCENARIO (most likely - 60% probability)
    - Uses the assumptions already in the provided context
    - Confirms the base case numbers
    - Expected outcome at end of holding period
    - Key trigger events that would cause this scenario
    - Early warning signs to watch for
    - Recommended action if this scenario unfolds
    
    BULL SCENARIO (best case - 20% probability)
    - Triggers: GDP growth accelerates to 8%+, vacancy drops to 5%, property values rise 25% in 3 years, rent increases 15%
    - Recalculate: monthly cash flow, IRR, break-even
    - Upside potential
    - Key trigger events that would cause this scenario
    - Early warning signs to watch for
    - Recommended action if this scenario unfolds

    Then produce a SENSITIVITY ANALYSIS showing which single factor has the most impact on returns:
    - What happens if only interest rate changes by 1%?
    - What happens if only vacancy changes by 10%?
    - What happens if only rent changes by 10%?
    - What happens if only property value changes by 10%?

    Use response_format={"type": "json_object"} and return exactly this JSON structure:
    {
      "bear": { "probability": "20%", "irr": "", 
                "monthly_cashflow": 0, "triggers": [], 
                "warnings": [], "action": "" },
      "base": { "probability": "60%", "irr": "", 
                "monthly_cashflow": 0, "verdict": "" },
      "bull": { "probability": "20%", "irr": "", 
                "monthly_cashflow": 0, "triggers": [], 
                "upside": "" },
      "sensitivity": {
        "interest_rate_1pct_change": "",
        "vacancy_10pct_change": "",
        "rent_10pct_change": "",
        "property_value_10pct_change": "",
        "biggest_risk_factor": ""
      },
      "summary": ""
    }
    """
    
    user_prompt = f"""
    Query: {query}
    Budget: {budget}
    Risk: {risk}
    
    Context Cash Flow Data:
    {context}
    """

    try:
        response = groq_manager.safe_call(
            model="llama-3.3-70b-versatile",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            response_format={"type": "json_object"}
        )
        return json.loads(response)
    except Exception as e:
        return {"error": f"Failed to generate scenarios: {str(e)}"}
