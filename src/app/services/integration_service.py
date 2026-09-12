"""
GridPulse AI — Module Integration Adapters
Bridges DGA analysis (IEEE C57.104) and Weather risk calculation
into the risk orchestration engine.
"""
from typing import Dict, Any, List, Optional
from dataclasses import dataclass


# ─── DGA Adapter ─────────────────────────────────────────────────────────────

class DGAAdapter:
    """
    Dissolved Gas Analysis fault classifier using IEEE C57.104 Rogers Ratio method.
    Classifies transformer faults based on dissolved gas concentrations.
    """

    FAULT_TYPES = {
        "NORMAL": "No significant fault detected",
        "THERMAL_LOW": "Low-temperature thermal fault (< 300°C) — overloaded cellulose",
        "THERMAL_HIGH": "High-temperature thermal fault (> 700°C) — oil pyrolysis",
        "ARCING": "High-energy electrical arcing — immediate intervention required",
        "PARTIAL_DISCHARGE": "Partial discharge in gas or oil voids",
        "MULTIPLE_FAULT": "Multiple concurrent fault types detected",
    }

    @staticmethod
    def classify_fault_type(dga) -> Dict[str, Any]:
        """
        Classify fault type using IEEE C57.104 Rogers Ratio method.
        
        Rogers Ratios:
          R1 = CH4/H2
          R2 = C2H2/C2H4
          R3 = C2H4/C2H6
        
        Args:
            dga: DGAReading object or dict with gas values.
            
        Returns:
            dict with fault_type, severity, ratios, description
        """
        # Handle both ORM objects and dicts
        if hasattr(dga, "c2h2"):
            h2 = dga.h2 or 0.001
            ch4 = dga.ch4 or 0.001
            c2h2 = dga.c2h2 or 0.001
            c2h4 = dga.c2h4 or 0.001
            c2h6 = dga.c2h6 or 0.001
            co = dga.co or 0.001
        else:
            h2 = dga.get("h2", 0.001) or 0.001
            ch4 = dga.get("ch4", 0.001) or 0.001
            c2h2 = dga.get("c2h2", 0.001) or 0.001
            c2h4 = dga.get("c2h4", 0.001) or 0.001
            c2h6 = dga.get("c2h6", 0.001) or 0.001
            co = dga.get("co", 0.001) or 0.001

        # Compute Rogers Ratios
        r1 = ch4 / h2        # CH4/H2
        r2 = c2h2 / c2h4     # C2H2/C2H4
        r3 = c2h4 / c2h6     # C2H4/C2H6

        ratios = {
            "R1_CH4_H2": round(r1, 4),
            "R2_C2H2_C2H4": round(r2, 4),
            "R3_C2H4_C2H6": round(r3, 4),
        }

        # IEEE C57.104 classification
        fault_type = "NORMAL"
        severity = "low"
        faults_found = []

        # Arcing: C2H2 > 3 ppm
        if c2h2 > 3.0:
            faults_found.append("ARCING")
        elif c2h2 > 1.0:
            faults_found.append("PARTIAL_DISCHARGE")

        # High thermal: C2H4 > 50 ppm
        if c2h4 > 50.0:
            faults_found.append("THERMAL_HIGH")
        elif c2h4 > 20.0:
            faults_found.append("THERMAL_LOW")

        # Hydrogen fault
        if h2 > 150:
            faults_found.append("PARTIAL_DISCHARGE")

        if len(faults_found) > 1:
            fault_type = "MULTIPLE_FAULT"
            severity = "critical"
        elif len(faults_found) == 1:
            fault_type = faults_found[0]
            if fault_type == "ARCING":
                severity = "critical"
            elif fault_type == "THERMAL_HIGH":
                severity = "high"
            elif fault_type in ("THERMAL_LOW", "PARTIAL_DISCHARGE"):
                severity = "medium"
        else:
            fault_type = "NORMAL"
            severity = "low"

        return {
            "fault_type": fault_type,
            "severity": severity,
            "ratios": ratios,
            "description": DGAAdapter.FAULT_TYPES.get(fault_type, "Unknown fault type"),
            "key_gases": {
                "h2_ppm": round(h2, 2),
                "c2h2_ppm": round(c2h2, 2),
                "c2h4_ppm": round(c2h4, 2),
                "ch4_ppm": round(ch4, 2),
            }
        }


# ─── Weather Adapter ──────────────────────────────────────────────────────────

