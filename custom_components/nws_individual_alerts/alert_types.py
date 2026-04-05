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

    "Flood": frozenset({
        "Coastal Flood Advisory",
        "Coastal Flood Statement",
        "Coastal Flood Warning",
        "Coastal Flood Watch",
        "Flash Flood Statement",
        "Flash Flood Warning",
        "Flash Flood Watch",
        "Flood Advisory",
        "Flood Statement",
        "Flood Warning",
        "Flood Watch",
        "Hydrologic Outlook",
        "Lakeshore Flood Advisory",
        "Lakeshore Flood Statement",
        "Lakeshore Flood Warning",
        "Lakeshore Flood Watch",
    }),
    "Tsunami": frozenset({
        "Tsunami Advisory",
        "Tsunami Warning",
        "Tsunami Watch",
    }),
    "Tornado": frozenset({
        "Tornado Warning",
        "Tornado Watch",
    }),
    "Hurricane": frozenset({
        "Hurricane Warning",
        "Hurricane Watch",
        "Storm Surge Warning",
        "Storm Surge Watch",
        "Tropical Cyclone Local Statement",
        "Tropical Storm Warning",
        "Tropical Storm Watch",
        "Typhoon Warning",
        "Typhoon Watch",
    }),
    "Thunderstorms": frozenset({
        "Severe Thunderstorm Warning",
        "Severe Thunderstorm Watch",
        "Storm Warning",
        "Storm Watch",
    }),
    "Wind": frozenset({
        "Brisk Wind Advisory",
        "Extreme Wind Warning",
        "Gale Warning",
        "Gale Watch",
        "High Wind Warning",
        "High Wind Watch",
        "Hurricane Force Wind Warning",
        "Hurricane Force Wind Watch",
        "Lake Wind Advisory",
        "Wind Advisory",
    }),
    "Dust": frozenset({
        "Blowing Dust Advisory",
        "Blowing Dust Warning",
        "Dust Advisory",
        "Dust Storm Warning",
    }),
    "Fog": frozenset({
        "Dense Fog Advisory",
        "Freezing Fog Advisory",
    }),
    "Winter Weather": frozenset({
        "Avalanche Advisory",
        "Avalanche Warning",
        "Avalanche Watch",
        "Blizzard Warning",
        "Extreme Cold Warning",
        "Extreme Cold Watch",
        "Freezing Spray Advisory",
        "Heavy Freezing Spray Warning",
        "Heavy Freezing Spray Watch",
        "Ice Storm Warning",
        "Lake Effect Snow Warning",
        "Snow Squall Warning",
        "Winter Storm Warning",
        "Winter Storm Watch",
        "Winter Weather Advisory",
    }),
    "Heat": frozenset({
        "Excessive Heat Warning",
        "Excessive Heat Watch",
        "Extreme Heat Warning",
        "Extreme Heat Watch",
        "Heat Advisory",
    }),
    "Wildfire": frozenset({
        "Ashfall Advisory",
        "Ashfall Warning",
        "Extreme Fire Danger",
        "Fire Warning",
        "Fire Weather Watch",
        "Red Flag Warning",
    }),
    "Volcano": frozenset({
        "Volcano Warning",
    }),
    "Beach Hazards": frozenset({
        "Beach Hazards Statement",
        "High Surf Advisory",
        "High Surf Warning",
        "Rip Current Statement",
    }),
    "Marine": frozenset({
        "Hazardous Seas Warning",
        "Hazardous Seas Watch",
        "Low Water Advisory",
        "Marine Weather Statement",
        "Small Craft Advisory",
        "Special Marine Warning",
    }),
    "Air Quality": frozenset({
        "Air Quality Alert",
        "Air Stagnation Advisory",
        "Dense Smoke Advisory",
    }),
    "Cold": frozenset({
        "Cold Weather Advisory",
        "Freeze Warning",
        "Freeze Watch",
        "Frost Advisory",
    }),
    "Weather": frozenset({
        "Hazardous Weather Outlook",
        "Severe Weather Statement",
        "Special Weather Statement",
    }),
    "Earthquake": frozenset({
        "Earthquake Warning",
    }),

    # --- Life-Safety / Non-Weather Emergencies ---------------------------------
    "Other Hazards": frozenset({
        "911 Telephone Outage",
        "Blue Alert",
        "Child Abduction Emergency",
        "Civil Danger Warning",
        "Civil Emergency Message",
        "Evacuation Immediate",
        "Hazardous Materials Warning",
        "Law Enforcement Warning",
        "Local Area Emergency",
        "Nuclear Power Plant Warning",
        "Radiological Hazard Warning",
        "Shelter In Place Warning",
    }),
}
