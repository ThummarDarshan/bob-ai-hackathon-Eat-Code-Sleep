from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Dict, List, Optional
from src.app.engine import EquipmentRiskEngine

app = FastAPI(
    title="GridPulse AI - Power Outage & Grid Equipment Failure Advisor",
    description="Intelligent outage forecasting and substation maintenance pre-positioning engine powered by IBM Bob & watsonx",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Simulated in-memory database of Substation Assets
SUBSTATIONS = [
    {
        "id": "SUB-NORTH-01",
        "name": "North Cascade 400kV Primary Substation",
        "location": "North Sector, Zone 4",
        "capacity_mva": 250,
        "critical_customers": 42000,
        "equipment": {
            "type": "Power Transformer T-101",
            "mfg_year": 2011,
            "sensor_telemetry": {
                "oil_temperature_c": 92.4,
                "vibration_mms": 4.8,
                "partial_discharge_pc": 540.0,
                "acetylene_ppm": 4.2,
                "ethylene_ppm": 68.0
            }
        },
        "weather": {
            "wind_speed_kmh": 68.5,
            "ambient_temp_c": 38.2,
            "lightning_strikes_10km": 14,
            "precip_mmh": 22.0
        }
    },
    {
        "id": "SUB-EAST-04",
        "name": "Metro Harbor 220kV Distribution Hub",
        "location": "Industrial Coastal Hub",
        "capacity_mva": 180,
        "critical_customers": 28500,
        "equipment": {
            "type": "Autotransformer AT-2",
            "mfg_year": 2017,
            "sensor_telemetry": {
                "oil_temperature_c": 78.1,
                "vibration_mms": 2.6,
                "partial_discharge_pc": 290.0,
                "acetylene_ppm": 0.8,
                "ethylene_ppm": 24.0
            }
        },
        "weather": {
            "wind_speed_kmh": 52.0,
            "ambient_temp_c": 31.0,
            "lightning_strikes_10km": 5,
            "precip_mmh": 12.0
        }
    },
    {
        "id": "SUB-WEST-09",
        "name": "Valley Solar Intertie Substation",
        "location": "West Valley Energy Corridor",
        "capacity_mva": 120,
        "critical_customers": 9200,
        "equipment": {
            "type": "Step-up Transformer GSU-1",
            "mfg_year": 2020,
            "sensor_telemetry": {
                "oil_temperature_c": 64.2,
                "vibration_mms": 1.2,
                "partial_discharge_pc": 95.0,
                "acetylene_ppm": 0.1,
                "ethylene_ppm": 8.0
            }
        },
        "weather": {
            "wind_speed_kmh": 24.0,
            "ambient_temp_c": 29.5,
            "lightning_strikes_10km": 0,
            "precip_mmh": 0.0
        }
    }
]

@app.get("/")
def read_root():
    return {
        "service": "GridPulse AI - Power Outage & Equipment Failure Advisor",
        "status": "online",
        "version": "1.0.0",
        "docs_url": "/docs"
    }

@app.get("/api/v1/substations")
def get_all_substations():
    """Returns all substations with computed real-time risk scores."""
    results = []
    for sub in SUBSTATIONS:
        sensor = sub["equipment"]["sensor_telemetry"]
        weather = sub["weather"]
        
        hi = EquipmentRiskEngine.calculate_health_index(sensor)
        stress = EquipmentRiskEngine.calculate_weather_stress(weather)
        risk = EquipmentRiskEngine.evaluate_outage_risk(
            health_index=hi,
            weather_stress=stress,
            critical_customers_count=sub["critical_customers"],
            capacity_mva=sub["capacity_mva"]
        )
        
        results.append({
            "substation_id": sub["id"],
            "name": sub["name"],
            "location": sub["location"],
            "capacity_mva": sub["capacity_mva"],
            "critical_customers": sub["critical_customers"],
            "equipment": sub["equipment"],
            "weather": weather,
            "assessment": risk
        })
    return {"substations": results}

@app.get("/api/v1/prepositioning-plan")
def get_crew_prepositioning_plan():
    """Calculates prioritized emergency maintenance dispatch based on risk rankings."""
    subs_evaluated = []
    for sub in SUBSTATIONS:
        hi = EquipmentRiskEngine.calculate_health_index(sub["equipment"]["sensor_telemetry"])
        stress = EquipmentRiskEngine.calculate_weather_stress(sub["weather"])
        risk = EquipmentRiskEngine.evaluate_outage_risk(
            health_index=hi,
            weather_stress=stress,
            critical_customers_count=sub["critical_customers"],
            capacity_mva=sub["capacity_mva"]
        )
        subs_evaluated.append({
            "substation_id": sub["id"],
            "name": sub["name"],
            "risk": risk
        })

    # Sort descending by Risk Priority Index
    subs_evaluated.sort(key=lambda x: x["risk"]["risk_priority_index"], reverse=True)

    plan = []
    for idx, item in enumerate(subs_evaluated):
        priority = f"Priority {idx + 1}"
        action = item["risk"]["recommended_action"]
        plan.append({
            "rank": idx + 1,
            "priority": priority,
            "substation_id": item["substation_id"],
            "substation_name": item["name"],
            "risk_level": item["risk"]["risk_level"],
            "failure_probability_pct": item["risk"]["failure_probability_pct"],
            "assigned_crew_hub": f"Mobile Rapid Response Unit #{idx+101}",
            "recommended_action": action
        })

    return {
        "generated_timestamp": "2026-09-12T21:15:00Z",
        "total_assets_monitored": len(SUBSTATIONS),
        "prepositioning_plan": plan
    }
