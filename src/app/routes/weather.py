"""
GridPulse AI — Weather Router
Handles /api/v1/weather endpoints.
"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from src.app.database.postgres import get_db
from src.app.services.postgres_service import PostgresService
from src.app.services.integration_service import WeatherAdapter
from src.app.schemas.weather import WeatherListResponse, WeatherDetailResponse

router = APIRouter(prefix="/weather", tags=["Weather"])


@router.get("", response_model=WeatherListResponse)
async def get_all_weather(db: AsyncSession = Depends(get_db)):
    """Returns latest weather readings for all assets with risk scores."""
    svc = PostgresService(db)
    assets, _ = await svc.get_all_assets()

    weather_data = []
    for asset in assets:
        reading = await svc.get_latest_weather(asset.asset_id)
        if reading:
            from src.app.schemas.asset import WeatherReadingResponse
            wr = WeatherReadingResponse.model_validate(reading)
            risk_result = WeatherAdapter.calculate_weather_risk(wr)
            weather_data.append({
                "asset_id": asset.asset_id,
                "asset_name": asset.name,
                "wind_speed": reading.wind_speed,
                "rainfall": reading.rainfall,
                "lightning_probability": reading.lightning_probability,
                "flood_risk": reading.flood_risk,
                "temperature": reading.temperature,
                "weather_risk_score": risk_result["weather_risk_score"],
                "dominant_hazard": risk_result["dominant_hazard"],
                "timestamp": reading.timestamp,
            })

    return WeatherListResponse(weather_data=weather_data, total=len(weather_data))


@router.get("/{asset_id}", response_model=WeatherDetailResponse)
async def get_asset_weather(asset_id: str, db: AsyncSession = Depends(get_db)):
    """Returns weather history and risk for a single asset."""
    svc = PostgresService(db)
    asset = await svc.get_asset(asset_id)
    if not asset:
        raise HTTPException(status_code=404, detail=f"Asset {asset_id} not found")

    reading = await svc.get_latest_weather(asset_id)
    risk_analysis = None
    if reading:
        from src.app.schemas.asset import WeatherReadingResponse
        wr = WeatherReadingResponse.model_validate(reading)
        risk_analysis = WeatherAdapter.calculate_weather_risk(wr)

    return WeatherDetailResponse(
        asset_id=asset_id,
        asset_name=asset.name,
        current=reading.__dict__ if reading else None,
        risk_analysis=risk_analysis
    )
