# 🏢 Real Estate AI Platform

## Overview
A multi-agent AI platform that generates finance-grade real estate investment reports for any location on earth. Powered by 10 specialized AI agents and 8 real-time data sources, it provides deep insights into market trends, risks, and profitability.

## Architecture
```
Frontend (Next.js) → Node/Express API → Python FastAPI → 10 AI Agents + 8 Data Sources
```

## Tech Stack
- **Frontend**: Next.js 15, React 19, TypeScript, Tailwind CSS
- **Backend**: Node.js, Express, TypeScript, PostgreSQL, Prisma, Redis
- **AI Engine**: Python, FastAPI, Groq API, Cerebras API
- **LLM Models**: `llama-3.3-70b-versatile`, `qwen-3-235b`
- **Data Sources**: World Bank, OpenStreetMap, Numbeo, OpenMeteo, GDELT, REST Countries, Wikipedia, Open Exchange Rates

## The 10 AI Agents
1. **Location Intelligence Specialist**: Analyzes historical and spatial context to identify growth triggers.
2. **Market Analysis Specialist**: Evaluates current supply, demand, and rental yields.
3. **Future Prediction Specialist**: Provides 3, 5, and 10-year trajectory simulations with confidence scores.
4. **Investment Strategist**: Delivers actionable build/buy verdicts and exit strategy optimization.
5. **News Analyst**: Decodes real-time GDELT sentiment to identify emerging bullish or bearish triggers.
6. **Legal & Tax Specialist**: Evaluates property taxes, visa benefits, and foreign ownership restrictions.
7. **Risk Scoring Specialist**: Generates 0-100 quantifiable scores across 6 key investment dimensions.
8. **Construction & Development Specialist**: Compares renovation vs. new-build ROIs and development timelines.
9. **Cashflow Analyst**: Provides finance-grade projections including IRR, NPV, and yield analysis.
10. **Scenario Planner**: Simulates Bull, Base, and Bear cases for stress-testing investment outcomes.

## The 8 Data Sources
1. **World Bank**: GDP growth, inflation, and macroeconomic indicators.
2. **OpenStreetMap**: Infrastructure mapping (schools, transit, hospitals) via Overpass API.
3. **Numbeo**: Real-time quality of life, safety, and cost of living indices.
4. **OpenMeteo**: Historical climate archives and flood/heat risk forecasting.
5. **GDELT**: Global news sentiment extraction for real estate trends.
6. **REST Countries**: Official sovereignty, currency, and demographic baseline data.
7. **Wikipedia**: Historical context and qualitative location deep-dives.
8. **Open Exchange Rates**: Live cross-currency conversion against USD/EUR/GBP.

## API Endpoints
- **POST `/analyze`**: Generates a full investment report.
- **GET `/data/worldbank`**: Fetches macroeconomic data.
- **GET `/data/climate`**: Fetches flood and heat risk indices.
- **GET `/data/news`**: Fetches news sentiment via GDELT.
- **GET `/utils/keys`**: Returns count of active LLM API keys.
- **GET `/api/v1/health`**: (Node) Health check for the gateway.
- **POST `/api/v1/analyze`**: (Node) Gateway endpoint for full analysis.

## Sample Response
```json
{
  "risk_score": {
    "market_risk": 25,
    "safety_risk": 15,
    "climate_risk": 40,
    "infrastructure_risk": 10,
    "legal_risk": 20,
    "economic_risk": 30,
    "overall_score": 23
  }
}
```

## Getting Started

### Prerequisites
- Python 3.12+
- Node.js 18+
- PostgreSQL
- Redis

### Installation

1. **Clone the repo**:
   ```bash
   git clone <your-repo-url>
   cd real-estate
   ```

2. **Setup Python agents**:
   ```bash
   cd agents
   python -m venv venv
   source venv/bin/activate # On Windows: venv\Scripts\activate
   pip install -r requirements.txt
   cp .env.example .env
   # Add your API keys to .env
   uvicorn main:app --port 8000
   ```

3. **Setup Node backend**:
   ```bash
   cd ../backend
   npm install
   cp .env.example .env
   npm run dev
   ```

4. **Setup Frontend**:
   ```bash
   cd ../frontend
   npm install
   npm run dev
   ```

### Environment Variables
`.env.example` format for the AI Engine:
```env
GROQ_API_KEY_1=your_groq_key
GROQ_API_KEY_2=your_groq_key
CEREBRAS_API_KEY_1=your_cerebras_key
```

## Key Features
- **10 Specialized AI Agents**: Running in an intelligent sequence with context summarization.
- **Real-time Data Integration**: Orchestrates data from 8 disparate external sources.
- **Key Rotation**: Automatic failover and load balancing across Groq and Cerebras keys.
- **Token Optimization**: Smart pipeline that compresses context for deep reasoning agents.
- **Investment Grade Analysis**: Professional IRR, NPV, and Cashflow calculations.
- **Global Coverage**: Supports 195+ countries with localized tax and legal profiles.
- **Risk Evaluation**: Multi-dimensional risk scoring with quantitative heatmaps.

## License
MIT
