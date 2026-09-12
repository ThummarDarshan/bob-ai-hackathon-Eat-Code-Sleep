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

### The $1M-Per-Hour Crisis

Power transformer and substation failures cause widespread blackouts costing electrical utilities **over $1 million per hour** — and the consequences extend far beyond financial loss. Hospitals lose backup power, water treatment plants shut down, and millions of citizens are left without electricity for hours or days.

### What's Broken Today

Despite an abundance of sensor infrastructure already installed across substations, **the grid remains dangerously reactive**:

| Gap | Reality |
|---|---|
| 📅 **Calendar-based maintenance** | Utilities schedule inspections on fixed intervals, not on actual equipment health — meaning critical degradation between cycles goes undetected. |
| 📡 **Siloed sensor data** | Transformers continuously emit temperature, vibration, partial discharge, and dissolved oil gas (DGA) readings that are **never correlated with each other** or with external risk signals. |
| 🌩️ **Weather-blind decisions** | Weather forecasts exist, but grid operations teams have no system that **automatically combines storm forecasts with equipment vulnerability** to pre-empt failures. |
| 🗂️ **Buried incident history** | Years of historical failure records sit in maintenance logs that are **never mined for failure pattern intelligence**. |
| 🚒 **Reactive crew dispatch** | Field repair crews are deployed *after* equipment fails, not positioned ahead of forecasted high-risk windows — dramatically inflating Mean Time to Recovery (MTTR). |

### The Compounding Risk

When a Category-3 storm intersects with a transformer already running at 92 °C oil temperature and showing elevated hydrogen gas ratios — that is a predictable catastrophe. **The data to prevent it already exists. It just isn't connected.**

---

## 💡 Solution

### GridPulse AI — Proactive Grid Resilience Copilot

GridPulse AI is a predictive maintenance and emergency decision-support system built on **IBM Bob** and **watsonx.ai (IBM Granite models)**. It fuses multi-source intelligence streams — asset health telemetry, live weather forecasts, and historical incident records — into a unified risk model that tells grid operators exactly **which equipment will fail, when, and what to do about it before it happens**.

### How It Works

```
Sensor Telemetry (DGA, vibration, temp, PD)
          +
Weather Forecast API (wind, lightning, flood)     ──▶  Multi-Factor Risk Fusion Engine
          +                                                        │
Historical Incident Records (failure patterns)                     ▼
                                              Asset Severity Score & Ranked Work Orders
                                                                   │
                                                                   ▼
                                              IBM Bob / watsonx.ai Advisory Copilot
                                              (NL Diagnostics + SOP Generation + Crew Plan)
```

### What Makes GridPulse AI Unique

> **Standard predictive maintenance tools look at sensors. GridPulse AI looks at sensors, weather, and history — simultaneously — and speaks to operators in plain language.**

| Unique Differentiator | Description |
|---|---|
| 🧬 **IEEE C57.104 DGA Ratio Intelligence** | Instead of raw sensor thresholds, GridPulse uses dissolved gas ratios (H₂, CH₄, C₂H₂) computed against IEEE standards to classify transformer fault type (thermal, arcing, partial discharge) — not just fault presence. |
| 🌦️ **Storm-Asset Vulnerability Matrix** | A live weather window is cross-referenced against each asset's degradation state to compute a compounded failure probability — **hours before a storm makes landfall**, not after. |
| 📊 **Cascading Failure Graph Scoring** | Assets are not ranked in isolation. The severity score accounts for grid topology: a single substation failure that would cascade to 3 downstream nodes is scored higher than an isolated transformer failure. |
| 🗣️ **Bob-Powered NL Advisory Interface** | Field operators query the system in plain English: *"Which substations are most at risk this weekend?"* or *"Generate a repair SOP for Transformer T-07."* IBM Bob synthesises context from all data layers and responds with actionable, jargon-free guidance. |
| 🚁 **Pre-emptive Crew Pre-Positioning Engine** | Rather than dispatching crews reactively, GridPulse outputs a **48-hour crew staging plan** that places repair units at optimal geographic hubs ahead of predicted failure windows — minimising MTTR from hours to minutes. |
| 🔁 **Closed-Loop Learning from Incidents** | Every resolved incident feeds back into the historical pattern store. The system continuously recalibrates its failure signature library — getting smarter after every storm season. |
| 🏥 **Critical Facility Impact Weighting** | Assets serving hospitals, emergency services, water treatment, and data centres receive a **Critical Infrastructure Multiplier** in the severity score, ensuring life-safety dependencies always surface at the top of the priority queue. |

---

## ✨ Key Features

- **Transformer Telemetry Health Indexing**: Ingests dissolved gas analysis (DGA), oil temperature, vibration, and partial discharge metrics to calculate real-time asset degradation scores conforming to IEEE C57.104.
- **Dynamic Weather & Storm Impact Correlation**: Fuses real-time wind speed, temperature extremes, lightning strike proximity, and flood-level alerts to compute per-asset environmental failure probability.
- **Cascading Grid Impact & Severity Scoring**: Dynamically calculates potential customer load loss, downstream node exposure, critical facility dependency, and cascading failure risk across the full grid topology.
- **Intelligent Crew Pre-Positioning Engine**: Generates a 48-hour crew staging and dispatch plan placing field teams at strategic geographic hubs *before* failures occur — minimising Mean Time to Recovery (MTTR).
- **IBM Bob & watsonx.ai Advisory Copilot**: Conversational AI interface that provides natural-language diagnostics, automated root-cause analysis, and step-by-step Standard Operating Procedures (SOPs) tailored to each asset event.
- **Closed-Loop Incident Learning**: Historical failure records are continuously mined and used to recalibrate failure signature models after each incident cycle.

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
