"""
GridPulse AI — PostgreSQL Service Layer
All database operations via SQLAlchemy async ORM.
"""
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, desc
from typing import Optional, List, Tuple
from datetime import datetime, timezone

from src.app.models.asset import Asset
from src.app.models.sensor import SensorReading, DGAReading
from src.app.models.weather import WeatherReading
from src.app.models.incident import Incident
from src.app.models.risk import RiskScore, WorkOrder, AIAdvisory
from src.app.schemas.asset import (
    AssetResponse, SensorReadingResponse, DGAReadingResponse,
    WeatherReadingResponse, IncidentResponse, AssetDetailResponse
)
from src.app.schemas.risk import WorkOrderCreate, WorkOrderUpdate, WorkOrderResponse


class PostgresService:
    def __init__(self, db: AsyncSession):
        self.db = db

    # ─── Assets ────────────────────────────────────────────────────────────────

    async def get_all_assets(
        self,
        risk_level: Optional[str] = None,
        asset_type: Optional[str] = None,
        limit: int = 100,
        offset: int = 0
    ) -> Tuple[List[AssetResponse], int]:
        stmt = select(Asset)
        if asset_type:
            stmt = stmt.where(Asset.asset_type == asset_type)
        count_stmt = select(func.count()).select_from(stmt.subquery())
        total = (await self.db.execute(count_stmt)).scalar_one()
        stmt = stmt.offset(offset).limit(limit)
        result = await self.db.execute(stmt)
        assets = result.scalars().all()

        responses = []
        for asset in assets:
            risk = await self.get_latest_risk(asset.asset_id)
            ar = AssetResponse.model_validate(asset)
            if risk:
                if risk_level and risk.risk_level != risk_level:
                    continue
                ar.risk_level = risk.risk_level
                ar.final_risk_score = risk.final_risk_score
            responses.append(ar)

        return responses, total

    async def get_asset(self, asset_id: str) -> Optional[Asset]:
        result = await self.db.execute(
            select(Asset).where(Asset.asset_id == asset_id)
        )
        return result.scalar_one_or_none()

    async def get_asset_detail(self, asset_id: str) -> Optional[AssetDetailResponse]:
        asset = await self.get_asset(asset_id)
        if not asset:
            return None

        sensor = await self.get_latest_sensor(asset_id)
        dga = await self.get_latest_dga(asset_id)
        weather = await self.get_latest_weather(asset_id)
        risk = await self.get_latest_risk(asset_id)

        result = await self.db.execute(
            select(Incident)
            .where(Incident.asset_id == asset_id)
            .order_by(desc(Incident.timestamp))
            .limit(10)
        )
        incidents_raw = result.scalars().all()

        ar = AssetResponse.model_validate(asset)
        if risk:
            ar.risk_level = risk.risk_level
            ar.final_risk_score = risk.final_risk_score

        return AssetDetailResponse(
            asset=ar,
            latest_sensor=SensorReadingResponse.model_validate(sensor) if sensor else None,
            latest_dga=DGAReadingResponse.model_validate(dga) if dga else None,
            latest_weather=WeatherReadingResponse.model_validate(weather) if weather else None,
            latest_risk=risk.__dict__ if risk else None,
            incidents=[IncidentResponse.model_validate(i) for i in incidents_raw]
        )

    # ─── Sensor Readings ───────────────────────────────────────────────────────

    async def get_latest_sensor(self, asset_id: str) -> Optional[SensorReading]:
        result = await self.db.execute(
            select(SensorReading)
            .where(SensorReading.asset_id == asset_id)
            .order_by(desc(SensorReading.timestamp))
            .limit(1)
        )
        return result.scalar_one_or_none()

    # ─── DGA Readings ──────────────────────────────────────────────────────────

    async def get_latest_dga(self, asset_id: str) -> Optional[DGAReading]:
        result = await self.db.execute(
            select(DGAReading)
            .where(DGAReading.asset_id == asset_id)
            .order_by(desc(DGAReading.timestamp))
            .limit(1)
        )
        return result.scalar_one_or_none()

    # ─── Weather Readings ──────────────────────────────────────────────────────

    async def get_latest_weather(self, asset_id: str) -> Optional[WeatherReading]:
        result = await self.db.execute(
            select(WeatherReading)
            .where(WeatherReading.asset_id == asset_id)
            .order_by(desc(WeatherReading.timestamp))
            .limit(1)
        )
        return result.scalar_one_or_none()

    # ─── Risk Scores ───────────────────────────────────────────────────────────

    async def get_latest_risk(self, asset_id: str) -> Optional[RiskScore]:
        result = await self.db.execute(
            select(RiskScore)
            .where(RiskScore.asset_id == asset_id)
            .order_by(desc(RiskScore.timestamp))
            .limit(1)
        )
        return result.scalar_one_or_none()

    async def save_risk_score(self, score_data: dict) -> RiskScore:
        score = RiskScore(
            asset_id=score_data["asset_id"],
            timestamp=score_data.get("timestamp", datetime.now(timezone.utc)),
            failure_probability=score_data["failure_probability"],
            asset_health_risk=score_data["asset_health_risk"],
            weather_risk=score_data["weather_risk"],
            grid_impact=score_data["grid_impact"],
            cascade_risk=score_data["cascade_risk"],
            critical_multiplier=score_data["critical_multiplier"],
            final_risk_score=score_data["final_risk_score"],
            risk_level=score_data["risk_level"],
        )
        self.db.add(score)
        await self.db.flush()
        return score

    # ─── Work Orders ───────────────────────────────────────────────────────────

    async def get_workorders(self, asset_id: str) -> List[WorkOrderResponse]:
        result = await self.db.execute(
            select(WorkOrder)
            .where(WorkOrder.asset_id == asset_id)
            .order_by(desc(WorkOrder.id))
        )
        wos = result.scalars().all()
        return [WorkOrderResponse.model_validate(wo) for wo in wos]

    async def create_workorder(self, data: WorkOrderCreate) -> WorkOrderResponse:
        wo = WorkOrder(
            asset_id=data.asset_id,
            priority=data.priority,
            description=data.description,
            assigned_crew=data.assigned_crew,
            scheduled_time=data.scheduled_time,
            status="pending"
        )
        self.db.add(wo)
        await self.db.flush()
        await self.db.refresh(wo)
        return WorkOrderResponse.model_validate(wo)

    async def update_workorder(self, workorder_id: int, data: WorkOrderUpdate) -> Optional[WorkOrderResponse]:
        result = await self.db.execute(select(WorkOrder).where(WorkOrder.id == workorder_id))
        wo = result.scalar_one_or_none()
        if not wo:
            return None
        if data.status is not None:
            wo.status = data.status
        if data.assigned_crew is not None:
            wo.assigned_crew = data.assigned_crew
        if data.scheduled_time is not None:
            wo.scheduled_time = data.scheduled_time
        if data.description is not None:
            wo.description = data.description
        await self.db.flush()
        await self.db.refresh(wo)
        return WorkOrderResponse.model_validate(wo)

    async def count_workorders_by_status(self, status: str) -> int:
        result = await self.db.execute(
            select(func.count()).select_from(WorkOrder).where(WorkOrder.status == status)
        )
        return result.scalar_one()

    # ─── Incidents ─────────────────────────────────────────────────────────────

    async def get_recent_incidents(self, limit: int = 5) -> List[dict]:
        result = await self.db.execute(
            select(Incident)
            .order_by(desc(Incident.timestamp))
            .limit(limit)
        )
        incidents = result.scalars().all()
        return [
            {
                "id": i.id,
                "asset_id": i.asset_id,
                "timestamp": i.timestamp.isoformat() if i.timestamp else None,
                "failure_type": i.failure_type,
                "severity": i.severity,
                "description": i.description,
            }
            for i in incidents
        ]

    # ─── Advisory ──────────────────────────────────────────────────────────────

    async def save_advisory(self, asset_id: str, question: str, response: str, provider: str):
        advisory = AIAdvisory(
            asset_id=asset_id,
            question=question,
            response=response,
            provider=provider,
            created_at=datetime.now(timezone.utc)
        )
        self.db.add(advisory)
        await self.db.flush()
        return advisory
