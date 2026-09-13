from src.app.core.weather_risk import calculate_weather_risk


def test_high_lightning_risk():
    weather = {
        "wind_speed": 20,
        "rainfall": 10,
        "lightning_probability": 0.9,
        "flood_risk": 0.1,
        "temperature": 30,
    }

    result = calculate_weather_risk(weather)

    assert result["dominant_hazard"] == "lightning"


def test_high_wind_risk():
    weather = {
        "wind_speed": 100,
        "rainfall": 20,
        "lightning_probability": 0.1,
        "flood_risk": 0.1,
        "temperature": 30,
    }

    result = calculate_weather_risk(weather)

    assert result["dominant_hazard"] == "wind"


def test_high_temperature_risk():
    weather = {
        "wind_speed": 10,
        "rainfall": 10,
        "lightning_probability": 0.1,
        "flood_risk": 0.1,
        "temperature": 45,
    }

    result = calculate_weather_risk(weather)

    assert result["dominant_hazard"] == "temperature"


def test_low_weather_risk():
    weather = {
        "wind_speed": 10,
        "rainfall": 5,
        "lightning_probability": 0.05,
        "flood_risk": 0.05,
        "temperature": 30,
    }

    result = calculate_weather_risk(weather)

    assert result["weather_risk_score"] < 0.2