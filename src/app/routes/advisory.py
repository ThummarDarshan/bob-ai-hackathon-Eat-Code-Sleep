"""
GridPulse AI — Advisory Router
Handles /api/v1/advisory endpoints.
"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from datetime import datetime, timezone

from src.app.database.postgres import get_db
from src.app.schemas.advisory import (
    AdvisoryRequest, AdvisoryResponse, ChatRequest, ChatResponse
)
from src.app.services.postgres_service import PostgresService
from src.app.core.advisory import AdvisoryEngine

router = APIRouter(prefix="/advisory", tags=["Advisory"])


@router.post("/chat", response_model=ChatResponse)
async def advisory_chat(request: ChatRequest, db: AsyncSession = Depends(get_db)):
    """Free-form chat with the AI grid advisor."""
    svc = PostgresService(db)
    engine = AdvisoryEngine()

    # Build context from current backend data
    assets, _ = await svc.get_all_assets()
    top_risk = []
    for asset in assets[:5]:
        risk = await svc.get_latest_risk(asset.asset_id)
        if risk:
            top_risk.append({
                "asset_id": asset.asset_id,
                "name": asset.name,
                "risk_level": risk.risk_level,
                "final_risk_score": risk.final_risk_score
            })

    context_data = {
        "top_risk_assets": top_risk,
        "total_assets": len(assets),
        "user_context": request.context
    }

    response_text, provider = await engine.chat(request.message, context_data)

    return ChatResponse(
        response=response_text,
        provider=provider,
        timestamp=datetime.now(timezone.utc)
    )


@router.post("", response_model=AdvisoryResponse)
async def get_asset_advisory(
    request: AdvisoryRequest,
    db: AsyncSession = Depends(get_db)
):
    """Ask the AI advisor about a specific asset."""
    svc = PostgresService(db)

    asset = await svc.get_asset(request.asset_id)
    if not asset:
        raise HTTPException(status_code=404, detail=f"Asset {request.asset_id} not found")

    sensor = await svc.get_latest_sensor(request.asset_id)
    dga = await svc.get_latest_dga(request.asset_id)
    weather = await svc.get_latest_weather(request.asset_id)
    risk = await svc.get_latest_risk(request.asset_id)

    # Fetch cascade analysis from Neo4j
    cascade_data = {}
    try:
        from src.app.database.neo4j import get_neo4j_session
        from src.app.services.neo4j_service import Neo4jService
        from src.app.core.graph_scoring import CascadeAnalyzer
        async with get_neo4j_session() as neo4j_session:
            neo4j_svc = Neo4jService(neo4j_session)
            analyzer = CascadeAnalyzer(neo4j_svc)
            cascade_data = await analyzer.analyze_cascade(request.asset_id) or {}
    except Exception:
        pass

    engine = AdvisoryEngine()
    advisory = await engine.get_asset_advisory(
        asset=asset,
        sensor=sensor,
        dga=dga,
        weather=weather,
        risk=risk,
        cascade=cascade_data,
        question=request.question
    )

    # Persist advisory record
    await svc.save_advisory(
        asset_id=request.asset_id,
        question=request.question,
        response=str(advisory),
        provider=advisory.get("provider", "Local Fallback")
    )

    return AdvisoryResponse(
        asset_id=request.asset_id,
        question=request.question,
        summary=advisory.get("summary", ""),
        risk_factors=advisory.get("risk_factors", []),
        potential_consequences=advisory.get("potential_consequences", []),
        recommended_actions=advisory.get("recommended_actions", []),
        urgency=advisory.get("urgency", "ROUTINE"),
        provider=advisory.get("provider", "Local Fallback"),
        created_at=datetime.now(timezone.utc)
    )
