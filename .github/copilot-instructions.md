# Copilot Instructions for Real Estate Investment Analysis Platform

## Architecture Overview

This is a full-stack real estate investment platform with three layers:

1. **Python Agent Service** (`agents/`): FastAPI-based AI analysis orchestration with 8 specialized Groq LLM agents
2. **Node.js Backend** (`backend/`): Express.js TypeScript server proxying to Python agents and managing persistence
3. **Next.js Frontend** (`frontend/`): React-based UI consuming backend APIs

**Key Pattern**: The frontend calls `/api/v1/query` on Node backend → backend proxies to Python `/analyze` endpoint → Python orchestrates data fetching + sequential agent analysis → unified report returned.

## Critical System Flows

### Data Pipeline (agents/data/fetcher.py)
The `fetch_all_data(query, location, country)` function orchestrates 8 data sources sequentially. Each source (WorldBank, Wikipedia, OpenStreetMap, Numbeo, Climate, Forex, News, RestCountries) wraps errors as `{"error": "message"}` to prevent pipeline failure. Raw data is assembled into a single dict and passed to agents with non-null metrics embedded as context strings.

### Agent Orchestration (agents/main.py)
After fetching raw data, agents run in fixed sequence: Location → Market → Prediction → Strategy → News → Legal → Risk → Construction. Between each agent, `summarize_output()` compresses analysis using `llama-3.1-8b-instant` to prevent token overflow before passing context to the next agent. Final output returns all unsummarized agent analyses.

**Agent ReAct Pattern**:
- **Thought**: Agent reasons about the investment scenario (e.g., "How does flood risk affect ROI?")
- **Action**: Agent retrieves or analyzes data from `real_data_context` 
- **Observation**: Agent processes results and identifies key insights
- **Iteration**: Continue with bounded loop (never infinite)
- **Graceful Degradation**: If data missing, agent acknowledges gap and provides best-effort analysis

### LLM Key Rotation (agents/utils/groq_client.py)
The `GroqKeyManager` loads up to 10 API keys from `GROQ_API_KEY_1` through `GROQ_API_KEY_10` (or falls back to `GROQ_API_KEY`). On 429 rate limit errors, it automatically rotates to the next key. This is critical for production stability when a single key hits limits.

## Project-Specific Conventions

