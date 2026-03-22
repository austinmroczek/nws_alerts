"""DataUpdateCoordinator and API fetch logic for NWS Alerts."""

import asyncio
import hashlib
import logging
import uuid
from datetime import timedelta

from homeassistant.const import CONF_NAME
from homeassistant.core import HomeAssistant
from homeassistant.helpers.aiohttp_client import async_get_clientsession
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed
from homeassistant.util import dt as dt_util

from .const import (
    API_ENDPOINT,
    CONF_GPS_LOC,
    CONF_INTERVAL,
    CONF_TIMEOUT,
    CONF_TRACKER,
    CONF_ZONE_ID,
    USER_AGENT,
)

_LOGGER = logging.getLogger(__name__)


class AlertsDataUpdateCoordinator(DataUpdateCoordinator):
    """Class to manage fetching NWS Alert data."""

    def __init__(self, hass, config, the_timeout: int, interval: int):
        """Initialize."""
        self.interval = timedelta(minutes=interval)
        self.name = config[CONF_NAME]
        self.timeout = the_timeout
        self.config = config
        self.hass = hass

        _LOGGER.debug("Data will be update every %s", self.interval)

        super().__init__(hass, _LOGGER, name=self.name, update_interval=self.interval)

    async def _async_update_data(self):
        """Fetch data."""
        coords = None
        if CONF_TRACKER in self.config:
            coords = await self._get_tracker_gps()
        async with asyncio.timeout(self.timeout):
            try:
                data = await update_alerts(self.hass, self.config, coords)
            except AttributeError:
                _LOGGER.debug(
                    "Error fetching most recent data from NWS Alerts API; will continue trying"
                )
                return self.data
            except Exception as error:
                raise UpdateFailed(error) from error
            _LOGGER.debug("Data: %s", data)
            return data

    async def _get_tracker_gps(self):
        """Return device tracker GPS data."""
        tracker = self.config[CONF_TRACKER]
        entity = self.hass.states.get(tracker)
        if entity and "source_type" in entity.attributes:
            return f"{entity.attributes['latitude']},{entity.attributes['longitude']}"
        return None


async def update_alerts(hass: HomeAssistant, config, coords) -> dict:
    """Fetch new state data for the sensor.
    This is the only method that should fetch new data for Home Assistant.
    """
    return await async_get_state(hass, config, coords)


async def async_get_state(hass: HomeAssistant, config, coords) -> dict:
    """Query API for status."""

    zone_id = ""
    gps_loc = ""
    url = f"{API_ENDPOINT}/alerts/active/count"
    values = {
        "state": 0,
        "event": None,
        "event_id": None,
        "message_type": None,
        "event_status": None,
        "event_severity": None,
        "event_sent": None,
        "event_onset": None,
        "event_expires": None,
        "event_ends": None,
        "areas_affected": None,
        "display_desc": None,
        "spoken_desc": None,
    }
    headers = {"User-Agent": USER_AGENT, "Accept": "application/ld+json"}
    data = None

    if CONF_ZONE_ID in config:
        zone_id = config[CONF_ZONE_ID]
        _LOGGER.debug("getting state for %s from %s", zone_id, url)
    elif CONF_GPS_LOC in config or CONF_TRACKER in config:
        if coords is not None:
            gps_loc = coords
        else:
            gps_loc = config[CONF_GPS_LOC].replace(" ", "")
        _LOGGER.debug("getting state for %s from %s", gps_loc, url)

    session = async_get_clientsession(hass)
    async with session.get(url, headers=headers) as r:
        if r.status == 200:
            data = await r.json()
        else:
            _LOGGER.error("Problem updating NWS data: (%s)", r.status)

    if data is not None:
        if "zones" in data and zone_id != "":
            for zone in zone_id.split(","):
                if zone in data["zones"]:
                    values = await async_get_alerts(hass, zone_id=zone_id)
                    break
        else:
            values = await async_get_alerts(hass, gps_loc=gps_loc)

    return values


async def async_get_alerts(
    hass: HomeAssistant, zone_id: str = "", gps_loc: str = ""
) -> dict:
    """Query API for Alerts."""

    url = ""
    alerts = {}
    headers = {"User-Agent": USER_AGENT, "Accept": "application/geo+json"}
    data = None

    if zone_id != "":
        url = f"{API_ENDPOINT}/alerts/active?zone={zone_id}"
        _LOGGER.debug("getting alert for %s from %s", zone_id, url)
    elif gps_loc != "":
        url = f"{API_ENDPOINT}/alerts/active?point={gps_loc}"
        _LOGGER.debug("getting alert for %s from %s", gps_loc, url)

    session = async_get_clientsession(hass)
    async with session.get(url, headers=headers) as r:
        if r.status == 200:
            data = await r.json()
        else:
            _LOGGER.error("Problem updating NWS data: (%s)", r.status)

    if data is not None:
        features = data["features"]
        alert_list = []
        for alert in features:
            tmp_dict = {}

            alert_id = await generate_id(alert["id"])

            tmp_dict["Event"] = alert["properties"]["event"]
            tmp_dict["ID"] = alert_id
            tmp_dict["URL"] = alert["id"]

            event = alert["properties"]["event"]
            if "NWSheadline" in alert["properties"]["parameters"]:
                tmp_dict["Headline"] = alert["properties"]["parameters"]["NWSheadline"][0]
            else:
                tmp_dict["Headline"] = event

            tmp_dict["Type"] = alert["properties"]["messageType"]
            tmp_dict["Status"] = alert["properties"]["status"]
            tmp_dict["Severity"] = alert["properties"]["severity"]
            tmp_dict["Certainty"] = alert["properties"]["certainty"]
            tmp_dict["Sent"] = alert["properties"]["sent"]
            tmp_dict["Onset"] = alert["properties"]["onset"]
            tmp_dict["Expires"] = alert["properties"]["expires"]
            tmp_dict["Ends"] = alert["properties"]["ends"]
            tmp_dict["AreasAffected"] = alert["properties"]["areaDesc"]
            tmp_dict["Description"] = alert["properties"]["description"]
            tmp_dict["Instruction"] = alert["properties"]["instruction"]

            alert_list.append(tmp_dict)

        alerts["state"] = len(features)
        alerts["alerts"] = alert_list
        alerts["last_updated"] = dt_util.utcnow()

    return alerts


async def generate_id(val: str) -> str:
    """Generate a stable UUID from a NWS alert ID string."""
    hex_string = hashlib.md5(val.encode("UTF-8")).hexdigest()
    return str(uuid.UUID(hex=hex_string))
