# NWS Alert Lookup Options

The NWS Individual Alerts integration supports three methods for querying weather alerts from the National Weather Service API. Each has different trade-offs around precision and coverage.

## GPS Location (recommended)

GPS-based lookup uses a latitude/longitude coordinate to query the NWS `/alerts/active?point=` endpoint. The NWS determines which zones contain that point and returns only the alerts that affect your precise location.

**This is the recommended method for most users.** It provides the most accurate results and avoids alerts that technically cover your county or zone but don't affect your specific location.

The integration offers two GPS sub-options:

- **Home Assistant location** — uses the latitude/longitude configured in your Home Assistant instance (Settings → System → General)
- **Device Tracker** — uses the GPS coordinates reported by a Home Assistant device tracker entity. Useful if you want alerts that follow a person or vehicle.

## Zone ID

Zone ID lookup uses one or more NWS zone or county codes (e.g. `OHC049` or `OHZ033,OHZ034`) to query the NWS `/alerts/active?zone=` endpoint. Both county and public zone codes are accepted and can be mixed.

Zones cover a broader geographic area than a single point, so this method may return alerts that do not affect your exact location. It is useful when:

- GPS coordinates are not available or not appropriate
- You intentionally want broader coverage (e.g. monitoring an entire county)

To find your zone code: go to [alerts.weather.gov](https://alerts.weather.gov/), click "Land areas with zones", scroll to your state, then click "public zones" or "county zones". Separate multiple codes with commas.

## Sources

- https://www.weather.gov/media/documentation/docs/NWS_Geolocation.pdf
- https://www.weather.gov/gis/PublicZones