class WeatherAdapter:
    """
    Weather risk calculator and crew positioning planner.
    Bridges weather readings into the risk engine.
    """

    @staticmethod
    def calculate_weather_risk(weather) -> Dict[str, Any]:
        """
        Calculate weather risk score and identify dominant hazard.
        
        Args:
            weather: WeatherReading object or dict.
            
        Returns:
            dict with weather_risk_score (0-1), risk_factors, dominant_hazard
        """
        if hasattr(weather, "wind_speed"):
            wind = weather.wind_speed or 0.0
            rain = weather.rainfall or 0.0
            lightning = weather.lightning_probability or 0.0
            flood = weather.flood_risk or 0.0
            temp = weather.temperature or 25.0
        else:
            wind = weather.get("wind_speed", 0.0) or 0.0
            rain = weather.get("rainfall", 0.0) or 0.0
            lightning = weather.get("lightning_probability", 0.0) or 0.0
            flood = weather.get("flood_risk", 0.0) or 0.0
            temp = weather.get("temperature", 25.0) or 25.0

        scores = {}
        risk_factors = []

        # Wind risk
        if wind > 70:
            scores["wind"] = 0.35
            risk_factors.append(f"Severe wind: {wind:.1f} km/h (threshold: 70 km/h)")
        elif wind > 45:
            scores["wind"] = 0.20
            risk_factors.append(f"Elevated wind: {wind:.1f} km/h")
        else:
            scores["wind"] = 0.0

        # Temperature risk
        if temp > 40:
            scores["heat"] = 0.30
            risk_factors.append(f"Extreme heat: {temp:.1f}°C (threshold: 40°C)")
        elif temp > 35:
            scores["heat"] = 0.15
            risk_factors.append(f"High temperature: {temp:.1f}°C")
        else:
            scores["heat"] = 0.0

        # Lightning risk
        if lightning > 0.7:
            scores["lightning"] = 0.25
            risk_factors.append(f"High lightning probability: {lightning:.0%}")
        elif lightning > 0.4:
            scores["lightning"] = 0.15
            risk_factors.append(f"Moderate lightning probability: {lightning:.0%}")
        else:
            scores["lightning"] = 0.0

        # Flood/rain risk
        if rain > 30 or flood > 0.5:
            scores["flood"] = 0.20
            risk_factors.append(f"Flood/heavy rain risk: {rain:.1f} mm/h, flood: {flood:.0%}")
        elif rain > 15 or flood > 0.3:
            scores["flood"] = 0.10
            risk_factors.append(f"Moderate rainfall: {rain:.1f} mm/h")
        else:
            scores["flood"] = 0.0

        total_risk = min(sum(scores.values()), 1.0)

        # Dominant hazard
        if scores:
            dominant_hazard = max(scores, key=scores.get)
        else:
            dominant_hazard = "none"

        return {
            "weather_risk_score": round(total_risk, 3),
            "risk_factors": risk_factors,
            "dominant_hazard": dominant_hazard,
            "component_scores": scores,
        }

    @staticmethod
    def generate_crew_positioning(assets_with_risk: List[Dict]) -> Dict[str, Any]:
        """
        Generate a 48-hour crew staging plan based on risk-ranked assets.
        
        Args:
            assets_with_risk: list of dicts with asset_id, name, risk_level, final_risk_score
            
        Returns:
            dict with crew_hubs, deployment_schedule, asset_assignments
        """
        # Sort by risk score descending
        sorted_assets = sorted(
            assets_with_risk,
            key=lambda x: x.get("final_risk_score", 0),
            reverse=True
        )

        crew_hubs = [
            {"hub_id": "HUB-NORTH", "name": "North Operations Center", "capacity": 3},
            {"hub_id": "HUB-EAST",  "name": "East Metro Depot",        "capacity": 2},
            {"hub_id": "HUB-WEST",  "name": "West Valley Station",     "capacity": 2},
        ]

        deployment_schedule = []
        asset_assignments = []

        for idx, asset in enumerate(sorted_assets):
            risk_level = asset.get("risk_level", "LOW")
            asset_id = asset.get("asset_id", "")
            asset_name = asset.get("asset_name", asset.get("name", asset_id))

            if risk_level == "CRITICAL":
                deploy_within = "Immediately (0-2 hours)"
                crew_count = 3
                hub = crew_hubs[0]["name"]
            elif risk_level == "HIGH":
                deploy_within = "Within 24 hours"
                crew_count = 2
                hub = crew_hubs[1]["name"]
            elif risk_level == "MEDIUM":
                deploy_within = "Within 48 hours"
                crew_count = 1
                hub = crew_hubs[2]["name"]
            else:
                deploy_within = "Routine schedule"
                crew_count = 1
                hub = "Local depot"

            assignment = {
                "rank": idx + 1,
                "asset_id": asset_id,
                "asset_name": asset_name,
                "risk_level": risk_level,
                "final_risk_score": asset.get("final_risk_score", 0),
                "staging_hub": hub,
                "crew_count": crew_count,
                "deploy_within": deploy_within,
            }
            asset_assignments.append(assignment)

            if risk_level in ("CRITICAL", "HIGH"):
                deployment_schedule.append({
                    "time_window": f"T+{'0' if risk_level == 'CRITICAL' else '24'}h",
                    "asset_id": asset_id,
                    "action": f"Dispatch {crew_count} crew from {hub} to {asset_name}",
                    "priority": risk_level,
                })

        return {
            "crew_hubs": crew_hubs,
            "deployment_schedule": deployment_schedule,
            "asset_assignments": asset_assignments,
            "total_assets": len(sorted_assets),
            "crews_required": sum(a["crew_count"] for a in asset_assignments if a["risk_level"] in ("CRITICAL", "HIGH")),
        }
