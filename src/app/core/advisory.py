"""
GridPulse AI — Advisory Engine
Combines IBM Granite AI with structured local fallback logic.
Provides asset-level and chat advisory capabilities.
"""
import json
import logging
from typing import Tuple, Dict, Any, Optional

from src.app.core.config import settings
from src.app.core.watsonx_integration import WatsonxClient

logger = logging.getLogger(__name__)

# ─── Local Fallback Logic ─────────────────────────────────────────────────────

def local_fallback_advisory(risk_score: float, asset_name: str, asset=None, sensor=None, dga=None, weather=None, cascade=None) -> Dict[str, Any]:
    """
    Deterministic local advisory when watsonx.ai is unavailable.
    Always labels provider as 'Local Fallback'.
    """
    if risk_score >= 0.85:
        urgency = "IMMEDIATE"
        recommended_actions = [
            "Deploy emergency inspection crew immediately",
            "Pre-position mobile transformer backup unit",
            "Initiate contingency load transfer to adjacent feeders",
            "Alert grid operations center for emergency protocols",
        ]
        potential_consequences = [
            "Equipment failure within 24 hours without intervention",
            "Large-scale power outage affecting downstream customers",
            "Cascade failure to connected feeders and critical facilities",
        ]
    elif risk_score >= 0.70:
        urgency = "URGENT"
        recommended_actions = [
            "Inspect asset within 24 hours",
            "Stage maintenance crew at nearest hub",
            "Increase sensor polling frequency to 1-minute intervals",
        ]
        potential_consequences = [
            "Possible equipment failure within 72 hours",
            "Risk of service interruption during peak load",
        ]
    elif risk_score >= 0.40:
        urgency = "MONITOR"
        recommended_actions = [
            "Enhanced monitoring recommended",
            "Schedule preventive maintenance within 7 days",
            "Review trend data for anomaly patterns",
        ]
        potential_consequences = [
            "Gradual degradation possible without maintenance",
            "Increased failure risk during adverse weather events",
        ]
    else:
        urgency = "ROUTINE"
        recommended_actions = [
            "Continue standard monitoring schedule",
            "Log data for trend analysis",
        ]
        potential_consequences = [
            "No immediate risk identified",
        ]

    # Build risk factors from available readings
    risk_factors = []
    if dga and hasattr(dga, "c2h2") and dga.c2h2 > 3.0:
        risk_factors.append(f"Acetylene at {dga.c2h2:.1f} ppm — active arcing fault (IEEE C57.104 limit: 3 ppm)")
    if sensor and hasattr(sensor, "temperature") and sensor.temperature > 85:
        risk_factors.append(f"Oil temperature at {sensor.temperature:.1f}°C — thermal stress (safe limit: 75°C)")
    if sensor and hasattr(sensor, "partial_discharge") and sensor.partial_discharge > 400:
        risk_factors.append(f"Partial discharge at {sensor.partial_discharge:.0f} pC — insulation degradation")
    if weather and hasattr(weather, "wind_speed") and weather.wind_speed > 60:
        risk_factors.append(f"Wind speed at {weather.wind_speed:.1f} km/h — structural risk")
    if weather and hasattr(weather, "lightning_probability") and weather.lightning_probability > 0.6:
        risk_factors.append(f"Lightning probability at {weather.lightning_probability:.0%} — surge risk")
    if cascade and cascade.get("critical_facility_count", 0) > 0:
        risk_factors.append(f"Cascade failure would impact {cascade['critical_facility_count']} critical facilities")

    if not risk_factors:
        risk_factors = [f"Composite risk score: {risk_score:.2f} ({urgency})"]

    summary = (
        f"{asset_name} is at {urgency} risk level with a composite score of {risk_score:.2f}. "
        f"{'Immediate action is required.' if urgency == 'IMMEDIATE' else 'Timely attention recommended.'}"
    )

    return {
        "summary": summary,
        "risk_factors": risk_factors,
        "potential_consequences": potential_consequences,
        "recommended_actions": recommended_actions,
        "urgency": urgency,
        "provider": "Local Fallback",
    }


# ─── Advisory Engine ──────────────────────────────────────────────────────────

