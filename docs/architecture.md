# GridPulse AI — Architecture

## System Overview

GridPulse AI is a full-stack power grid risk monitoring and advisory platform built for the IBM watsonx hackathon. It combines real-time sensor telemetry, dissolved gas analysis, weather data, and graph-topology-based cascade analysis to deliver AI-powered risk assessments.

---

## Architecture Diagram

```
┌─────────────────────────────────────────────────────────────┐
│                     FRONTEND (React + Vite)                 │
│  Dashboard │ Assets │ Risk │ Grid │ Weather │ Crew │ AI      │
│  Chart.js Visualizations + SVG Grid Topology Map            │
└──────────────────────┬──────────────────────────────────────┘
                       │ HTTP / REST
┌──────────────────────▼──────────────────────────────────────┐
│                  FASTAPI BACKEND (Python 3.11)              │
│                                                             │
│  /api/v1/health   /api/v1/assets     /api/v1/risk           │
│  /api/v1/grid     /api/v1/weather    /api/v1/advisory       │
│  /api/v1/recommendations             /api/v1/dashboard      │
│                                                             │
│  ┌─────────────────┐   ┌─────────────────────────────────┐  │
│  │   RISK ENGINE   │   │    CASCADE ANALYZER (Neo4j)     │  │
│  │  failure_prob   │   │  BFS graph traversal            │  │
│  │  weather_risk   │   │  cascade_risk formula           │  │
│  │  grid_impact    │   │  affected_facilities            │  │
│  │  cascade_risk   │   └─────────────────────────────────┘  │
│  │  critical_mult  │                                        │
│  └─────────────────┘   ┌─────────────────────────────────┐  │
│                        │    ADVISORY ENGINE              │  │
│  ┌─────────────────┐   │  IBM Granite → watsonx.ai       │  │
│  │ DGA ADAPTER     │   │  Local Fallback (rule-based)    │  │
│  │ Rogers Ratios   │   └─────────────────────────────────┘  │
│  │ IEEE C57.104    │                                        │
│  └─────────────────┘                                        │
└───────────┬────────────────────────┬────────────────────────┘
            │                        │
┌───────────▼──────────┐  ┌──────────▼──────────────────────┐
│   POSTGRESQL (15)    │  │         NEO4J (5)               │
│                      │  │                                 │
│  assets              │  │  (:Substation)-[:CONTAINS]->   │
│  sensor_readings     │  │  (:Transformer)-[:FEEDS]->     │
│  dga_readings        │  │  (:Feeder)-[:SUPPLIES]->       │
│  weather_readings    │  │  (:CriticalFacility)           │
│  incidents           │  │                                 │
│  risk_scores         │  │  Graph queries for cascade     │
│  work_orders         │  │  impact analysis               │
│  ai_advisories       │  │                                 │
└──────────────────────┘  └─────────────────────────────────┘
```

---

## Technology Stack

| Layer | Technology |
|---|---|
| Frontend | React 18 + TypeScript, Vite, Chart.js, React Router |
| Backend | Python 3.11, FastAPI, Uvicorn, Pydantic v2 |
| Relational DB | PostgreSQL 15 (SQLAlchemy async + Alembic) |
| Graph DB | Neo4j 5 (async neo4j driver, Cypher queries) |
| AI / LLM | IBM watsonx.ai + IBM Granite (Granite 3.3-8b / 13B Instruct) |
| Fallback AI | Rule-based local advisory engine |
| Containers | Docker + Docker Compose |
| Testing | Pytest + pytest-asyncio |

---

## Risk Engine Formula

```
base_risk = 0.30 × failure_probability   (from sensor + DGA)
          + 0.20 × asset_health_risk     (derived from failure_prob)
          + 0.15 × weather_risk          (wind, temp, lightning, flood)
          + 0.20 × grid_impact           (Neo4j downstream traversal)
          + 0.15 × cascade_risk          (critical facility weighting)

final_risk_score = clamp(base_risk × critical_multiplier, 0, 1)
```

**Critical Multipliers:**
- Normal asset: ×1.0
- Important facility: ×1.2
- Critical facility (hospital/water/airport): ×1.5

---

## Data Flow

1. **Sensor Telemetry** → PostgreSQL `sensor_readings`
2. **DGA Analysis** → IEEE C57.104 Rogers Ratio classification → failure probability
3. **Weather Data** → wind + temp + lightning + flood → weather risk score
4. **Neo4j Graph** → BFS traversal → cascade risk + grid impact
5. **Risk Engine** → weighted formula → `risk_scores` table
6. **Advisory Engine** → IBM Granite or local fallback → structured response
7. **Frontend** → fetches all data from FastAPI → renders glassmorphic dashboard

---

## Key API Endpoints

| Method | Path | Description |
|---|---|---|
| GET | `/api/v1/health` | Service health + dependency status |
| GET | `/api/v1/dashboard` | Aggregated dashboard data |
| GET | `/api/v1/assets` | All assets with risk scores |
| GET | `/api/v1/assets/{id}` | Full asset detail |
| GET | `/api/v1/risk` | All risk scores ranked |
| GET | `/api/v1/grid/topology` | Full grid graph (single-line schematic + GIS) |
| GET | `/api/v1/grid/assets/{id}/impact` | Cascade failure analysis |
| GET | `/api/v1/weather` | Weather risk per asset |
| GET | `/api/v1/weather/crew-preposition` | 48-Hour field crew staging & dispatch plan |
| POST | `/api/v1/advisory` | Asset-specific AI advisory |
| POST | `/api/v1/advisory/chat` | Dynamic context-aware free-form AI chat |
| GET | `/api/v1/recommendations` | Auto-generated work order recommendations |
| GET | `/api/v1/workorders` | All open & completed work orders |
| POST | `/api/v1/workorders` | Create new work order |
| PATCH | `/api/v1/workorders/{id}` | Update work order status and field notes |
