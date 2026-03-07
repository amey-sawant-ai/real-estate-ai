# Real Estate Agents API - Technical Documentation

## 1. SYSTEM OVERVIEW
- **What this system does:** The Real Estate Agents API is a robust backend engine that ingests a user's target location, budget, and risk profile, enriching it with real-time data from 8 external sources. This real data is sequentially passed through 8 specialized AI agents (each representing a real estate persona) to generate an exhaustive, professional-grade investment report covering location history, market trends, future predictions, strategy, news, legal risks, risk scoring, and construction feasibility.
- **Overall architecture:** The user's query hits the FastAPI `/analyze` endpoint -> Pre-step extracts structured location/country -> Data Pipeline (`fetcher.py`) orchestrates 8 disparate data sources to assemble actual metrics -> The sequence of 8 specialized AI Agents runs in order -> At each step, the newly generated analysis is explicitly summarized using a smaller LLM model (to prevent exceeding token limits) before being appended to the context of the next agent -> The final unified payload returns the full unsummarized output for all 8 agents.
- **Technology stack:** Python 3, FastAPI, Uvicorn (ASGI server), Groq API (LLM Orchestration: `llama-3.3-70b-versatile` for agent evaluation & data extraction, `llama-3.1-8b-instant` for compression/summarization), Pydantic (data validation). 

## 2. FOLDER STRUCTURE

- `main.py`: The core FastAPI application that defines the endpoints, orchestrates data fetching, LLM summarization, and sequentially runs all 8 agents.
- `.env`: Environment variables configuration file storing the active API keys.
- `utils/`
  - `groq_client.py`: Implements a `GroqKeyManager` to handle instantiating the Groq client, automatically rotating up to 10 API keys if a 429 Rate Limit error is encountered during a `safe_call()`.
- `agents/`
  - `location.py`: Defines the Location Intelligence Specialist agent.
  - `market.py`: Defines the Market Analysis Specialist agent.
  - `prediction.py`: Defines the Future Prediction Specialist agent.
  - `strategy.py`: Defines the Investment Strategist agent.
  - `news_agent.py`: Defines the News Analyst agent.
  - `legal_agent.py`: Defines the Legal and Tax Specialist agent.
  - `risk_agent.py`: Defines the Risk Scoring Specialist agent, returning structured JSON scores over 6 dimensions.
  - `construction_agent.py`: Defines the Construction and Development agent for building vs buying analysis.
- `data/`
  - `fetcher.py`: The single entry point `fetch_all_data()` that orchestrates calls to all individual data scripts, handling exceptions gracefully.
  - `worldbank.py`: Queries WorldBank APIs for GDP, inflation, unemployment, pop growth, etc.
  - `wikipedia.py`: Fetches the wiki page summary and intro text.
  - `openstreetmap.py`: Uses Nominatim for geocoding and Overpass API (with retry logic) to count infrastructure points (metros, hospitals, schools) in a 3km radius.
  - `numbeo.py`: Scrapes numbeo.com using BeautifulSoup to extract quality of life, safety, and living cost indices.
  - `climate.py`: Queries Open-Meteo for archival and forecasted climate data, deriving flood and heat risk indices.
  - `forex.py`: Relies on open.er-api.com to get live cross-currency exchange rates relative to USD.
  - `news.py`: Uses GDELT to find recent real estate-related news articles.
  - `restcountries.py`: Queries RestCountries API to map country basics (currencies, area, capital, full name).

## 3. DATA PIPELINE (`agents/data/`)

### The 8 Data Sources
1. **World Bank (`worldbank.py`)**: 
   - **Data Fetched:** GDP growth, inflation rate, unemployment rate, etc.
   - **Method:** REST API (`api.worldbank.org/v2`).
   - **Returns:** Metrics dictionary showing the most recent 5-year non-null indicators.
   - **Errors:** Handled universally via try/except returning `{"error": "message"}` instead of crashing.

2. **Wikipedia (`wikipedia.py`)**:
   - **Data Fetched:** Location summary and full introduction text.
   - **Method:** REST API (`en.wikipedia.org/api/rest_v1` and `en.wikipedia.org/w/api.php`).
   - **Returns:** Clean strings of `summary` and `introduction`.
   - **Errors:** Includes a trailing-word drop strategy (e.g. "Mumbai West" -> "Mumbai") before gracefully failing.

