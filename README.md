# NWS Individual Alerts

A Home Assistant custom integration that retrieves active weather alerts from the US National Weather Service API and exposes them as sensors for use in automation and dashboards.

- Polls the NWS API every minute (configurable)
- Creates a main sensor with the count of active alerts and full alert details as attributes
- Creates one sensor per alert category reporting the highest active severity level (`none`, `advisory`, `watch`, or `warning`)
- Supports lookup by NWS Zone ID, GPS coordinates, or a Home Assistant device tracker

## Installation

### HACS (Recommended)

1. Open **HACS → Integrations → ⋮ → Custom repositories** in Home Assistant
2. Add the repository URL `https://github.com/austinmroczek/nws_alerts` and select **Integration** as the category
3. Find and install **NWS Individual Alerts** through the search function
4. Restart Home Assistant to complete the setup

### Manual Installation

1. Copy the `custom_components/nws_individual_alerts/` directory into your Home Assistant `config/custom_components/` folder
2. Restart Home Assistant

After restarting, configure the integration using the instructions in the following section.

## Configuration

Go to **Settings → Devices & Services**, click **+ Add Integration**, search for **NWS Individual Alerts**, and follow the prompts.

### Lookup methods

Choose the method that best fits your situation:

**Zone ID** — Enter one or more NWS zone or county codes (e.g. `OHC049` or `OHZ033,OHZ034`). This is the most reliable option and matches how NWS issues alerts — each alert targets specific zones, so a zone lookup will never miss an alert for your area. Best choice for a fixed location.

