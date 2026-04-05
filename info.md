# NWS Individual Alerts

Retrieves active weather alerts from the US National Weather Service API and exposes them as Home Assistant sensors.

Based on the original work by [@eracknaphobia](https://github.com/eracknaphobia/nws_custom_component) and [@finity69x2](https://github.com/finity69x2/nws_alerts).

## What it creates

- **Alert count sensor** — state is the number of currently active alerts, with full alert details in the `Alerts` attribute
- **Category sensors** — one sensor per alert category (Tornado, Flood, Heat, Wildfire, etc.) reporting the highest active severity level: `none`, `advisory`, `watch`, or `warning`

## Configuration

After installation, go to **Settings → Devices & Services → Add Integration** and search for **NWS Individual Alerts**.

Choose a lookup method:

- **Zone ID** — enter your NWS zone or county code (e.g. `OHC049`). Find yours at [alerts.weather.gov](https://alerts.weather.gov/) under your state's zone or county list. Separate multiple zones with commas.
- **GPS Coordinates** — uses your Home Assistant home location.
- **Device Tracker** — uses the GPS position of a tracked device for location-aware alerts.