3. **OpenStreetMap (`openstreetmap.py`)**:
   - **Data Fetched:** Infrastructure points in a 3km radius (schools, malls, banks, transit).
   - **Method:** Nominatim API (geolocating) followed by Overpass API.
   - **Returns:** Exact point counts and coordinates.
   - **Errors:** Implements auto-retry intervals if Overpass hits rate limits (429).

4. **Numbeo (`numbeo.py`)**:
   - **Data Fetched:** Cost of Living, Safety Index, Quality of Life index, etc.
   - **Method:** Web Scraping (Requests + Regex pattern matching).
   - **Returns:** Dictionary of extracted index floats.
   - **Errors:** Attempts various location variants sequentially (stripping from left vs right) if exactly 200 OK + matching patterns are not found.

5. **Climate (`climate.py`)**:
   - **Data Fetched:** Average rainfall, max/min temps, and derived Risk Levels (Flood/Heat).
   - **Method:** REST API (`archive-api.open-meteo.com` and `api.open-meteo.com`).
   - **Returns:** Annual averages, abs_max temperature, and categorised Risk metrics (High/Medium/Low).
   - **Errors:** Skips if OpenStreetMap coordinates are omitted or if coordinates have no climate archive.

6. **Forex (`forex.py`)**:
   - **Data Fetched:** Convert local currency against USD, EUR, and GBP.
   - **Method:** REST API (`open.er-api.com/v6/latest/USD`) and RestCountries (for resolution).
   - **Returns:** Exchange rates and a summary label.
   - **Errors:** Evaluates standard dictionaries or falls back.

7. **News (`news.py`)**:
   - **Data Fetched:** Top 5 recent real estate articles.
   - **Method:** REST API (`api.gdeltproject.org`).
   - **Returns:** Titles, URL domains, and publish dates.
   - **Errors:** Groq extracts city/target to refine the query. If zero results, shifts to the wider country query (after sleep).

8. **REST Countries (`restcountries.py`)**:
   - **Data Fetched:** Sovereignty status, total population, timezones, capitals, languages.
   - **Method:** REST API (`restcountries.com/v3.1`).
   - **Returns:** Standard dict mapping strings and lists of facts.
   - **Errors:** Silently fails into an error dict.

### Pipeline Orchestration (`fetcher.py`)
The `fetcher.py/fetch_all_data(query, location, country)` function operates as the master orchestrator. It executes the 8 source functions sequentially ensuring no single data failure breaks the pipeline. If a function cannot resolve data, it injects a dictionary containing `"error": "..."`. The final aggregate `raw_data` dictionary object is passed back to `main.py`.

### Context Assembly
In `main.py`, the `raw_data` is intelligently parsed to build a cohesive text block (`real_data_context`) that surfaces the non-null metrics from WorldBank, Numbeo, Climate, Forex, News, and RestCountries. The LLM agents are explicitly commanded to anchor their logic in these provided metrics to prevent hallucination.

## 4. THE 8 AGENTS (`agents/agents/`)

1. **Location Intelligence Specialist (`location.py`)**:
   - **Role:** Historical & spatial context.
   - **Inputs/Outputs:** Extracts 10-20 year histories, identifying infra/economic turning points affecting value. Outputs plain text analysis.
2. **Market Analysis Specialist (`market.py`)**:
   - **Role:** Evaluates current market temperature.
   - **Inputs/Outputs:** Outputs demographics, rental yields, fast-moving property variants, supply and demand metrics.
3. **Future Prediction Specialist (`prediction.py`)**:
   - **Role:** Trajectory simulation.
   - **Inputs/Outputs:** Delivers 3, 5, and 10-year outlooks with confidence scores alongside demographic shifts.
4. **Investment Strategist (`strategy.py`)**:
   - **Role:** Actionable verdicts.
   - **Inputs/Outputs:** Recommends exactly what to build/buy alongside hard numbers for exit strategy & risks.
5. **News Analyst (`news_agent.py`)**:
   - **Role:** Sentiment decoding.
   - **Inputs/Outputs:** Classifies the GDELT headlines into Bullish, Neutral, or Bearish scores indicating opportunities or threats.
6. **Legal & Tax Specialist (`legal_agent.py`)**:
   - **Role:** Restrictive environments evaluation.
   - **Inputs/Outputs:** Lists specific property taxes, visa benefits, repatriation rules, and a Legal Friendliness Score.
