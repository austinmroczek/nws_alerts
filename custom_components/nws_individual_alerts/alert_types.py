"""NWS alert event type groupings.

Each entry in ALERT_GROUPS produces one NWSAlertGroupSensor. The sensor value
reflects the highest active severity level among the alert types in the group:

  "advisory"  — Advisory, Statement, Outlook, or equivalent
  "watch"     — Watch
  "warning"   — Warning

Source: https://api.weather.gov/alerts/types
"""

# Alert types to ignore entirely — not actionable weather events.
IGNORE_TYPES: frozenset[str] = frozenset({
    "Administrative Message",
    "Short Term Forecast",
    "Test",
})

# ---------------------------------------------------------------------------
# ALERT_GROUPS: ordered mapping of sensor display name → NWS event type set.
# Each key becomes one sensor entity; the value is the set of NWS event types
# that contribute to it.
# ---------------------------------------------------------------------------
ALERT_GROUPS: dict[str, frozenset[str]] = {

    # --- Flood -----------------------------------------------------------------
    "Flash Flood": frozenset({
        "Flash Flood Statement",
        "Flash Flood Warning",
        "Flash Flood Watch",
    }),
    "Flood": frozenset({
        "Flood Advisory",
        "Flood Statement",
        "Flood Warning",
        "Flood Watch",
    }),
    "Coastal Flood": frozenset({
        "Coastal Flood Advisory",
        "Coastal Flood Statement",
        "Coastal Flood Warning",
        "Coastal Flood Watch",
    }),
    "Lakeshore Flood": frozenset({
        "Lakeshore Flood Advisory",
        "Lakeshore Flood Statement",
        "Lakeshore Flood Warning",
        "Lakeshore Flood Watch",
    }),
    "Storm Surge": frozenset({
        "Storm Surge Warning",
        "Storm Surge Watch",
    }),
    "Tsunami": frozenset({
        "Tsunami Advisory",
        "Tsunami Warning",
        "Tsunami Watch",
    }),

    # --- Storm -----------------------------------------------------------------
    "Tornado": frozenset({
        "Tornado Warning",
        "Tornado Watch",
    }),
    "Hurricane": frozenset({
        "Hurricane Warning",
        "Hurricane Watch",
        "Hurricane Force Wind Warning",
        "Hurricane Force Wind Watch",
        "Tropical Cyclone Local Statement",
        "Tropical Storm Warning",
        "Tropical Storm Watch",
        "Typhoon Warning",
        "Typhoon Watch",
    }),
    "Storm": frozenset({
        "Severe Thunderstorm Warning",
        "Severe Thunderstorm Watch",
        "Storm Warning",
        "Storm Watch",
    }),

    # --- Wind ------------------------------------------------------------------
    "Wind": frozenset({
        "Brisk Wind Advisory",
        "Extreme Wind Warning",
        "High Wind Warning",
        "High Wind Watch",
        "Lake Wind Advisory",
        "Wind Advisory",
    }),
    "Gale": frozenset({
        "Gale Warning",
        "Gale Watch",
    }),

    # --- Dust / Visibility -----------------------------------------------------
    "Dust": frozenset({
        "Blowing Dust Advisory",
        "Blowing Dust Warning",
        "Dust Advisory",
        "Dust Storm Warning",
    }),
    "Dense Fog": frozenset({
        "Dense Fog Advisory",
    }),
    "Dense Smoke": frozenset({
        "Dense Smoke Advisory",
    }),

    # --- Winter / Ice ----------------------------------------------------------
    "Winter Storm": frozenset({
        "Blizzard Warning",
        "Extreme Cold Warning",
        "Extreme Cold Watch",
        "Ice Storm Warning",
        "Lake Effect Snow Warning",
        "Snow Squall Warning",
        "Winter Storm Warning",
        "Winter Storm Watch",
        "Winter Weather Advisory",
    }),
    "Freeze": frozenset({
        "Freeze Warning",
        "Freeze Watch",
    }),
    "Frost": frozenset({
        "Frost Advisory",
    }),
    "Freezing Fog": frozenset({
        "Freezing Fog Advisory",
    }),
    "Freezing Spray": frozenset({
        "Freezing Spray Advisory",
        "Heavy Freezing Spray Warning",
        "Heavy Freezing Spray Watch",
    }),
    "Avalanche": frozenset({
        "Avalanche Advisory",
        "Avalanche Warning",
        "Avalanche Watch",
    }),

    # --- Heat ------------------------------------------------------------------
    "Heat": frozenset({
        "Extreme Heat Warning",
        "Extreme Heat Watch",
        "Heat Advisory",
    }),

    # --- Fire ------------------------------------------------------------------
    "Fire": frozenset({
        "Fire Warning",
        "Fire Weather Watch",
    }),
    "Red Flag": frozenset({
        "Red Flag Warning",
    }),
    "Extreme Fire Danger": frozenset({
        "Extreme Fire Danger",
    }),
    "Ashfall": frozenset({
        "Ashfall Advisory",
        "Ashfall Warning",
    }),
    "Volcano": frozenset({
        "Volcano Warning",
    }),

    # --- Marine ----------------------------------------------------------------
    "High Surf": frozenset({
        "High Surf Advisory",
        "High Surf Warning",
    }),
    "Hazardous Seas": frozenset({
        "Hazardous Seas Warning",
        "Hazardous Seas Watch",
    }),
    "Small Craft": frozenset({
        "Small Craft Advisory",
    }),
    "Special Marine": frozenset({
        "Special Marine Warning",
    }),
    "Rip Current": frozenset({
        "Rip Current Statement",
    }),
    "Beach Hazards": frozenset({
        "Beach Hazards Statement",
    }),
    "Marine Weather": frozenset({
        "Marine Weather Statement",
    }),

    # --- General Weather -------------------------------------------------------
    "Air Quality": frozenset({
        "Air Quality Alert",
    }),
    "Air Stagnation": frozenset({
        "Air Stagnation Advisory",
    }),
    "Cold Weather": frozenset({
        "Cold Weather Advisory",
    }),
    "Low Water": frozenset({
        "Low Water Advisory",
    }),
    "Hydrologic": frozenset({
        "Hydrologic Outlook",
    }),
    "Hazardous Weather": frozenset({
        "Hazardous Weather Outlook",
    }),
    "Severe Weather": frozenset({
        "Severe Weather Statement",
    }),
    "Special Weather": frozenset({
        "Special Weather Statement",
    }),

    # --- Life-Safety / Non-Weather Emergencies ---------------------------------
    "Earthquake": frozenset({
        "Earthquake Warning",
    }),
    "Civil Danger": frozenset({
        "Civil Danger Warning",
    }),
    "Civil Emergency": frozenset({
        "Civil Emergency Message",
    }),
    "Child Abduction Emergency": frozenset({
        "Child Abduction Emergency",
    }),
    "Evacuation": frozenset({
        "Evacuation Immediate",
    }),
    "Shelter In Place": frozenset({
        "Shelter In Place Warning",
    }),
    "Law Enforcement": frozenset({
        "Law Enforcement Warning",
    }),
    "Local Area Emergency": frozenset({
        "Local Area Emergency",
    }),
    "Nuclear Power Plant": frozenset({
        "Nuclear Power Plant Warning",
    }),
    "Radiological Hazard": frozenset({
        "Radiological Hazard Warning",
    }),
    "Hazardous Materials": frozenset({
        "Hazardous Materials Warning",
    }),
    "911 Telephone Outage": frozenset({
        "911 Telephone Outage",
    }),
    "Blue Alert": frozenset({
        "Blue Alert",
    }),
}
