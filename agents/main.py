from fastapi import FastAPI
import uvicorn
import os
from dotenv import load_dotenv
from groq import Groq
from pydantic import BaseModel

load_dotenv()

class LocationQuery(BaseModel):
    query: str
    budget: str
    risk: str

class DataFetchQuery(BaseModel):
    query: str
    location: str
    country: str

app = FastAPI(
    title="Real Estate Agents API",
    description="AI agents service for the real estate platform",
    version="1.0.0",
)

@app.get("/")
def root():
    return {"message": "Welcome to the Real Estate Agents API", "docs": "/docs"}

@app.get("/ping")
def ping():
    return {"status": "agents are alive"}

from utils.groq_client import groq_manager

@app.get("/groq-ping")
def groq_ping():
    try:
        response = groq_manager.safe_call(
            messages=[{"role": "user", "content": "Just say 'Groq is connected!' and nothing else."}]
        )
        return {"status": "success", "response": response}
    except Exception as e:
        return {"status": "error", "message": str(e)}

@app.get("/utils/keys")
def get_utils_keys():
    groq_count = len([k for k in groq_manager.keys if k.get('provider') == 'groq'])
    cerebras_count = len([k for k in groq_manager.keys if k.get('provider') == 'cerebras'])
    
    current_key = groq_manager.keys[groq_manager.current_index] if groq_manager.keys else {}
    return {
        "groq_keys": groq_count,
        "cerebras_keys": cerebras_count,
        "total_keys": len(groq_manager.keys),
        "current_provider": current_key.get('provider', 'none'),
        "current_index": current_key.get('index', 0)
    }

from agents.location import analyze_location_logic
from agents.market import analyze_market_logic
from agents.prediction import analyze_prediction_logic
from agents.strategy import analyze_strategy_logic
from agents.news_agent import analyze_news_logic
from agents.legal_agent import analyze_legal_logic
from agents.risk_agent import analyze_risk_logic
from agents.construction_agent import analyze_construction_logic
from agents.cashflow_agent import analyze_cashflow_logic
from agents.scenario_agent import analyze_scenario_logic

@app.post("/analyze/location")
def analyze_location(payload: LocationQuery):
    output = analyze_location_logic(payload.query, payload.budget, payload.risk)
    return {
        "agent": "location_intelligence",
        "output": output
    }

@app.post("/analyze/market")
def analyze_market(payload: LocationQuery):
    output = analyze_market_logic(payload.query, payload.budget, payload.risk)
    return {
        "agent": "market_analysis",
        "output": output
    }

@app.post("/analyze/prediction")
def analyze_prediction(payload: LocationQuery):
    output = analyze_prediction_logic(payload.query, payload.budget, payload.risk)
    return {
        "agent": "future_prediction",
        "output": output
    }

@app.post("/analyze/strategy")
def analyze_strategy(payload: LocationQuery):
    output = analyze_strategy_logic(payload.query, payload.budget, payload.risk)
    return {
        "agent": "investment_strategy",
        "output": output
    }

import json
import time

def summarize_output(text: str) -> str:
    if not text or len(text) < 50:
        return text
    try:
        prompt = "Summarize the following real estate agent analysis in maximum 80 words. Keep only the most important facts, numbers, and conclusions:\n\n" + text
        return groq_manager.safe_call(
            messages=[{"role": "user", "content": prompt}],
            use_small_model=True,
            temperature=0.3
        )
    except Exception:
        return text[:500] + "...(summary failed)"

