"""
GridPulse AI — Risk Engine
Computes multi-factor risk scores from PostgreSQL + Neo4j data.
Adapted from the original engine.py, extended with graph impact and DB persistence.
"""
from datetime import datetime, timezone
from typing import Optional, Dict, Any
import logging

from sqlalchemy.ext.asyncio import AsyncSession

from src.app.core.config import settings
from src.app.services.postgres_service import PostgresService

logger = logging.getLogger(__name__)

# Critical facility types and their multipliers
CRITICAL_FACILITY_TYPES = {"hospital", "water_plant", "airport", "data_center"}
IMPORTANT_FACILITY_TYPES = {"school", "fire_station", "police_station"}


def classify_risk_level(score: float) -> str:
    """Classify final risk score into LOW/MEDIUM/HIGH/CRITICAL."""
    if score >= 0.85:
        return "CRITICAL"
    elif score >= 0.70:
        return "HIGH"
    elif score >= 0.40:
        return "MEDIUM"
    else:
        return "LOW"


def get_critical_multiplier(asset) -> float:
    """Returns the critical facility multiplier based on asset attributes."""
    if not asset.critical_facility:
        return settings.multiplier_normal
    ft = (asset.facility_type or "").lower()
    if ft in CRITICAL_FACILITY_TYPES:
        return settings.multiplier_critical
    if ft in IMPORTANT_FACILITY_TYPES:
        return settings.multiplier_important
    return settings.multiplier_important  # default for critical_facility=True


def compute_failure_probability(sensor, dga) -> float:
    """
    Computes failure probability (0-1) from sensor and DGA readings.
    Adapted from EquipmentRiskEngine.calculate_health_index().
    """
    if not sensor and not dga:
        return 0.3  # default moderate risk when no data

    # ── Thermal component (0-0.25) ──────────────────────────────────────────
    temp = sensor.temperature if sensor else 65.0
    if temp <= 65:
        thermal = 0.0
    elif temp <= 85:
        thermal = (temp - 65) / 80.0
    else:
        thermal = 0.25 + min(0.25, (temp - 85) / 40.0)

    # ── Vibration component (0-0.20) ─────────────────────────────────────────
    vib = sensor.vibration if sensor else 1.5
    if vib <= 2.0:
        vib_score = 0.0
    elif vib <= 4.5:
        vib_score = (vib - 2.0) / 12.5
    else:
        vib_score = 0.20 + min(0.10, (vib - 4.5) / 15.0)

    # ── Partial Discharge component (0-0.25) ─────────────────────────────────
    pd = sensor.partial_discharge if sensor else 120.0
    if pd <= 200:
        pd_score = 0.0
    elif pd <= 500:
        pd_score = (pd - 200) / 1200.0
    else:
        pd_score = 0.25 + min(0.25, (pd - 500) / 2000.0)

    # ── DGA component (0-0.30) ───────────────────────────────────────────────
    dga_score = 0.0
    if dga:
        if dga.c2h2 > 3.0:
            dga_score = 0.30  # arcing — critical
        elif dga.c2h2 > 1.0:
            dga_score = 0.20
        elif dga.c2h4 > 50.0:
            dga_score = 0.15  # thermal fault
        elif dga.h2 > 150.0:
            dga_score = 0.10
        else:
            dga_score = 0.0

    total = thermal + vib_score + pd_score + dga_score
    return min(round(total, 3), 1.0)


def compute_asset_health_risk(failure_probability: float) -> float:
    """Converts failure probability into an asset health risk score."""
    return round(failure_probability * 0.9 + 0.05, 3)