class AdvisoryEngine:
    """
    Orchestrates AI advisory generation.
    Tries IBM Granite first; falls back to local logic if unavailable.
    """

    def __init__(self):
        self.watsonx = WatsonxClient(
            api_key=settings.watsonx_api_key,
            project_id=settings.watsonx_project_id,
            url=settings.watsonx_url,
            model_id=settings.watsonx_model_id,
        )

    def _build_asset_prompt(self, asset, sensor, dga, weather, risk, cascade, question: str) -> str:
        """Build structured context prompt for Granite."""
        risk_score = risk.final_risk_score if risk else 0.5
        risk_level = risk.risk_level if risk else "UNKNOWN"

        sensor_info = ""
        if sensor:
            sensor_info = f"Oil Temperature: {sensor.temperature:.1f}°C, Vibration: {sensor.vibration:.2f} mm/s, Partial Discharge: {sensor.partial_discharge:.0f} pC"

        dga_info = ""
        if dga:
            dga_info = f"H2: {dga.h2:.0f} ppm, CH4: {dga.ch4:.0f} ppm, C2H2: {dga.c2h2:.1f} ppm (arcing indicator), C2H4: {dga.c2h4:.0f} ppm"

        weather_info = ""
        if weather:
            weather_info = f"Wind: {weather.wind_speed:.1f} km/h, Temp: {weather.temperature:.1f}°C, Lightning Prob: {weather.lightning_probability:.0%}, Rainfall: {weather.rainfall:.1f} mm/h"

        cascade_info = ""
        if cascade:
            cascade_info = f"Affected assets: {cascade.get('affected_asset_count', 0)}, Critical facilities: {cascade.get('critical_facility_count', 0)}, Cascade risk: {cascade.get('cascade_risk', 0):.2f}"

        prompt = f"""You are GridPulse AI, an expert power grid risk advisor.

Asset: {asset.name} (ID: {asset.asset_id}, Type: {asset.asset_type})
Risk Level: {risk_level} (Score: {risk_score:.2f})
Sensor Readings: {sensor_info or 'No data'}
DGA Analysis: {dga_info or 'No data'}
Weather Conditions: {weather_info or 'No data'}
Grid Impact: {cascade_info or 'No data'}

Question: {question}

Provide a structured advisory response with:
1. A brief summary of the situation
2. Key risk factors (list)
3. Potential consequences if unaddressed (list)
4. Recommended immediate actions (list)
5. Urgency level: IMMEDIATE / URGENT / MONITOR / ROUTINE

Be concise and technical. Focus on actionable recommendations."""
        return prompt

    def _parse_ai_response(self, text: str, asset_name: str, risk_score: float) -> Dict[str, Any]:
        """Parse Granite's text response into structured format."""
        lines = [l.strip() for l in text.split("\n") if l.strip()]
        summary = lines[0] if lines else f"AI Advisory for {asset_name}"

        # Extract urgency
        urgency = "MONITOR"
        for line in lines:
            upper = line.upper()
            if "IMMEDIATE" in upper:
                urgency = "IMMEDIATE"
                break
            elif "URGENT" in upper:
                urgency = "URGENT"
                break
            elif "ROUTINE" in upper:
                urgency = "ROUTINE"
                break

        # Extract bullet points
        bullets = [
            l.lstrip("-*123456789. ").strip()
            for l in lines
            if l.startswith(("-", "*")) or (len(l) > 2 and l[0].isdigit() and l[1] in ".)")
        ]

        risk_factors = bullets[:3] if len(bullets) >= 3 else [f"Risk score: {risk_score:.2f}"]
        consequences = bullets[3:5] if len(bullets) >= 5 else ["Potential service disruption if unaddressed"]
        actions = bullets[5:8] if len(bullets) >= 8 else ["Contact maintenance crew for assessment"]

        return {
            "summary": summary,
            "risk_factors": risk_factors or [f"Composite risk score: {risk_score:.2f}"],
            "potential_consequences": consequences or ["Service disruption possible"],
            "recommended_actions": actions or ["Consult maintenance team"],
            "urgency": urgency,
            "provider": "IBM Granite",
        }

    async def get_asset_advisory(self, asset, sensor, dga, weather, risk, cascade, question: str) -> Dict[str, Any]:
        """Generate structured advisory for a specific asset."""
        risk_score = risk.final_risk_score if risk else 0.5

        if self.watsonx.is_available():
            try:
                prompt = self._build_asset_prompt(asset, sensor, dga, weather, risk, cascade, question)
                response_text = self.watsonx.generate(prompt, max_tokens=500)
                if response_text:
                    return self._parse_ai_response(response_text, asset.name, risk_score)
            except Exception as e:
                logger.warning(f"Granite generation failed: {e}, using fallback")

        return local_fallback_advisory(
            risk_score=risk_score,
            asset_name=asset.name,
            asset=asset,
            sensor=sensor,
            dga=dga,
            weather=weather,
            cascade=cascade
        )

    async def chat(self, message: str, context_data: Dict) -> Tuple[str, str]:
        """
        Free-form chat advisory.
        Returns (response_text, provider).
        """
        if self.watsonx.is_available():
            try:
                top_risk = context_data.get("top_risk_assets", [])
                context_str = ""
                if top_risk:
                    context_str = "Current grid status:\n" + "\n".join(
                        f"- {a['name']} ({a['asset_id']}): {a['risk_level']} risk"
                        for a in top_risk
                    )

                prompt = f"""You are GridPulse AI, an intelligent power grid risk advisor for a utility company.

{context_str}

User Question: {message}

Provide a helpful, concise answer based on the grid data above. Be specific and actionable."""

                response = self.watsonx.generate(prompt, max_tokens=400)
                if response:
                    return response, "IBM Granite"
            except Exception as e:
                logger.warning(f"Chat generation failed: {e}")

        # Local fallback for chat
        return self._local_chat_response(message, context_data), "Local Fallback"

    def _local_chat_response(self, message: str, context_data: Dict) -> str:
        """Local fallback for chat — rule-based responses."""
        top_risk = context_data.get("top_risk_assets", [])
        message_lower = message.lower()

        if any(w in message_lower for w in ["inspect first", "priority", "most at risk", "worst", "highest risk"]):
            if top_risk:
                top = top_risk[0]
                return (
                    f"Based on current analysis, **{top['name']}** ({top['asset_id']}) "
                    f"is the highest priority with a risk level of **{top['risk_level']}** "
                    f"(score: {top.get('final_risk_score', 'N/A'):.2f}). "
                    "Deploy an inspection crew immediately and consider initiating contingency load transfer."
                )
            return "No risk data available. Please ensure the database is seeded."

        if any(w in message_lower for w in ["critical", "critical_facility", "hospital", "water"]):
            critical_assets = [a for a in top_risk if a.get("risk_level") in ("CRITICAL", "HIGH")]
            if critical_assets:
                names = ", ".join(a["name"] for a in critical_assets[:3])
                return (
                    f"Critical infrastructure risk detected. Assets at HIGH/CRITICAL risk: {names}. "
                    "These assets supply essential services. Immediate inspection and crew pre-positioning recommended."
                )
            return "No critical infrastructure assets currently at elevated risk."

        if any(w in message_lower for w in ["weather", "storm", "wind", "lightning"]):
            return (
                "Weather-related risk is factored into all risk scores. "
                "Assets with wind speeds > 70 km/h, lightning probability > 70%, "
                "or flood risk > 50% receive elevated weather risk scores. "
                "Monitor the Weather Risk page for real-time weather impacts."
            )

        if any(w in message_lower for w in ["maintenance", "crew", "dispatch", "schedule"]):
            if top_risk:
                critical = [a for a in top_risk if a.get("risk_level") == "CRITICAL"]
                high = [a for a in top_risk if a.get("risk_level") == "HIGH"]
                return (
                    f"Maintenance recommendation: {len(critical)} asset(s) require immediate attention, "
                    f"{len(high)} require inspection within 24 hours. "
                    "Visit the Crew & Recommendations page for the full 48-hour staging plan."
                )
            return "Check the Recommendations page for the current crew deployment plan."

        # Generic response
        total = context_data.get("total_assets", 0)
        critical_count = sum(1 for a in top_risk if a.get("risk_level") == "CRITICAL")
        return (
            f"GridPulse AI is monitoring {total} grid assets. "
            f"Currently {critical_count} asset(s) are at CRITICAL risk level. "
            "You can ask me about specific assets, weather risk, critical facilities, or crew deployment. "
            "For detailed analysis, use the POST /api/v1/advisory endpoint with a specific asset ID."
        )
