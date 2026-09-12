# ⚡ GridPulse AI — Power Outage & Grid Equipment Failure Advisor

> Proactive AI-driven resilience copilot for power utilities: fusing substation asset health telemetry with real-time weather analytics to predict catastrophic grid outages and optimize field crew dispatch.

---

## 👥 Team

| Field | Value |
|---|---|
| **Team Name** | Eat-Code-Sleep |
| **Track** | AI |
| **Team Lead** | Darshan Thummar — darshantce.059@gmail.com |
| **Members** | Shreeja Upadhyay, Kishan Vadsola, Vishv Undavia |

---

## 🎯 Problem Statement

Power transformer and substation failures cost utilities **over $1M/hour** in blackouts, yet most still rely on calendar-based maintenance. Sensor data (temperature, vibration, partial discharge, DGA) already shows failure signatures weeks ahead — but it's never combined with weather forecasts or historical incident records to act in time. The result: predictable catastrophes that nobody predicted.

---

## 💡 Solution

**GridPulse AI** is a predictive maintenance copilot built on **IBM Bob** and **watsonx.ai**. It fuses asset health telemetry, live weather forecasts, and historical failure records into a unified risk model — telling operators which equipment will fail, when, and exactly what to do before it happens.

**What makes it unique:**

- 🧬 **IEEE C57.104 DGA Intelligence** — classifies fault *type* (thermal / arcing / partial discharge) from dissolved gas ratios, not just raw thresholds
- 🌦️ **Storm-Asset Vulnerability Matrix** — cross-references live weather with each asset's degradation state to compute compounded failure probability *hours before landfall*
- 📊 **Cascading Failure Graph Scoring** — ranks assets by grid topology impact; a failure cascading to 3 downstream nodes scores higher than an isolated one
- 🚁 **48-Hour Crew Pre-Positioning Engine** — stages repair crews at optimal hubs *before* failures occur, cutting MTTR from hours to minutes
- 🏥 **Critical Facility Multiplier** — hospitals, water plants, and emergency services are automatically weighted to the top of the priority queue
- 🔁 **Closed-Loop Incident Learning** — every resolved incident recalibrates the failure signature model, improving accuracy each storm season
- 🗣️ **Bob NL Advisory Interface** — operators ask plain-English questions; Bob synthesises all data layers into actionable diagnostics and SOPs

---

## ✨ Key Features

- **Asset Health Indexing** — real-time DGA, oil temperature, vibration, and partial discharge scoring (IEEE C57.104)
- **Weather-Risk Fusion** — per-asset failure probability from wind, lightning, flood, and temperature extremes
- **Severity-Ranked Work Orders** — cascading impact + critical facility weighting drives the maintenance queue
- **Pre-emptive Crew Dispatch** — 48-hour staging plan generated before failures, not after
- **Bob & watsonx.ai Copilot** — natural-language root-cause analysis and step-by-step SOPs
- **Self-Improving Models** — historical incident feedback loop continuously sharpens predictions

---

## 🛠️ Tech Stack

| Category | Technologies |
|---|---|
| **Languages** | Python 3.10+, JavaScript (ES6+), HTML5, CSS3 |
| **Frameworks** | FastAPI, Uvicorn, Pydantic |
| **IBM Technologies** | IBM Bob, watsonx.ai, IBM Granite Models |
| **Data & Storage** | SQLite / In-Memory TimeSeries State Cache |
| **Design & Visualization**| Modern Glassmorphic CSS, Mermaid.js, Chart.js / SVG Visualizers |

---

## 📁 Repository Structure

```
├── src/                  # Complete backend API & interactive operational dashboard
│   ├── app/              # FastAPI application core, routes, and risk engines
│   ├── static/           # Responsive operator UI and monitoring views
│   ├── data/             # Asset registry, sensor telemetry, and weather mock streams
│   ├── .env.example      # Environment variable template
│   └── README.md         # Source directory documentation
├── docs/                 # Detailed architectural and operational documentation
│   ├── problem-statement.md
│   ├── solution-overview.md
│   ├── architecture.md
│   └── setup-guide.md
├── demo/                 # Demonstration artifacts
│   ├── screenshots/      # Application screenshots
│   ├── demo-video-link.txt  # Link to walkthrough video
│   └── live-demo-url.txt    # Live deployment status
├── presentation/         # Project slide deck
└── submission.yaml       # Structured submission metadata
```

---

## ⚡ How to Run

```bash
# 1. Clone the repo
git clone https://github.com/ThummarDarshan/bob-ai-hackathon-Eat-Code-Sleep.git
cd bob-ai-hackathon-Eat-Code-Sleep

# 2. Set up Python environment
python -m venv .venv
# On Windows:
.venv\Scripts\activate
# On Linux/macOS:
# source .venv/bin/activate

# 3. Install dependencies
pip install -r src/requirements.txt

# 4. Configure environment variables
cp src/.env.example src/.env

# 5. Start the GridPulse AI Server
python -m uvicorn src.app.main:app --host 0.0.0.0 --port 8000 --reload
```

Open your browser at `http://localhost:8000` to interact with the GridPulse AI Control Center.

---

## 🖥️ Demo

| Artifact | Link |
|---|---|
| 📹 Demo Video | [See demo/demo-video-link.txt](demo/demo-video-link.txt) |
| 🌐 Live Demo | [See demo/live-demo-url.txt](demo/live-demo-url.txt) |
| 🖼️ Screenshots | [See demo/screenshots/](demo/screenshots/) |
| 📊 Presentation | [See presentation/](presentation/) |

---

## ⚠️ Known Limitations

- **Simulated Grid Telemetry**: Asset sensor metrics and weather feeds simulate real-time SCADA and meteorological APIs for repeatable demonstration environments.
- **Advisory Control**: The system outputs dispatch orders and breaker isolation advisories for human grid operators rather than directly actuating physical substation relays.
- **Offline LLM Fallback**: If an active watsonx.ai API key is not supplied in `.env`, the system automatically defaults to an intelligent local heuristic reasoning engine.

---

## 🏅 What We're Most Proud Of

The integration of the multi-factor risk fusion algorithm that links chemical dissolved gas ratios (IEEE C57.104 DGA standard) directly with approaching weather storm fronts, enabling grid operators to pre-stage emergency response crews hours ahead of line collapse.

---