7. **Risk Scoring Specialist (`risk_agent.py`)**:
   - **Role:** Automated 0-100 quantifiable scoring.
   - **Inputs/Outputs:** Returns a strict explicit JSON object defining scores over 6 dimensions (Market, Safety, Climate, Infra, Legal, Economic) and an overarching weighted summary.
8. **Construction & Development Specialist (`construction_agent.py`)**:
   - **Role:** Building evaluator.
   - **Inputs/Outputs:** Compares building vs buying ROIs, costs per sqft, and detailed timelines for approvals/development.

## 5. LLM PROCESSING & TOKEN LIMITS

### Summarization (`summarize_output`)
To conquer the strict context window token limits inherent in LLMs, the pipeline leverages two different variants of LLaMA models. Passing the exact, unsummarized output block of each prior agent successively would rapidly breach the ceiling constraints by Agent 5 or 6 and result in context overflow. 
Instead, `main.py -> summarize_output()` is triggered immediately after each Agent returns. It invokes `llama-3.1-8b-instant` (highly cost & speed efficient) to aggressively compress the previous agent's payload into a strict maximum of 150 words (saving facts & numbers). This compressed string passes to the *next* agent, while the overarching `/analyze` API response naturally retains the massive, rich text blocks.

### Groq Key Manager (`utils/groq_client.py`)
To prevent the rapid successive LLM calls per HTTP request from hitting Tier 1 rate limits (429 errors), `GroqKeyManager` instantiates an intelligent rotator pulling `GROQ_API_KEY_1`..`10` from `.env`. The `safe_call()` method tracks exceptions dynamically. If a rate limit text matches the returned request, it smoothly loops the internal index to the next key and retries seamlessly inside the function context without aborting the client's HTTP request or producing UX friction.

## 6. THE MASTER PIPELINE (`main.py`)

### `POST /analyze` Route Execution Flow:
1. **Initial Setup:** Pydantic validation guarantees `query`, `budget`, and `risk` fields.
2. **Pre-Step (Extraction):** LLaMA explicitly isolates the specific location text and geographic country to prevent mismatch errors.
3. **Data Fetching:** Pipeline pulls `fetch_all_data(...)` blocking until real metrics respond.
4. **Context Construction:** Real data parsed into clean string components.
5. **Agent Sequences:**
   - Run Agent 1 -> Compile uncompressed response -> Summarize Output.
   - Run Agent 2 (passing original context + Summary 1) -> Compile uncompressed response -> Summarize Output.
   - Run Agent 3..8 successively mapping the same process.
6. **Response Output:** Returns the JSON master dictionary containing all 8 uncompressed text reports alongside overarching queries.

### API Routes Architecture
- **`/ping`**: Returns alive status indicator.
- **`/groq-ping`**: Tests current `GroqManager` active key and returns a basic string response.
- **`/utils/keys`**: Returns the count of loaded load-balanced `.env` keys.
- **`/data/<endpoint>`**: 8 unique exposed routes to test parsing capabilities on specific sources independent of AI bottlenecks (e.g., `/data/numbeo`, `/data/climate`).
- **`/analyze/<endpoint>`**: Routes for testing individual agent logic (`/analyze/location`, `/analyze/market`) independently.
- **`/analyze` (POST)**: The master pipeline orchestrating everything above into a single output object.

## 7. KEY DESIGN DECISIONS
- **Redundant LLMs:** Separation of concerns. Using expensive, deep reasoning (`llama-3.3-70b-versatile`) explicitly for evaluation/generation, while leveraging the swift (`llama-3.1-8b-instant`) purely for text compression workflows on the backend.
- **Dynamic Key Routing**: Eliminates single points of failure directly integrated into the Groq ecosystem, unlocking scalable concurrent requests.
- **Graceful Degradation:** All data fetchers default natively to silent error-dictionary catches (`{"error":...}`). The LLM prompt explicitly commands agents to evaluate data but to proceed analyzing standard principles logically if variables say "N/A" or "Skipped".
- **Structured JSON Injection:** Implemented specifically in Extractor and Risk Agent processes using explicit Groq configuration (`response_format={"type": "json_object"}`) instead of regex/string parsing which avoids brittle parsing errors entirely.
