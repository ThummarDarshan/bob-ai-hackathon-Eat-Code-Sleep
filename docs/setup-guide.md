# Setup Guide: GridPulse AI

> **This document contains verified instructions to run GridPulse AI locally.**

## Prerequisites

Before starting, ensure you have:
- **Python 3.10+** installed on your machine (`python --version`)
- **Git** installed (`git --version`)
- A modern web browser (Google Chrome, Microsoft Edge, Firefox, or Safari)
- *(Optional)* An IBM Cloud account with watsonx.ai credentials if testing live Granite LLM endpoints.

---

## Environment Configuration

1. Clone the repository and enter the project directory:
   ```bash
   git clone https://github.com/ThummarDarshan/bob-ai-hackathon-Eat-Code-Sleep.git
   cd bob-ai-hackathon-Eat-Code-Sleep
   ```

2. Copy the environment variables template:
   ```bash
   cp src/.env.example src/.env
   ```

3. Environment Variables breakdown:

| Variable | Description | Default / Required |
|---|---|---|
| `PORT` | Local web server listening port | `8000` (Yes) |
| `HOST` | Bind host address | `0.0.0.0` (Yes) |
| `ENVIRONMENT` | Deployment environment mode | `development` (Yes) |
| `IBM_WATSONX_APIKEY` | IBM watsonx API Key | *(Optional, runs fallback if empty)* |
| `IBM_WATSONX_PROJECT_ID`| IBM watsonx Project ID | *(Optional)* |
| `IBM_WATSONX_URL` | Regional IBM Cloud inference URL | `https://us-south.ml.cloud.ibm.com` |

---

## Installation

1. Create and activate a Python virtual environment:
   ```bash
   # On Windows (PowerShell / Command Prompt):
   python -m venv .venv
   .venv\Scripts\activate

   # On macOS / Linux:
   python3 -m venv .venv
   source .venv/bin/activate
   ```

2. Install backend dependencies:
   ```bash
   pip install -r src/requirements.txt
   ```

---

## Running the Application

1. Start the GridPulse AI FastAPI server:
   ```bash
   python -m uvicorn src.app.main:app --host 0.0.0.0 --port 8000 --reload
   ```

2. Access the application in your browser:
   - **Interactive Web Dashboard**: `http://localhost:8000/`
   - **Interactive Swagger API Docs**: `http://localhost:8000/docs`
   - **Substations Telemetry API**: `http://localhost:8000/api/v1/substations`
   - **Crew Pre-Positioning API**: `http://localhost:8000/api/v1/prepositioning-plan`

---

## Running Automated Verification & Tests

To verify that the risk prediction calculations and API endpoints function properly:
```bash
python -c "from src.app.engine import EquipmentRiskEngine; print('Engine Health Test:', EquipmentRiskEngine.calculate_health_index({'oil_temperature_c': 70, 'vibration_mms': 2.0, 'partial_discharge_pc': 150, 'acetylene_ppm': 0.5, 'ethylene_ppm': 10}))"
```

Expected output:
```
Engine Health Test: 100.0
```

---

## Troubleshooting

| Issue | Cause | Solution |
|---|---|---|
| `ModuleNotFoundError: No module named 'fastapi'` | Virtual environment not active or dependencies not installed | Run `.venv\Scripts\activate` (or `source .venv/bin/activate`) followed by `pip install -r src/requirements.txt`. |
| `Address already in use: 8000` | Port 8000 is occupied by another local service | Start uvicorn on another port: `python -m uvicorn src.app.main:app --port 8080 --reload`. |
| `UnicodeEncodeError / SyntaxError` | Running outdated Python version | Verify Python version is 3.10 or higher using `python --version`. |
