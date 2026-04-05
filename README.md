# Alerts from the US National Weather Service  (nws_individual_alerts)

An updated version of the nws_alerts custom integration for Home Assistant originally found at github.com/eracknaphobia/nws_custom_component, and then upgraded  at https://github.com/finity69x2/nws_alerts

This integration retrieves updated weather alerts every minute from the US NWS API (by default but it can be changed in the config options).

You can configure the integration to use your NWS Zone, your precise location via GPS coordinates or you can get dynamic location alerts by configuring the integration to use a device_tracker entity from HA as long as that device tracker provides GPS coordinates.

The integration presents the number of currently active alerts as the state of the main sensor and lists full alert details as a list in its attributes. It also creates one sensor per alert category that reports the highest active severity level (`advisory`, `watch`, or `warning`) for that category.

The sensor that is created is used in my "NWS Alerts" package: https://github.com/finity69x2/nws_alerts/blob/master/packages/nws_alerts_package.yaml

You can also display the generated alerts in your frontend. For example usage see: https://github.com/finity69x2/nws_alerts/blob/master/lovelace/alerts_tab.yaml

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

## Configuration:

<b>NOTE: As of HA versoin 2024.5.x the yaml configuration option is broken. I don't know if it will ever be fixed so the only viable config option is via the UI</b>

<b>You can configure the integration via the "Configuration->Integrations" section of the Home Assistant UI:</b>

Click on "+ Add Integration" buuton in the bottom right corner.

Search for "NWS Alerts" in the list of integrations and follow the UI prompts to configure the sensor.

You can find your Zone or County ID by going to https://alerts.weather.gov/, click on "Land areas with zones", scroll down to your state, then click on either "public zones" or "county zones". Then scroll to find your location (county) from the list(s). The desired zone or county code (depending on which link you used) will be listed above the location

There are a few configuration method options to select from.

Please see the following link to help you decide which option to use:

https://github.com/finity69x2/nws_alerts/blob/master/lookup_options.md

If you select the "Using a device tracker" option under the "GPS Location" option then HA will use the GPS coordinates provided by that tracker to query for alerts so you should follow the same recommendations for using GPS coordinates when using that option.

After you restart Home Assistant then you should have a new sensor (by default) called "sensor.nws_individual_alerts" in your system.

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


| Sensor | Advisory | Watch | Warning |
| --- | --- | --- | --- |
| **Flood** | Coastal Flood Advisory, Coastal Flood Statement, Flash Flood Statement, Flood Advisory, Flood Statement, Hydrologic Outlook, Lakeshore Flood Advisory, Lakeshore Flood Statement | Coastal Flood Watch, Flash Flood Watch, Flood Watch, Lakeshore Flood Watch | Coastal Flood Warning, Flash Flood Warning, Flood Warning, Lakeshore Flood Warning |
| **Tsunami** | Tsunami Advisory | Tsunami Watch | Tsunami Warning |
| **Tornado** | — | Tornado Watch | Tornado Warning |
| **Hurricane** | Tropical Cyclone Local Statement | Hurricane Watch, Storm Surge Watch, Tropical Storm Watch, Typhoon Watch | Hurricane Warning, Storm Surge Warning, Tropical Storm Warning, Typhoon Warning |
| **Thunderstorms** | — | Severe Thunderstorm Watch, Storm Watch | Severe Thunderstorm Warning, Storm Warning |
| **Wind** | Brisk Wind Advisory, Lake Wind Advisory, Wind Advisory | Gale Watch, High Wind Watch, Hurricane Force Wind Watch | Extreme Wind Warning, Gale Warning, High Wind Warning, Hurricane Force Wind Warning |
| **Dust** | Blowing Dust Advisory, Dust Advisory | — | Blowing Dust Warning, Dust Storm Warning |
| **Fog** | Dense Fog Advisory, Freezing Fog Advisory | — | — |
| **Winter Weather** | Avalanche Advisory, Freezing Spray Advisory, Winter Weather Advisory | Avalanche Watch, Extreme Cold Watch, Heavy Freezing Spray Watch, Winter Storm Watch | Avalanche Warning, Blizzard Warning, Extreme Cold Warning, Heavy Freezing Spray Warning, Ice Storm Warning, Lake Effect Snow Warning, Snow Squall Warning, Winter Storm Warning |
| **Heat** | Heat Advisory | Extreme Heat Watch | Extreme Heat Warning |
| **Wildfire** | Ashfall Advisory, Extreme Fire Danger | Fire Weather Watch | Ashfall Warning, Fire Warning, Red Flag Warning |
| **Volcano** | — | — | Volcano Warning |
| **Beach Hazards** | Beach Hazards Statement, High Surf Advisory, Rip Current Statement | — | High Surf Warning |
| **Marine** | Low Water Advisory, Marine Weather Statement, Small Craft Advisory | Hazardous Seas Watch | Hazardous Seas Warning, Special Marine Warning |
| **Air Quality** | Air Quality Alert, Air Stagnation Advisory, Dense Smoke Advisory | — | — |
| **Cold** | Cold Weather Advisory, Frost Advisory | Freeze Watch | Freeze Warning |
| **Weather** | Hazardous Weather Outlook, Severe Weather Statement, Special Weather Statement | — | — |
| **Earthquake** | — | — | Earthquake Warning |
| **Other Hazards** | 911 Telephone Outage, Blue Alert, Child Abduction Emergency, Civil Emergency Message, Evacuation Immediate, Local Area Emergency | — | Civil Danger Warning, Hazardous Materials Warning, Law Enforcement Warning, Nuclear Power Plant Warning, Radiological Hazard Warning, Shelter In Place Warning |

The full list of NWS alert event types is available at: [https://api.weather.gov/alerts/types](https://api.weather.gov/alerts/types)

## Testing

If there are currently no active alerts for your location but you want to do testing you can use any manually configured location ID that has an active alert.

To find those locations go to: https://api.weather.gov/alerts/active/count you will see a list of all areas with active alerts and how many alerts are active for each area.

You can use the given code(s) in your config to get the alerts for the selected zones in the integration.
