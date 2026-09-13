"""
GridPulse AI - Weather Risk & Storm-Asset Vulnerability Module

This module calculates the weather-related risk for a grid asset
using wind, rainfall, lightning, flood risk, and temperature.

Output:
    - weather_risk_score
    - dominant_hazard
"""


def calculate_weather_risk(weather):
    """
    Calculate the overall weather risk score for an asset.

    Expected input:
        {
            "wind_speed": float,
            "rainfall": float,
            "lightning_probability": float,
            "flood_risk": float,
            "temperature": float
        }

    Returns:
        {
            "weather_risk_score": float,
            "dominant_hazard": str
        }
    """

    # ---------------------------------------------------------
    # 1. Calculate individual hazard scores
    # ---------------------------------------------------------

    # Wind: 100 km/h or above = maximum risk
    wind_score = min(weather["wind_speed"] / 100, 1.0)

    # Rainfall: 100 mm or above = maximum risk
    rainfall_score = min(weather["rainfall"] / 100, 1.0)

    # Lightning probability: 100% = maximum risk
    lightning_score = min(
        weather["lightning_probability"] / 100,
        1.0
    )

    # Flood risk is already expected as a percentage
    flood_score = min(weather["flood_risk"] / 100, 1.0)

    # ---------------------------------------------------------
    # 2. Calculate temperature risk
    # ---------------------------------------------------------

    temperature = weather["temperature"]

    if temperature >= 45:
        temperature_score = 1.0
    elif temperature >= 40:
        temperature_score = 0.7
    elif temperature <= 0:
        temperature_score = 0.8
    elif temperature <= 5:
        temperature_score = 0.5
    else:
        temperature_score = 0.0

    # ---------------------------------------------------------
    # 3. Store all hazard scores
    # ---------------------------------------------------------

    hazards = {
        "wind": wind_score,
        "rainfall": rainfall_score,
        "lightning": lightning_score,
        "flood": flood_score,
        "temperature": temperature_score,
    }

    # ---------------------------------------------------------
    # 4. Calculate weighted weather-risk score
    # ---------------------------------------------------------

    weather_risk_score = (
        wind_score * 0.25
        + rainfall_score * 0.15
        + lightning_score * 0.25
        + flood_score * 0.20
        + temperature_score * 0.15
    )

    # ---------------------------------------------------------
    # 5. Find the dominant hazard
    # ---------------------------------------------------------

    dominant_hazard = max(
        hazards,
        key=hazards.get
    )

    # ---------------------------------------------------------
    # 6. Return result
    # ---------------------------------------------------------

    return {
        "weather_risk_score": round(weather_risk_score, 2),
        "dominant_hazard": dominant_hazard,
    }


# -------------------------------------------------------------
# Simple local test
# -------------------------------------------------------------

if __name__ == "__main__":

    sample_weather = {
        "wind_speed": 80,
        "rainfall": 60,
        "lightning_probability": 90,
        "flood_risk": 40,
        "temperature": 32,
    }

    result = calculate_weather_risk(sample_weather)

    print("Weather Risk Result:")
    print(result)