@app.post("/analyze")
def analyze_sequence(payload: LocationQuery):
    q, b, r = payload.query, payload.budget, payload.risk
    
    n_keys = len(groq_manager.keys)
    print(f"Starting pipeline with {n_keys} API keys available")
    
    # Pre-Step: Extract Location & Country via Groq
    extract_prompt = f"""
    You are an expert location extractor.
    Extract the specific location name and the country name from this query: "{q}"
    If the country is not explicitly mentioned, infer it based on the location.
    Return ONLY a valid JSON object in this exact format, nothing else:
    {{ "location": "City/Region name", "country": "Country name" }}
    """
    
    try:
        response = groq_manager.safe_call(
            model="llama-3.3-70b-versatile",
            messages=[{"role": "user", "content": extract_prompt}],
            response_format={"type": "json_object"}
        )
        extracted = json.loads(response)
        loc_name = extracted.get("location", q)
        country_name = extracted.get("country", "")
    except Exception:
        loc_name = q
        country_name = ""

    # Fetch Real Data
    from data.fetcher import fetch_all_data
    raw_data = fetch_all_data(q, loc_name, country_name)
    
    # Parse metrics safely
    real_data_context = "CRITICAL REAL DATA FOR THIS LOCATION:"
    
    # World Bank
    wb = raw_data.get("worldbank", {})
    if isinstance(wb, dict) and "error" not in wb:
        wb_metrics = wb.get("metrics", {})
        gdp = wb_metrics.get("gdp_growth", {}).get("value", "N/A")
        inflation = wb_metrics.get("inflation_rate", {}).get("value", "N/A")
        unemployment = wb_metrics.get("unemployment_rate", {}).get("value", "N/A")
        
        real_data_context += f"""
- GDP: {gdp}%
- Inf: {inflation}%
- Unemp: {unemployment}%"""

    # Numbeo
    numbeo = raw_data.get("numbeo", {})
    if isinstance(numbeo, dict) and "error" not in numbeo:
        ql = numbeo.get("quality_of_life_index", "N/A")
        safety = numbeo.get("safety_index", "N/A")
        real_data_context += f"""
- QL/Safety: {ql}/{safety}"""

    # Climate
    climate = raw_data.get("climate", {})
    if isinstance(climate, dict) and "error" not in climate:
        flood = climate.get("flood_risk", "N/A")
        real_data_context += f"""
- Flood: {flood}"""

    # Forex
    forex = raw_data.get("forex", {})
    if isinstance(forex, dict) and "error" not in forex:
        f_summary = forex.get("summary", "N/A")
        real_data_context += f"""
- Forex: {f_summary}"""

    # News
    news = raw_data.get("news", {})
    if isinstance(news, dict) and "error" not in news:
        articles = news.get("articles", [])
        if articles:
            art = articles[0]
            real_data_context += f"\n- News: {art.get('title')}"

    # Country Legal/Info Data
    country_data = raw_data.get("country_data", {})
    if isinstance(country_data, dict) and "error" not in country_data:
        full_name = country_data.get("full_name", "N/A")
        real_data_context += f"""
- Country: {full_name}"""

    # Step 1: Location Intelligence
    location_output = analyze_location_logic(q, b, r, context=real_data_context)
    loc_summary = summarize_output(location_output)
    time.sleep(5)
    
    # Step 2: Market Analysis (pass Step 1 summary + real data context)
    market_context = f"{real_data_context}\n\n--- Location Intelligence Summary ---\n{loc_summary}"
    market_output = analyze_market_logic(q, b, r, context=market_context)
    market_summary = summarize_output(market_output)
    time.sleep(5)
    
    # Step 3: Future Prediction (pass prior summaries + real data context)
    prediction_context = f"{market_context}\n\n--- Market Analysis Summary ---\n{market_summary}"
    prediction_output = analyze_prediction_logic(q, b, r, context=prediction_context)
    pred_summary = summarize_output(prediction_output)
    time.sleep(5)
    
    # Step 4: Investment Strategy
    strategy_context = f"{prediction_context}\n\n--- Future Prediction Summary ---\n{pred_summary}"
    strategy_output = analyze_strategy_logic(q, b, r, context=strategy_context)
    strat_summary = summarize_output(strategy_output)
    time.sleep(5)
    
    # Step 5: News Analysis
    news_context = f"{strategy_context}\n\n--- Investment Strategy Summary ---\n{strat_summary}"
    news_output = analyze_news_logic(q, b, r, context=news_context)
    
    # Extract string for summarization if output is dict format
    news_output_str = news_output.get("output", str(news_output)) if isinstance(news_output, dict) else str(news_output)
    news_summary = summarize_output(news_output_str)
    time.sleep(5)
    
    # Step 6: Legal Analysis
    legal_context = f"{news_context}\n\n--- News Analysis Summary ---\n{news_summary}"
    legal_output = analyze_legal_logic(q, b, r, context=legal_context)
    
    # Extract string for summarization if output is dict format
    legal_output_str = legal_output.get("output", str(legal_output)) if isinstance(legal_output, dict) else str(legal_output)
    legal_summary = summarize_output(legal_output_str)
    time.sleep(5)
    
    # Step 7: Risk Scoring
    risk_context = f"{legal_context}\n\n--- Legal Analysis Summary ---\n{legal_summary}"
    try:
        risk_output = analyze_risk_logic(q, b, r, context=risk_context)
    except Exception as e:
        print(f"ERROR IN RISK AGENT: {e}")
        risk_output = {
            "overall_score": 0,
            "rating": "Error",
            "scores": {
                "market": 0, "safety": 0, "climate": 0,
                "infrastructure": 0, "legal": 0, "economic": 0
            },
            "summary": "Failed to run risk scoring."
        }
    
    print("\n" + "="*50)
    print("RISK AGENT OUTPUT:")
    print("RAW OUTPUT:", risk_output)
    print("="*50 + "\n")
    
    # Extract string for summarization if output is dict format
    risk_output_str = risk_output.get("scores", str(risk_output)) if isinstance(risk_output, dict) else str(risk_output)
    risk_summary = summarize_output(risk_output_str)
    time.sleep(5)

    # Step 8: Construction Analysis
    construction_context = f"{risk_context}\n\n--- Risk Scoring Summary ---\n{risk_summary}"
    print("CONSTRUCTION AGENT STARTING...")
    try:
        construction_output = analyze_construction_logic(q, b, r, context=construction_context)
    except Exception as e:
        print(f"ERROR IN CONSTRUCTION AGENT: {e}")
        construction_output = {"error": f"Failed to run construction agent: {e}"}
    
    print("CONSTRUCTION AGENT OUTPUT:", construction_output)
    
    # Extract string for summarization if output is dict format
    construction_output_str = construction_output.get("output", str(construction_output)) if isinstance(construction_output, dict) else str(construction_output)
    construction_summary = summarize_output(construction_output_str)
    time.sleep(5)

    # Step 9: Cash Flow Analysis
    cashflow_context = f"--- Risk Scoring Summary ---\n{risk_summary}\n\n--- Construction Analysis Summary ---\n{construction_summary}"
    print("CASH FLOW AGENT STARTING...")
    try:
        cashflow_output = analyze_cashflow_logic(q, b, r, context=cashflow_context)
    except Exception as e:
        print(f"ERROR IN CASH FLOW AGENT: {e}")
        cashflow_output = {"error": f"Failed to run cash flow agent: {e}"}
    
    print("CASH FLOW AGENT OUTPUT:", cashflow_output)
    time.sleep(5)
    
    # Step 10: Scenario Analysis
    print("SCENARIO AGENT STARTING...")
    try:
        scenario_output = analyze_scenario_logic(q, b, r, context=str(cashflow_output))
    except Exception as e:
        print("ERROR IN SCENARIO AGENT:", str(e))
        scenario_output = {"error": f"Failed to run scenario agent: {e}"}
        
    print("SCENARIO AGENT OUTPUT:", scenario_output)
    
    return {
        "query": q,
        "budget": b,
        "risk": r,
        "report": {
            "location_intelligence": location_output,
            "market_analysis": market_output,
            "future_prediction": prediction_output,
            "investment_strategy": strategy_output,
            "news_analysis": news_output,
            "legal_analysis": legal_output,
            "risk_score": risk_output,
            "construction_analysis": construction_output,
            "cashflow_analysis": cashflow_output,
            "scenario_analysis": scenario_output
        }
    }

