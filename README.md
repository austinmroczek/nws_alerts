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


| Sensor                        | Alert Types Covered                                                            |
| ------------------------------- | -------------------------------------------------------------------------------- |
| **Flash Flood**               | Flash Flood Statement, Flash Flood Warning, Flash Flood Watch                  |
| **Flood**                     | Flood Advisory, Flood Statement, Flood Warning, Flood Watch                    |
| **Coastal Flood**             | Coastal Flood Advisory/Statement/Warning/Watch                                 |
| **Lakeshore Flood**           | Lakeshore Flood Advisory/Statement/Warning/Watch                               |
| **Storm Surge**               | Storm Surge Warning, Storm Surge Watch                                         |
| **Tsunami**                   | Tsunami Advisory, Tsunami Warning, Tsunami Watch                               |
| **Tornado**                   | Tornado Warning, Tornado Watch                                                 |
| **Hurricane**                 | Hurricane Warning/Watch, Hurricane Force Wind Warning/Watch, Tropical Storm Warning/Watch, Tropical Cyclone Local Statement, Typhoon Warning/Watch |
| **Storm**                     | Severe Thunderstorm Warning, Severe Thunderstorm Watch, Storm Warning, Storm Watch |
| **Wind**                      | High Wind Warning/Watch, Extreme Wind Warning, Brisk Wind Advisory, Lake Wind Advisory, Wind Advisory |
| **Gale**                      | Gale Warning, Gale Watch                                                       |
| **Dust**                      | Dust Advisory, Blowing Dust Advisory, Blowing Dust Warning, Dust Storm Warning |
| **Dense Fog**                 | Dense Fog Advisory                                                             |
| **Dense Smoke**               | Dense Smoke Advisory                                                           |
| **Winter Storm**              | Blizzard Warning, Extreme Cold Warning/Watch, Ice Storm Warning, Lake Effect Snow Warning, Snow Squall Warning, Winter Storm Warning/Watch, Winter Weather Advisory |
| **Freeze**                    | Freeze Warning, Freeze Watch                                                   |
| **Frost**                     | Frost Advisory                                                                 |
| **Freezing Fog**              | Freezing Fog Advisory                                                          |
| **Freezing Spray**            | Freezing Spray Advisory, Heavy Freezing Spray Warning/Watch                    |
| **Avalanche**                 | Avalanche Advisory, Avalanche Warning, Avalanche Watch                         |
| **Heat**                      | Extreme Heat Warning, Extreme Heat Watch, Heat Advisory                        |
| **Fire**                      | Fire Warning, Fire Weather Watch                                               |
| **Red Flag**                  | Red Flag Warning                                                               |
| **Extreme Fire Danger**       | Extreme Fire Danger                                                            |
| **Ashfall**                   | Ashfall Advisory, Ashfall Warning                                              |
| **Volcano**                   | Volcano Warning                                                                |
| **High Surf**                 | High Surf Advisory, High Surf Warning                                          |
| **Hazardous Seas**            | Hazardous Seas Warning, Hazardous Seas Watch                                   |
| **Small Craft**               | Small Craft Advisory                                                           |
| **Special Marine**            | Special Marine Warning                                                         |
| **Rip Current**               | Rip Current Statement                                                          |
| **Beach Hazards**             | Beach Hazards Statement                                                        |
| **Marine Weather**            | Marine Weather Statement                                                       |
| **Air Quality**               | Air Quality Alert                                                              |
| **Air Stagnation**            | Air Stagnation Advisory                                                        |
| **Cold Weather**              | Cold Weather Advisory                                                          |
| **Low Water**                 | Low Water Advisory                                                             |
| **Hydrologic**                | Hydrologic Outlook                                                             |
| **Hazardous Weather**         | Hazardous Weather Outlook                                                      |
| **Severe Weather**            | Severe Weather Statement                                                       |
| **Special Weather**           | Special Weather Statement                                                      |
| **Earthquake**                | Earthquake Warning                                                             |
| **Civil Danger**              | Civil Danger Warning                                                           |
| **Civil Emergency**           | Civil Emergency Message                                                        |
| **Child Abduction Emergency** | Child Abduction Emergency                                                      |
| **Evacuation**                | Evacuation Immediate                                                           |
| **Shelter In Place**          | Shelter In Place Warning                                                       |
| **Law Enforcement**           | Law Enforcement Warning                                                        |
| **Local Area Emergency**      | Local Area Emergency                                                           |
| **Nuclear Power Plant**       | Nuclear Power Plant Warning                                                    |
| **Radiological Hazard**       | Radiological Hazard Warning                                                    |
| **Hazardous Materials**       | Hazardous Materials Warning                                                    |
| **911 Telephone Outage**      | 911 Telephone Outage                                                           |
| **Blue Alert**                | Blue Alert                                                                     |

The full list of NWS alert event types is available at: [https://api.weather.gov/alerts/types](https://api.weather.gov/alerts/types)

## Testing

If there are currently no active alerts for your location but you want to do testing you can use any manually configured location ID that has an active alert.

To find those locations go to: https://api.weather.gov/alerts/active/count you will see a list of all areas with active alerts and how many alerts are active for each area.

You can use the given code(s) in your config to get the alerts for the selected zones in the integration.