def compute_weather_risk(weather) -> float:
    """
    Computes weather risk score (0-1) from WeatherReading.
    Adapted from EquipmentRiskEngine.calculate_weather_stress().
    """
    if not weather:
        return 0.1

    risk = 0.0

    # Wind
    if weather.wind_speed > 70:
        risk += 0.35
    elif weather.wind_speed > 45:
        risk += 0.20

    # Temperature
    if weather.temperature > 40:
        risk += 0.30
    elif weather.temperature > 35:
        risk += 0.15

    # Lightning probability
    if weather.lightning_probability > 0.7:
        risk += 0.25
    elif weather.lightning_probability > 0.4:
        risk += 0.15

    # Rainfall / flood
    if weather.rainfall > 30 or weather.flood_risk > 0.5:
        risk += 0.20
    elif weather.rainfall > 15 or weather.flood_risk > 0.3:
        risk += 0.10

    return min(round(risk, 3), 1.0)


class RiskEngine:
    """
    Orchestrates risk score calculation across PostgreSQL and Neo4j.
    Reads sensor/DGA/weather data → computes components → saves to DB.
    """

    def __init__(self, db: AsyncSession, neo4j_svc):
        self.db = db
        self.neo4j_svc = neo4j_svc
        self.pg_svc = PostgresService(db)

    async def compute_risk(self, asset_id: str) -> Dict[str, Any]:
        """
        Full risk computation pipeline:
        1. Fetch asset + latest readings from PostgreSQL
        2. Fetch graph impact from Neo4j
        3. Apply weighted formula
        4. Persist and return RiskScore
        """
        # 1. Fetch data
        asset = await self.pg_svc.get_asset(asset_id)
        if not asset:
            raise ValueError(f"Asset {asset_id} not found")

        sensor = await self.pg_svc.get_latest_sensor(asset_id)
        dga = await self.pg_svc.get_latest_dga(asset_id)
        weather = await self.pg_svc.get_latest_weather(asset_id)

        # 2. Compute component scores
        failure_prob = compute_failure_probability(sensor, dga)
        asset_health_risk = compute_asset_health_risk(failure_prob)
        weather_risk = compute_weather_risk(weather)

        # 3. Graph impact from Neo4j
        try:
            grid_impact = await self.neo4j_svc.calculate_graph_impact(asset_id)
            cascade_risk = await self._compute_cascade_risk(asset_id)
        except Exception as e:
            logger.warning(f"Neo4j unavailable for {asset_id}, using defaults: {e}")
            grid_impact = 0.3
            cascade_risk = 0.2

        # 4. Apply weighted formula
        critical_multiplier = get_critical_multiplier(asset)

        base_risk = (
            settings.weight_failure_probability * failure_prob
            + settings.weight_asset_health * asset_health_risk
            + settings.weight_weather * weather_risk
            + settings.weight_grid_impact * grid_impact
            + settings.weight_cascade * cascade_risk
        )

        final_risk_score = min(round(base_risk * critical_multiplier, 4), 1.0)
        risk_level = classify_risk_level(final_risk_score)

        # 5. Persist to PostgreSQL
        score_data = {
            "asset_id": asset_id,
            "timestamp": datetime.now(timezone.utc),
            "failure_probability": failure_prob,
            "asset_health_risk": asset_health_risk,
            "weather_risk": weather_risk,
            "grid_impact": grid_impact,
            "cascade_risk": cascade_risk,
            "critical_multiplier": critical_multiplier,
            "final_risk_score": final_risk_score,
            "risk_level": risk_level,
        }
        await self.pg_svc.save_risk_score(score_data)

        return {
            **score_data,
            "asset_name": asset.name,
            "asset_type": asset.asset_type.value if hasattr(asset.asset_type, "value") else asset.asset_type,
            "timestamp": score_data["timestamp"].isoformat(),
        }

    async def _compute_cascade_risk(self, asset_id: str) -> float:
        """Compute cascade risk via Neo4j downstream analysis."""
        from src.app.core.graph_scoring import CascadeAnalyzer
        try:
            analyzer = CascadeAnalyzer(self.neo4j_svc)
            result = await analyzer.analyze_cascade(asset_id)
            return result.get("cascade_risk", 0.2) if result else 0.2
        except Exception:
            return 0.2
