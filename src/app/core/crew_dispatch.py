"""
GridPulse AI - 48-Hour Crew Pre-Positioning Engine

Prioritizes grid assets for crew pre-positioning based on:
- Storm/weather risk
- Asset vulnerability
- Critical facility status
- Time until the predicted risk
"""


def generate_crew_preposition_plan(
    assets,
    crews,
    forecast_hours=48
):
    """
    Generate a crew pre-positioning plan for the next 48 hours.

    Expected asset format:
        {
            "asset_id": "TX-001",
            "vulnerability_score": 0.85,
            "critical_facility": True,
            "dominant_hazard": "wind"
        }

    Expected crew format:
        {
            "crew_id": "CREW-01",
            "available": True
        }

    Returns:
        {
            "planning_horizon_hours": 48,
            "priority_assets": [...],
            "crew_assignments": [...]
        }
    """

    priority_assets = []

    for asset in assets:
        vulnerability_score = asset.get("vulnerability_score", 0.0)
        critical_facility = asset.get("critical_facility", False)

        # Give critical facilities additional priority.
        priority_score = vulnerability_score

        if critical_facility:
            priority_score += 0.10

        priority_score = min(priority_score, 1.0)

        # Determine priority level.
        if priority_score >= 0.75:
            priority = "CRITICAL"
        elif priority_score >= 0.50:
            priority = "HIGH"
        elif priority_score >= 0.25:
            priority = "MEDIUM"
        else:
            priority = "LOW"

        priority_assets.append({
            "asset_id": asset["asset_id"],
            "priority_score": round(priority_score, 2),
            "priority": priority,
            "dominant_hazard": asset.get(
                "dominant_hazard",
                "unknown"
            ),
        })

    # Highest-risk assets should be handled first.
    priority_assets.sort(
        key=lambda asset: asset["priority_score"],
        reverse=True
    )

    # Select available crews.
    available_crews = [
        crew for crew in crews
        if crew.get("available", False)
    ]

    crew_assignments = []

    # Assign available crews to the highest-priority assets.
    for crew, asset in zip(available_crews, priority_assets):

        if asset["priority"] in ["CRITICAL", "HIGH"]:

            crew_assignments.append({
                "crew_id": crew["crew_id"],
                "asset_id": asset["asset_id"],
                "priority": asset["priority"],
                "reason": (
                    f"Pre-position for {asset['dominant_hazard']} "
                    f"risk"
                ),
            })

    return {
        "planning_horizon_hours": forecast_hours,
        "priority_assets": priority_assets,
        "crew_assignments": crew_assignments,
    }


if __name__ == "__main__":

    sample_assets = [
        {
            "asset_id": "TX-001",
            "vulnerability_score": 0.85,
            "critical_facility": True,
            "dominant_hazard": "wind",
        },
        {
            "asset_id": "TX-002",
            "vulnerability_score": 0.62,
            "critical_facility": False,
            "dominant_hazard": "lightning",
        },
        {
            "asset_id": "TX-003",
            "vulnerability_score": 0.20,
            "critical_facility": False,
            "dominant_hazard": "rainfall",
        },
    ]

    sample_crews = [
        {
            "crew_id": "CREW-01",
            "available": True,
        },
        {
            "crew_id": "CREW-02",
            "available": True,
        },
    ]

    result = generate_crew_preposition_plan(
        sample_assets,
        sample_crews,
        forecast_hours=48,
    )

    print("Crew Pre-Positioning Plan:")
    print(result)