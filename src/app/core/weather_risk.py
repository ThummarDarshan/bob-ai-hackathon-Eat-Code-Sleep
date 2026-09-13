"""
GridPulse AI - Weather Risk & Storm-Asset Vulnerability Module

Calculates weather-related risk for a grid asset using:
- Wind
- Rainfall
- Lightning probability
- Flood risk
- Temperature extremes
"""


def calculate_weather_risk(weather):
    """
    Calculate the overall weather risk score.

    Expected input:
        {
            "wind_speed": float,              # km/h
            "rainfall": float,                # mm/h
            "lightning_probability": float,   # 0-1
            "flood_risk": float,              # 0-1
            "temperature": float              # Celsius
        }

    Returns:
        {
            "weather_risk_score": float,
            "dominant_hazard": str
        }
    """

    # Normalize weather hazards to a 0-1 risk scale

    # Contract threshold: >70 km/h is high risk
    wind_score = min(weather["wind_speed"] / 70, 1.0)

    # Contract threshold: >30 mm/h is high risk
    rainfall_score = min(weather["rainfall"] / 30, 1.0)

    # Contract already provides this as 0-1
    lightning_score = min(max(weather["lightning_probability"], 0.0), 1.0)

    # Contract already provides this as 0-1
    flood_score = min(max(weather["flood_risk"], 0.0), 1.0)

    temperature = weather["temperature"]

    # Temperature extremes
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

    hazards = {
        "wind": wind_score,
        "rainfall": rainfall_score,
        "lightning": lightning_score,
        "flood": flood_score,
        "temperature": temperature_score,
    }

    # Overall weather-risk weighting
    weather_risk_score = (
        wind_score * 0.25
        + rainfall_score * 0.15
        + lightning_score * 0.25
        + flood_score * 0.20
        + temperature_score * 0.15
    )

    dominant_hazard = max(
        hazards,
        key=hazards.get
    )

    return {
        "weather_risk_score": round(weather_risk_score, 2),
        "dominant_hazard": dominant_hazard,
    }


if __name__ == "__main__":

    sample_weather = {
        "wind_speed": 68.5,
        "rainfall": 22.0,
        "lightning_probability": 0.75,
        "flood_risk": 0.3,
        "temperature": 38.2,
    }

    result = calculate_weather_risk(sample_weather)

    print("Weather Risk Result:")
    print(result)