To find your zone code: go to [alerts.weather.gov](https://alerts.weather.gov/), click "Land areas with zones", scroll to your state, then click "public zones" or "county zones". Your code is listed above the location name. Separate multiple zones with commas.

**GPS Coordinates** — Uses your Home Assistant latitude/longitude to query alerts for your precise location. The NWS API finds all zones that contain that point and returns their active alerts. Useful if you want alerts scoped to a specific address rather than a broader zone.

**Device Tracker** — Uses the GPS coordinates reported by a Home Assistant device tracker entity. The integration queries the NWS API using wherever the device is currently located. Use this if you want alerts that follow a person or vehicle.

After saving, the integration creates sensors under the name you entered as the Friendly Name during setup.

## Main Sensor

The main sensor's state is the **count of currently active alerts**. It is named after the Friendly Name you entered during setup (e.g. if you named it "Home", the sensor is `sensor.home_alerts`).

It exposes one attribute:

**`Alerts`** — a list of all active alerts, each with the following fields:

| Field | Description |
| --- | --- |
| `Event` | NWS event type name (e.g. `Tornado Warning`) |
| `Headline` | Short headline for the alert |
| `ID` | Stable UUID derived from the NWS alert ID |
| `URL` | Direct URL to the alert on api.weather.gov |
| `Type` | Message type (`Alert`, `Update`, or `Cancel`) |
| `Status` | Alert status (`Actual`, `Test`, etc.) |
| `Severity` | NWS severity (`Extreme`, `Severe`, `Moderate`, `Minor`, `Unknown`) |
| `Certainty` | NWS certainty (`Observed`, `Likely`, `Possible`, `Unlikely`, `Unknown`) |
| `Sent` | ISO timestamp when the alert was issued |
| `Onset` | ISO timestamp when the hazard is expected to begin |
| `Expires` | ISO timestamp when the alert expires |
| `Ends` | ISO timestamp when the hazard is expected to end (may be null) |
| `AreasAffected` | Free-text description of the affected areas |
| `Description` | Full alert text |
| `Instruction` | Recommended safety actions (may be null) |

A second sensor named `<friendly_name> Last Updated` reports the timestamp of the most recent successful API fetch.

## Alert Category Sensors

In addition to the main alert count sensor, the integration creates one **ENUM sensor per alert category**. Each sensor's state is the highest active severity level among alerts in that category:


| State      | Meaning                                                               |
| ------------ | ----------------------------------------------------------------------- |
| `none`     | No active alerts in this category                                     |
| `advisory` | An advisory, statement, outlook, or similar low-level alert is active |
| `watch`    | A watch is active — conditions are favorable for the hazard          |
| `warning`  | A warning is active — the hazard is imminent or occurring            |

Each sensor exposes two attributes when active:

- `active_alerts` — list of alert event names currently active in that category
- `alerts` — full detail list (same structure as the main sensor's `Alerts` attribute)

The categories and the NWS event types they cover:


| Sensor             | Advisory                                                                                                                                                                         | Watch                                                                               | Warning                                                                                                                                                                         |
| -------------------- | ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | ------------------------------------------------------------------------------------- | --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| **Flood**          | Coastal Flood Advisory, Coastal Flood Statement, Flash Flood Statement, Flood Advisory, Flood Statement, Hydrologic Outlook, Lakeshore Flood Advisory, Lakeshore Flood Statement | Coastal Flood Watch, Flash Flood Watch, Flood Watch, Lakeshore Flood Watch          | Coastal Flood Warning, Flash Flood Warning, Flood Warning, Lakeshore Flood Warning                                                                                              |
| **Tsunami**        | Tsunami Advisory                                                                                                                                                                 | Tsunami Watch                                                                       | Tsunami Warning                                                                                                                                                                 |
| **Tornado**        | —                                                                                                                                                                               | Tornado Watch                                                                       | Tornado Warning                                                                                                                                                                 |
| **Hurricane**      | Tropical Cyclone Local Statement                                                                                                                                                 | Hurricane Watch, Storm Surge Watch, Tropical Storm Watch, Typhoon Watch             | Hurricane Warning, Storm Surge Warning, Tropical Storm Warning, Typhoon Warning                                                                                                 |
| **Thunderstorms**  | —                                                                                                                                                                               | Severe Thunderstorm Watch, Storm Watch                                              | Severe Thunderstorm Warning, Storm Warning                                                                                                                                      |
| **Wind**           | Brisk Wind Advisory, Lake Wind Advisory, Wind Advisory                                                                                                                           | Gale Watch, High Wind Watch, Hurricane Force Wind Watch                             | Extreme Wind Warning, Gale Warning, High Wind Warning, Hurricane Force Wind Warning                                                                                             |
| **Dust**           | Blowing Dust Advisory, Dust Advisory                                                                                                                                             | —                                                                                  | Blowing Dust Warning, Dust Storm Warning                                                                                                                                        |
| **Fog**            | Dense Fog Advisory, Freezing Fog Advisory                                                                                                                                        | —                                                                                  | —                                                                                                                                                                              |
| **Winter Weather** | Avalanche Advisory, Freezing Spray Advisory, Winter Weather Advisory                                                                                                             | Avalanche Watch, Extreme Cold Watch, Heavy Freezing Spray Watch, Winter Storm Watch | Avalanche Warning, Blizzard Warning, Extreme Cold Warning, Heavy Freezing Spray Warning, Ice Storm Warning, Lake Effect Snow Warning, Snow Squall Warning, Winter Storm Warning |
| **Heat**           | Heat Advisory                                                                                                                                                                    | Extreme Heat Watch                                                                  | Extreme Heat Warning                                                                                                                                                            |
| **Wildfire**       | Ashfall Advisory, Extreme Fire Danger                                                                                                                                            | Fire Weather Watch                                                                  | Ashfall Warning, Fire Warning, Red Flag Warning                                                                                                                                 |
| **Volcano**        | —                                                                                                                                                                               | —                                                                                  | Volcano Warning                                                                                                                                                                 |
| **Beach Hazards**  | Beach Hazards Statement, High Surf Advisory, Rip Current Statement                                                                                                               | —                                                                                  | High Surf Warning                                                                                                                                                               |
| **Marine**         | Low Water Advisory, Marine Weather Statement, Small Craft Advisory                                                                                                               | Hazardous Seas Watch                                                                | Hazardous Seas Warning, Special Marine Warning                                                                                                                                  |
| **Air Quality**    | Air Quality Alert, Air Stagnation Advisory, Dense Smoke Advisory                                                                                                                 | —                                                                                  | —                                                                                                                                                                              |
| **Cold**           | Cold Weather Advisory, Frost Advisory                                                                                                                                            | Freeze Watch                                                                        | Freeze Warning                                                                                                                                                                  |
| **Weather**        | Hazardous Weather Outlook, Severe Weather Statement, Special Weather Statement                                                                                                   | —                                                                                  | —                                                                                                                                                                              |
| **Earthquake**     | —                                                                                                                                                                               | —                                                                                  | Earthquake Warning                                                                                                                                                              |
| **Other Hazards**  | 911 Telephone Outage, Blue Alert, Child Abduction Emergency, Civil Emergency Message, Evacuation Immediate, Local Area Emergency                                                 | —                                                                                  | Civil Danger Warning, Hazardous Materials Warning, Law Enforcement Warning, Nuclear Power Plant Warning, Radiological Hazard Warning, Shelter In Place Warning                  |

The following NWS alert types are intentionally ignored and will never appear in any sensor: `Administrative Message`, `Short Term Forecast`, `Test`.

The full list of NWS alert event types is available at: [https://api.weather.gov/alerts/types](https://api.weather.gov/alerts/types)

## Automation Examples

Trigger a notification when a Tornado Warning is issued:

```yaml
automation:
  - alias: "Notify on Tornado Warning"
    trigger:
      - platform: state
        entity_id: sensor.home_tornado
        to: "warning"
    action:
      - service: notify.mobile_app
        data:
          title: "Tornado Warning"
          message: >
            {{ state_attr('sensor.home_tornado', 'active_alerts') | join(', ') }}
```

Trigger on any warning-level alert across all categories:

```yaml
automation:
  - alias: "Notify on any Warning"
    trigger:
      - platform: state
        entity_id:
          - sensor.home_tornado
          - sensor.home_flood
          - sensor.home_winter_weather
          - sensor.home_thunderstorms
        to: "warning"
    action:
      - service: notify.mobile_app
        data:
          title: "Weather Warning"
          message: "{{ trigger.to_state.name }}: {{ state_attr(trigger.entity_id, 'active_alerts') | join(', ') }}"
```

Replace `home` in the entity IDs with the slug form of your Friendly Name (lowercase, spaces replaced with underscores).

## Testing

If there are currently no active alerts for your location but you want to do testing you can use any manually configured location ID that has an active alert.

To find those locations go to: https://api.weather.gov/alerts/active/count you will see a list of all areas with active alerts and how many alerts are active for each area.

You can use the given code(s) in your config to get the alerts for the selected zones in the integration.