### Agent Prompt Structure (AI Agents Architect Pattern)
Every agent (location.py, market.py, etc.) implements a **ReAct loop** with reasoning, tool use, and observation:
1. System prompt with role, goal, and data citation rules (e.g., "quote specific numbers from provided data")
2. User prompt with query + budget + risk profile + optional context from previous agent
3. Always use `groq_manager.safe_call()` for LLM calls—never instantiate Groq client directly
4. Include explicit iteration limits and graceful degradation when data is unavailable
5. Log all agent reasoning (use Python's logging module, never print())

**Enforce Data Grounding**: Agents MUST cite actual data values ("GDP growth is 3.99%") not hallucinate metrics. This prevents agent autonomy from creating false risk assessments.

### Error Handling Pattern (Production Code)
Apply exponential backoff for rate limits and transient failures:
```python
import logging
import time

logger = logging.getLogger(__name__)

def safe_agent_call_with_retry(query, max_retries=3):
    for attempt in range(max_retries):
        try:
            return groq_manager.safe_call(...)
        except Exception as e:
            if attempt == max_retries - 1:
                logger.error(f"Agent failed after {max_retries} attempts: {e}")
                raise
            backoff = 2 ** attempt
            logger.warning(f"Attempt {attempt + 1} failed. Retrying in {backoff}s")
            time.sleep(backoff)
```

### Node Backend Routes (Senior Fullstack TypeScript Pattern)
- `/api/v1/health` → health check endpoint (pings Python `/ping` and returns `{node, python, timestamp}`)
- `/api/v1/agents/ping` → proxies to Python `GET /ping` endpoint
- `/api/v1/analyze` → POST endpoint for analysis queries (calls Python `/analyze`, defined in `analysis.ts`)
- `/api/v1/query` → main query entry point (defined in `query.routes.ts`)
- `/api/v1/users/*` → user management endpoints

All routes follow senior fullstack patterns:
1. Use `async/await` for all Promise-based operations (fetch, database calls)
2. Wrap external service calls in try-catch with proper error formatting
3. Validate input using Zod schemas (see `types/` and `config/`)
4. Always proxy to Python at `${AGENTS_URL}` env var, never hardcode `localhost:8000`
5. Log errors via pino logger, never console.log in production

**Route Handler Template** (Senior Fullstack Pattern):
```typescript
import { Router, Request, Response, NextFunction } from 'express';
import { z } from 'zod';
import logger from '@/utils/logger';

const router = Router();

// Validation schema
const QuerySchema = z.object({
  query: z.string().min(1),
  budget: z.string(),
  risk: z.enum(['low', 'medium', 'high'])
});

/**
 * POST /api/v1/query
 * Execute AI analysis for real estate query
 */
router.post('/execute', async (req: Request, res: Response, next: NextFunction) => {
  try {
    // Validate input
    const payload = QuerySchema.parse(req.body);
    
    // Proxy to Python service with error handling
    const AGENTS_URL = process.env.AGENTS_URL || 'http://localhost:8000';
    const response = await fetch(`${AGENTS_URL}/analyze`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(payload)
    });

    if (!response.ok) {
      logger.error(`Agent service error: ${response.status}`);
      return res.status(response.status).json({
        success: false,
        error: 'Analysis service temporarily unavailable'
      });
    }

    const analysis = await response.json();
    logger.info(`Analysis completed for query: ${payload.query.slice(0,50)}`);
    return res.status(200).json({ success: true, data: analysis });
    
  } catch (err) {
    next(err); // Pass to errorHandler middleware
  }
});

export default router;
```

### Error Handling Philosophy (Multi-Layer Strategy)
- **Data sources** (Python): Wrap failures as dict with `"error"` key; continue pipeline. Use logging.error() for failures.
- **Agents** (Python): Let Groq exceptions propagate via groq_manager; rate limit retry is built-in. Never silent-fail.
- **API** (Node): Express middlewares catch errors via `errorHandler`; format as JSON with status codes. Client-friendly error messages only.
- **Frontend** (React/Next.js): Handle network errors gracefully with retry UI, never crash on failed API calls.

Implementation ensures:
1. **Graceful degradation**: One failing data source doesn't break the entire analysis
2. **Clear failure modes**: Agents know which context is missing and adjust reasoning
3. **Observability**: All errors logged with context (attempt count, resource, timestamp)

## Developer Workflows

### Running the Full Stack Locally
```bash
# Terminal 1: Python agents service
cd agents
pip install -r requirements.txt
python main.py  # Starts on http://localhost:8000

# Terminal 2: Node backend
cd backend
npm install
npm run dev  # Starts on http://localhost:4000

# Terminal 3: Next.js frontend
cd frontend
npm install
npm run dev  # Starts on http://localhost:3000
```

### Adding a New Data Source
1. Create `agents/data/new_source.py` with `fetch_new_source_data()` function that returns a dict
2. Implement error handling with try/except returning `{"error": "message"}` (never raise exceptions)
3. Include logging for API calls and failures: `logger.error(f"Failed to fetch from API: {e}")`
4. Import and call it in `agents/data/fetcher.py` within `fetch_all_data()`, wrapping with try/except
5. Parse non-error values into `real_data_context` string in `agents/main.py` (around line 150)
6. Validate returned data structure with type hints and docstrings

**Data Source Template** (Production Pattern):
```python
import logging
from typing import Dict, Any
import requests

logger = logging.getLogger(__name__)

def fetch_new_source_data(location: str) -> Dict[str, Any]:
    """Fetch data from external API with error handling and logging.
    
    Args:
        location: Target location name
        
    Returns:
        Dict with data keys, or {"error": "message"} on failure
    """
    try:
        response = requests.get(f"https://api.example.com/data", 
                               params={"q": location},
                               timeout=5)
        response.raise_for_status()
        data = response.json()
        logger.info(f"Successfully fetched data for {location}")
        return {
            "key1": data.get("value1"),
            "key2": data.get("value2")
        }
    except requests.exceptions.RequestException as e:
        logger.error(f"API request failed for {location}: {e}")
        return {"error": f"Failed to fetch from source: {str(e)}"}
    except (ValueError, KeyError) as e:
        logger.error(f"Data parsing failed for {location}: {e}")
        return {"error": f"Invalid response format: {str(e)}"}
```

### Adding a New Agent
1. Create `agents/agents/new_agent.py` with `analyze_new_agent_logic(query, budget, risk, context="")` function
2. Use `groq_manager.safe_call()` with system and user prompts enforcing data citation
3. Include explicit iteration limits and graceful degradation when data is unavailable
4. Log all agent reasoning (use Python's logging module, never print())
5. Call agent in `/analyze/new_agent` endpoint in `agents/main.py`
6. Add to sequential orchestration in the main `/analyze` endpoint (line ~250+)

**Agent Implementation Template** (ReAct Pattern):
```python
import logging
from utils.groq_client import groq_manager

logger = logging.getLogger(__name__)

def analyze_new_agent_logic(query: str, budget: str, risk: str, context: str = "") -> str:
    """Analyze investment from specialist perspective using ReAct pattern.
    
    Args:
        query: User's investment query
        budget: Budget constraints
        risk: Risk profile
        context: Analysis from previous agents
        
    Returns:
        Analysis text citing actual data values
    """
    system_prompt = """You are a Specialist Agent for real estate investment analysis.
Your goal is to [agent-specific goal with data citation rules].
CRITICAL: You MUST explicitly reference and cite actual numbers from the real_data_context.
Always quote specific values. Never invent metrics or hallucinate data.
If data is missing, explicitly acknowledge the gap and provide best-effort analysis."""

    user_prompt = f"Query: {query}\nBudget: {budget}\nRisk Profile: {risk}"
    if context:
        user_prompt += f"\n\nContext from previous analysis:\n{context}"
    
    # Add the real_data_context here (passed from main.py)
    # user_prompt += f"\n\nReal Data Context:\n{real_data_context}"

    logger.info(f"Starting analysis for query: {query[:50]}...")
    
    try:
        response = groq_manager.safe_call(
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            model="llama-3.3-70b-versatile",
            temperature=0.3
        )
        logger.info("Analysis completed successfully")
        return response
    except Exception as e:
        logger.error(f"Agent analysis failed: {e}")
        raise
```

### Testing
- Python unit tests in `agents/tests/test_data_sources.py`
- Run: `cd agents && pytest`
- Debug individual agents with `debug.py` (queries single agent in isolation)

## Key Files Reference

| File | Purpose |
|------|---------|
| `agents/main.py` | FastAPI app, endpoints for each agent, data context assembly |
| `agents/data/fetcher.py` | Master orchestrator for all 8 data sources |
| `agents/utils/groq_client.py` | Key rotation + rate limit retry logic (shared by all agents) |
| `agents/agents/*.py` | Individual agent implementations (8 files, location/market/prediction/strategy/news/legal/risk/construction) |
| `backend/src/routes/index.ts` | Route aggregator pointing to agent/query/user routes |
| `backend/src/routes/agents.routes.ts` | Proxy to Python agent service `/ping` endpoint |
| `backend/src/routes/analysis.ts` | Analysis route forwarding POST requests to Python `/analyze` |
| `backend/src/services/agentService.ts` | Service with `runAnalysis()` and `isPythonServiceOnline()` functions |
| `backend/prisma/schema.prisma` | Database schema (currently minimal: User model only) |
| `frontend/app/page.tsx` | Main Next.js page (UI entry point) |

## Available Skills Reference

### 1. **ai-agents-architect** - Building Autonomous AI Agents
Use this skill when designing or implementing agents with complex reasoning:
- **ReAct Pattern**: Thought → Action → Observation loops (all agents use this)
- **Tool Registry**: Managing available data sources and APIs
- **Anti-patterns to avoid**: Unlimited autonomy, tool overload, memory hoarding
- **Sharp edges**: Always set iteration limits, surface tool errors, implement tracing

All 8 agents in `agents/agents/` follow the ReAct pattern with bounded iterations and graceful degradation.

### 2. **senior-fullstack** - TypeScript/Node.js Backend Development
Use this skill when adding routes, services, or database logic to the backend:
- **Route patterns**: Async/await, Zod validation, proper error formatting
- **Code quality**: TypeScript typing, logging via pino, environment variable management
- **Tech stack**: Express, Prisma, PostgreSQL, environment configuration
- **Best practices**: No console.log in production, validate inputs, wrap external calls in try-catch

All Node routes must follow the patterns in `backend/src/routes/` with proper async handling and validation.

### 3. **dataverse-python-production-code** - Production Python Code
Use this skill when adding Python services, improving error handling, or optimizing code:
- **Error handling**: Exponential backoff for retries, logging instead of print()
- **Code structure**: Imports → constants → logging config → functions → classes
- **Best practices**: Type hints, docstrings, proper logging, timeout management
- **Production patterns**: Connection pooling, singleton patterns, OData optimization

The data pipeline in `agents/data/` exemplifies production Python with retry logic and comprehensive logging.

## Common Pitfalls to Avoid

1. **Direct Groq Instantiation**: Always use `groq_manager.safe_call()`, not `Groq()` directly. This skips rate-limit rotation.
2. **Breaking the Pipeline**: Always wrap data source calls with try/except returning `{"error": "..."}`. One failure must not crash the orchestrator.
3. **Token Overflow**: Summarization between agents is intentional; do not remove it or agents will fail mid-sequence.
4. **Missing Data Citation**: Agents must quote specific numbers from `real_data_context`, not invent metrics. Hallucinations create false risk scores.
5. **Hardcoded API Endpoints**: Use `${AGENTS_URL}` env var in Node routes, never hardcode `localhost:8000`. Breaks in staging/production.
6. **Silent Failures in Agents**: Always log agent errors via `logger.error()` with context. Use print() only for debugging.
7. **Tool Overload in Agents**: Each agent should have a clear ReAct loop with max iteration limits. Unbounded agent calls waste tokens.
8. **Missing Type Hints (Node)**: All Express handlers must have TypeScript types. This catches integration bugs early.
9. **Unlimited Agent Autonomy**: Agents must degrade gracefully when data is missing, not speculate. Always provide fallback logic.

## Environment Setup

**agents/.env** (Python service):
```
GROQ_API_KEY_1=gsk_...
GROQ_API_KEY_2=gsk_...  # Optional, up to 10 keys
# (or single GROQ_API_KEY)
```

**backend/.env** (Node service):
```
AGENTS_URL=http://localhost:8000
DATABASE_URL=postgresql://...
CLIENT_URL=http://localhost:3000
```

**frontend/.env.local**:
```
NEXT_PUBLIC_API_URL=http://localhost:4000/api/v1
```