from data.worldbank import fetch_worldbank_data

@app.get("/data/worldbank")
def get_worldbank_data(country: str):
    return fetch_worldbank_data(country)

from data.wikipedia import fetch_wikipedia_data

@app.get("/data/wikipedia")
def get_wikipedia_data(location: str):
    return fetch_wikipedia_data(location)

from data.openstreetmap import fetch_osm_data

@app.get("/data/openstreetmap")
def get_openstreetmap_data(location: str):
    return fetch_osm_data(location)

from data.fetcher import fetch_all_data

@app.post("/data/fetch")
def fetch_data_endpoint(payload: DataFetchQuery):
    return fetch_all_data(payload.query, payload.location, payload.country)

from data.numbeo import fetch_numbeo_data

@app.get("/data/numbeo")
def get_numbeo_data(location: str):
    return fetch_numbeo_data(location)

from data.climate import fetch_climate_data

@app.get("/data/climate")
def get_climate_data(lat: float, lng: float):
    return fetch_climate_data(lat, lng)

from data.forex import fetch_forex_data

@app.get("/data/forex")
def get_forex_data(country: str):
    return fetch_forex_data(country)

from data.news import fetch_news_data

@app.get("/data/news")
def get_news_data(location: str):
    return fetch_news_data(location)

from data.restcountries import fetch_country_legal_data

@app.get("/data/countries")
def get_country_legal_data(country: str):
    return fetch_country_legal_data(country)

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
