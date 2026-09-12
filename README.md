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

Power transformer and substation failures cause widespread blackouts costing electrical utilities over $1M per hour and leaving critical facilities without energy. Utilities currently rely on calendar-based inspections while high-frequency sensor readings (vibration, heat, partial discharge, dissolved oil gases) remain unlinked from live weather forecasts, leading to unpredicted equipment breakdown during high-load and storm events.

---

## 💡 Solution

GridPulse AI is a predictive maintenance and emergency decision support system designed with IBM Bob and watsonx.ai. It continuously monitors sensor streams across substations, evaluates transformer health indices according to IEEE standards, models environmental weather vulnerability, and automatically recommends prioritized repair orders and optimal crew pre-positioning strategies.

---

## ✨ Key Features

- **Transformer Telemetry Health Indexing**: Ingests dissolved gas analysis (DGA), oil temperature, vibration, and partial discharge metrics to calculate real-time asset degradation.
- **Dynamic Weather & Storm Impact Correlation**: Fuses real-time wind speed, temperature peaks, lightning strikes, and flood alerts to forecast localized equipment failure risks.
- **Grid Impact & Severity Scoring**: Dynamically calculates potential customer load loss, critical facility exposure (hospitals, water treatment), and risk of cascading failure.
- **Intelligent Crew Pre-Positioning**: Recommends strategic dispatch of field repair units to high-risk hubs prior to storm touchdown to minimize Mean Time to Recovery (MTTR).
- **IBM Bob & watsonx Advisory Copilot**: Natural language diagnostic assistant that generates automated root cause analysis and step-by-step Standard Operating Procedures (SOPs).

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
