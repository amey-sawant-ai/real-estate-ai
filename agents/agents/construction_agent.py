import os
from utils.groq_client import groq_manager

def analyze_construction_logic(query: str, budget: str, risk: str, context: str = "") -> dict:
    try:
        system_prompt = """You are a Senior Real Estate Construction and Development Specialist.
Your task is to provide a comprehensive development analysis based on the following context. 
You MUST explicitly use the real data provided in the context (such as infrastructure counts, flood risk, and economic indicators).

Please provide your analysis covering exactly these sections:

1. What to Build
   - Best property type for this location and budget (residential, commercial, mixed-use, hospitality)
   - Specific configuration (floors, units, amenities)
   - Why this building type suits this location

2. Construction Cost Estimate
   - Estimated cost per sqft in local currency
   - Total estimated construction cost for the budget
   - Land cost vs construction cost breakdown
   - Contingency budget recommendation (%)

3. Development Timeline
   - Planning and approvals phase (months)
   - Construction phase (months)
   - Total project timeline

4. Expected Returns from Building vs Buying
   - ROI from building and selling
   - ROI from building and renting
   - Compare both to simply buying an existing property
   - Which option gives best return for this budget

5. Key Risks for Developers
   - Construction risks specific to this location
   - Regulatory risks
   - Market absorption risk (can you sell/rent it?)
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
            "agent": "construction_analysis",
            "output": output_content
        }
    except Exception as e:
        return {
            "agent": "construction_analysis",
            "output": f"Error running Construction Agent: {str(e)}"
        }
