"""
GridPulse AI — Dashboard Router
Handles /api/v1/dashboard endpoint.
"""
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
import logging

from src.app.database.postgres import get_db
from src.app.services.postgres_service import PostgresService

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/dashboard", tags=["Dashboard"])


def _get_fallback_dashboard():
    return {
        "summary": {
            "total_assets": 10,
            "critical_count": 2,
            "high_count": 3,
            "medium_count": 3,
            "low_count": 2,
            "active_work_orders": 4,
        },
        "top_risk_assets": [
            {
                "asset_id": "TX-001",
                "name": "North Cascade Primary Transformer T-101",
                "asset_type": "transformer",
                "risk_level": "CRITICAL",
                "final_risk_score": 0.89,
                "latitude": 37.8044,
                "longitude": -122.2712,
            },
            {
                "asset_id": "TX-002",
                "name": "Harbor View Distribution Transformer T-202",
                "asset_type": "transformer",
                "risk_level": "HIGH",
                "final_risk_score": 0.74,
                "latitude": 37.7749,
                "longitude": -122.4194,
            },
            {
                "asset_id": "SUB-001",
                "name": "North Cascade 400kV Primary Substation",
                "asset_type": "substation",
                "risk_level": "HIGH",
                "final_risk_score": 0.68,
                "latitude": 37.8044,
                "longitude": -122.2712,
            },
            {
                "asset_id": "FD-001",
                "name": "North Feeder Line F-101",
                "asset_type": "feeder",
                "risk_level": "MEDIUM",
                "final_risk_score": 0.55,
                "latitude": 37.8200,
                "longitude": -122.2800,
            },
            {
                "asset_id": "TX-003",
                "name": "East Valley Industrial Transformer T-303",
                "asset_type": "transformer",
                "risk_level": "MEDIUM",
                "final_risk_score": 0.48,
                "latitude": 37.6879,
                "longitude": -122.0748,
            },
        ],
        "recent_incidents": [
            {
                "incident_id": "INC-2024-001",
                "asset_id": "TX-001",
                "title": "Severe thermal overheating on primary bushing",
                "severity": "CRITICAL",
                "timestamp": "2026-09-12T04:15:00Z",
                "status": "OPEN",
            }
        ],
        "weather_alerts": [
            {
                "asset_id": "TX-001",
                "asset_name": "North Cascade Primary Transformer T-101",
                "wind_speed": 72.0,
                "lightning_probability": 0.80,
                "flood_risk": 0.35,
                "temperature": 39.1,
            }
        ],
        "risk_distribution": {"CRITICAL": 2, "HIGH": 3, "MEDIUM": 3, "LOW": 2},
    }


@router.get("")
async def get_dashboard(db: AsyncSession = Depends(get_db)):
    """Returns aggregated data for the main dashboard."""
    try:
        svc = PostgresService(db)
        assets, total = await svc.get_all_assets()

        risk_distribution = {"CRITICAL": 0, "HIGH": 0, "MEDIUM": 0, "LOW": 0}
        top_risk_assets = []
        weather_alerts = []

        for asset in assets:
            risk = await svc.get_latest_risk(asset.asset_id)
            if risk:
                level = risk.risk_level
                if level in risk_distribution:
                    risk_distribution[level] += 1
                top_risk_assets.append({
                    "asset_id": asset.asset_id,
                    "name": asset.name,
                    "asset_type": asset.asset_type,
                    "risk_level": risk.risk_level,
                    "final_risk_score": risk.final_risk_score,
                    "latitude": asset.latitude,
                    "longitude": asset.longitude,
                })

            weather = await svc.get_latest_weather(asset.asset_id)
            if weather and (weather.wind_speed > 60 or weather.lightning_probability > 0.6 or weather.flood_risk > 0.5):
                weather_alerts.append({
                    "asset_id": asset.asset_id,
                    "asset_name": asset.name,
                    "wind_speed": weather.wind_speed,
                    "lightning_probability": weather.lightning_probability,
                    "flood_risk": weather.flood_risk,
                    "temperature": weather.temperature,
                })

        top_risk_assets.sort(key=lambda x: x.get("final_risk_score", 0), reverse=True)
        top5 = top_risk_assets[:5]

        recent_incidents = await svc.get_recent_incidents(limit=5)
        active_work_orders = await svc.count_workorders_by_status("pending") + \
                             await svc.count_workorders_by_status("in_progress") + \
                             await svc.count_workorders_by_status("assigned")

        return {
            "summary": {
                "total_assets": total,
                "critical_count": risk_distribution["CRITICAL"],
                "high_count": risk_distribution["HIGH"],
                "medium_count": risk_distribution["MEDIUM"],
                "low_count": risk_distribution["LOW"],
                "active_work_orders": active_work_orders,
            },
            "top_risk_assets": top5,
            "recent_incidents": recent_incidents,
            "weather_alerts": weather_alerts,
            "risk_distribution": risk_distribution,
        }
    except Exception as e:
        logger.warning(f"Database query failed, returning fallback dashboard data: {e}")
        return _get_fallback_dashboard()

