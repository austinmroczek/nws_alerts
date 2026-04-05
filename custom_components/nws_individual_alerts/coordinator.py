"""DataUpdateCoordinator and API fetch logic for NWS Alerts."""

from __future__ import annotations

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

from .alert_types import ALERT_GROUPS, IGNORE_TYPES
from .const import (
    API_ENDPOINT,
    CONF_GPS_LOC,
    CONF_INTERVAL,
    CONF_TIMEOUT,
    CONF_TRACKER,
    CONF_ZONE_ID,
    USER_AGENT,
)

_KNOWN_ALERT_TYPES: frozenset[str] = IGNORE_TYPES | frozenset(
    event for group in ALERT_GROUPS.values() for event in group
)

_LOGGER = logging.getLogger(__name__)


class AlertsDataUpdateCoordinator(DataUpdateCoordinator):
    """Class to manage fetching NWS Alert data."""

    def __init__(self, hass: HomeAssistant, config: dict, the_timeout: int, interval: int) -> None:
        """Initialize."""
        self.interval = timedelta(minutes=interval)
        self.name = config[CONF_NAME]
        self.timeout = the_timeout
        self.config = config

        _LOGGER.debug("Data will be update every %s", self.interval)

        super().__init__(hass, _LOGGER, name=self.name, update_interval=self.interval)

    async def _async_update_data(self) -> dict:
        """Fetch data."""
        coords = None
        if CONF_TRACKER in self.config:
            coords = await self._get_tracker_gps()
        try:
            async with asyncio.timeout(self.timeout):
                data = await async_fetch_alerts(self.hass, self.config, coords)
        except Exception as error:
            _LOGGER.warning(
                "Error fetching NWS Alerts data, keeping last known state: %s", error
            )
            if self.data is not None:
                return self.data
            raise UpdateFailed(error) from error

        _LOGGER.debug("Data: %s", data)
        return data

    async def _get_tracker_gps(self) -> str | None:
        """Return device tracker GPS data."""
        tracker = self.config[CONF_TRACKER]
        entity = self.hass.states.get(tracker)
        if entity and "source_type" in entity.attributes:
            return f"{entity.attributes['latitude']},{entity.attributes['longitude']}"
        return None


async def async_fetch_alerts(
    hass: HomeAssistant, config: dict, coords: str | None
) -> dict:
    """Determine the query target from config and fetch alerts."""
    if CONF_ZONE_ID in config:
        return await async_get_alerts(hass, zone_id=config[CONF_ZONE_ID])

    gps_loc = coords if coords is not None else config[CONF_GPS_LOC].replace(" ", "")
    return await async_get_alerts(hass, gps_loc=gps_loc)


async def async_get_alerts(
    hass: HomeAssistant, zone_id: str = "", gps_loc: str = ""
) -> dict:
    """Query the NWS alerts API and return parsed alert data."""
    if zone_id:
        url = f"{API_ENDPOINT}/alerts/active?zone={zone_id}"
        _LOGGER.debug("Fetching alerts for zone %s from %s", zone_id, url)
    elif gps_loc:
        url = f"{API_ENDPOINT}/alerts/active?point={gps_loc}"
        _LOGGER.debug("Fetching alerts for point %s from %s", gps_loc, url)
    else:
        return {}

    headers = {"User-Agent": USER_AGENT, "Accept": "application/geo+json"}
    session = async_get_clientsession(hass)

    async with session.get(url, headers=headers) as r:
        if r.status != 200:
            raise UpdateFailed(f"NWS API returned HTTP {r.status} for {url}")
        data = await r.json()

    features = data.get("features", [])
    alert_list = []
    for alert in features:
        event = alert["properties"]["event"]
        alert_id = await generate_id(alert["id"])

        if "NWSheadline" in alert["properties"].get("parameters", {}):
            headline = alert["properties"]["parameters"]["NWSheadline"][0]
        else:
            headline = event

        alert_list.append({
            "Event": event,
            "ID": alert_id,
            "URL": alert["id"],
            "Headline": headline,
            "Type": alert["properties"]["messageType"],
            "Status": alert["properties"]["status"],
            "Severity": alert["properties"]["severity"],
            "Certainty": alert["properties"]["certainty"],
            "Sent": alert["properties"]["sent"],
            "Onset": alert["properties"]["onset"],
            "Expires": alert["properties"]["expires"],
            "Ends": alert["properties"]["ends"],
            "AreasAffected": alert["properties"]["areaDesc"],
            "Description": alert["properties"]["description"],
            "Instruction": alert["properties"]["instruction"],
        })

    unknown = {a["Event"] for a in alert_list} - _KNOWN_ALERT_TYPES
    for event_type in sorted(unknown):
        _LOGGER.warning(
            "NWS alert type %r is not mapped to any sensor group", event_type
        )

    return {
        "state": len(features),
        "alerts": alert_list,
        "last_updated": dt_util.utcnow(),
    }


async def generate_id(val: str) -> str:
    """Generate a stable UUID from a NWS alert ID string."""
    hex_string = hashlib.md5(val.encode("UTF-8")).hexdigest()
    return str(uuid.UUID(hex=hex_string))
