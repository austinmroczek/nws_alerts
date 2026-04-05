"""Adds config flow for NWS Individual Alerts."""

from __future__ import annotations

import logging
from typing import Any

import voluptuous as vol
from homeassistant import config_entries
from homeassistant.components.device_tracker import DOMAIN as TRACKER_DOMAIN
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import CONF_NAME
from homeassistant.core import HomeAssistant, callback
from homeassistant.data_entry_flow import FlowResult
from homeassistant.helpers.aiohttp_client import async_get_clientsession

from .const import (
    API_ENDPOINT,
    CONF_GPS_LOC,
    CONF_INTERVAL,
    CONF_TIMEOUT,
    CONF_TRACKER,
    CONF_ZONE_ID,
    CONFIG_VERSION,
    DEFAULT_INTERVAL,
    DEFAULT_NAME,
    DEFAULT_TIMEOUT,
    DOMAIN,
    USER_AGENT,
)

JSON_FEATURES = "features"
JSON_PROPERTIES = "properties"
JSON_ID = "id"

_LOGGER = logging.getLogger(__name__)
MENU_OPTIONS: list[str] = ["zone", "gps"]
MENU_GPS: list[str] = ["gps_loc", "gps_tracker"]


def _get_schema_zone(
    hass: HomeAssistant,
    user_input: dict[str, Any] | None,
    default_dict: dict[str, Any],
) -> vol.Schema:
    """Get a schema using the default_dict as a backup."""
    if user_input is None:
        user_input = {}

    def _get_default(key: str) -> Any:
        return user_input.get(key, default_dict.get(key))

    return vol.Schema(
        {
            vol.Required(CONF_ZONE_ID, default=_get_default(CONF_ZONE_ID)): str,
            vol.Optional(CONF_NAME, default=_get_default(CONF_NAME)): str,
            vol.Optional(CONF_INTERVAL, default=_get_default(CONF_INTERVAL)): int,
            vol.Optional(CONF_TIMEOUT, default=_get_default(CONF_TIMEOUT)): int,
        }
    )


def _get_schema_gps(
    hass: HomeAssistant,
    user_input: dict[str, Any] | None,
    default_dict: dict[str, Any],
) -> vol.Schema:
    """Get a schema using the default_dict as a backup."""
    if user_input is None:
        user_input = {}

    def _get_default(key: str) -> Any:
        return user_input.get(key, default_dict.get(key))

    return vol.Schema(
        {
            vol.Required(CONF_GPS_LOC, default=_get_default(CONF_GPS_LOC)): str,
            vol.Optional(CONF_NAME, default=_get_default(CONF_NAME)): str,
            vol.Optional(CONF_INTERVAL, default=_get_default(CONF_INTERVAL)): int,
            vol.Optional(CONF_TIMEOUT, default=_get_default(CONF_TIMEOUT)): int,
        }
    )


def _get_schema_tracker(
    hass: HomeAssistant,
    user_input: dict[str, Any] | None,
    default_dict: dict[str, Any],
) -> vol.Schema:
    """Get a schema using the default_dict as a backup."""
    if user_input is None:
        user_input = {}

    def _get_default(key: str, fallback_default: Any = None) -> Any:
        return user_input.get(key, default_dict.get(key, fallback_default))

    return vol.Schema(
        {
            vol.Required(
                CONF_TRACKER, default=_get_default(CONF_TRACKER, "(none)")
            ): vol.In(_get_entities(hass, TRACKER_DOMAIN)),
            vol.Optional(CONF_NAME, default=_get_default(CONF_NAME)): str,
            vol.Optional(CONF_INTERVAL, default=_get_default(CONF_INTERVAL)): int,
            vol.Optional(CONF_TIMEOUT, default=_get_default(CONF_TIMEOUT)): int,
        }
    )


def _get_entities(
    hass: HomeAssistant,
    domain: str,
    search: list[str] | None = None,
    extra_entities: list[str] | None = None,
) -> list[str]:
    data = ["(none)"]
    if domain not in hass.data:
        return data

    for entity in hass.data[domain].entities:
        if search is not None and not any(map(entity.entity_id.__contains__, search)):
            continue
        data.append(entity.entity_id)

    if extra_entities:
        data.extend(extra_entities)

    return data


async def _get_zone_list(self: NWSAlertsFlowHandler) -> str | None:
    """Return comma-separated zone IDs for the HA home location."""
    lat = self.hass.config.latitude
    lon = self.hass.config.longitude

    headers = {"User-Agent": USER_AGENT, "Accept": "application/geo+json"}
    url = f"{API_ENDPOINT}/zones?point={lat},{lon}"

    _LOGGER.debug("Getting zone list for %s,%s from %s", lat, lon, url)
    session = async_get_clientsession(self.hass)
    async with session.get(url, headers=headers) as r:
        if r.status != 200:
            return None
        data = await r.json()

    if JSON_FEATURES in data:
        zone_list = [
            feature[JSON_PROPERTIES][JSON_ID]
            for feature in data[JSON_FEATURES]
        ]
        _LOGGER.debug("Zones list: %s", zone_list)
        return ",".join(zone_list)
    return None


class NWSAlertsFlowHandler(config_entries.ConfigFlow, domain=DOMAIN):
    """Config flow for NWS Individual Alerts."""

    VERSION = CONFIG_VERSION

    def __init__(self) -> None:
        """Initialize."""
        self._data: dict[str, Any] = {}
        self._errors: dict[str, str] = {}

    async def async_step_user(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        """Handle the flow initialized by the user."""
        return self.async_show_menu(step_id="user", menu_options=MENU_OPTIONS)

    async def async_step_gps(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        """Handle the GPS sub-menu."""
        return self.async_show_menu(step_id="gps", menu_options=MENU_GPS)

    async def async_step_gps_tracker(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        """Handle a flow for device trackers."""
        self._errors = {}
        if user_input is not None:
            self._data.update(user_input)
            return self.async_create_entry(title=self._data[CONF_NAME], data=self._data)
        return await self._show_config_gps_tracker(user_input)

    async def _show_config_gps_tracker(
        self, user_input: dict[str, Any] | None
    ) -> FlowResult:
        """Show the configuration form for device tracker."""
        defaults: dict[str, Any] = {
            CONF_NAME: DEFAULT_NAME,
            CONF_INTERVAL: DEFAULT_INTERVAL,
            CONF_TIMEOUT: DEFAULT_TIMEOUT,
        }
        return self.async_show_form(
            step_id="gps_tracker",
            data_schema=_get_schema_tracker(self.hass, user_input, defaults),
            errors=self._errors,
        )

    async def async_step_gps_loc(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        """Handle a flow for GPS coordinates."""
        lat = self.hass.config.latitude
        lon = self.hass.config.longitude
        self._errors = {}
        self._gps_loc = f"{lat},{lon}"

        if user_input is not None:
            self._data.update(user_input)
            return self.async_create_entry(title=self._data[CONF_NAME], data=self._data)
        return await self._show_config_gps_loc(user_input)

    async def _show_config_gps_loc(
        self, user_input: dict[str, Any] | None
    ) -> FlowResult:
        """Show the configuration form for GPS coordinates."""
        defaults: dict[str, Any] = {
            CONF_NAME: DEFAULT_NAME,
            CONF_INTERVAL: DEFAULT_INTERVAL,
            CONF_TIMEOUT: DEFAULT_TIMEOUT,
            CONF_GPS_LOC: self._gps_loc,
        }
        return self.async_show_form(
            step_id="gps_loc",
            data_schema=_get_schema_gps(self.hass, user_input, defaults),
            errors=self._errors,
        )

    async def async_step_zone(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        """Handle a flow for Zone ID."""
        self._errors = {}
        self._zone_list = await _get_zone_list(self)

        if user_input is not None:
            self._data.update(user_input)
            return self.async_create_entry(title=self._data[CONF_NAME], data=self._data)
        return await self._show_config_zone(user_input)

    async def _show_config_zone(
        self, user_input: dict[str, Any] | None
    ) -> FlowResult:
        """Show the configuration form for Zone ID."""
        defaults: dict[str, Any] = {
            CONF_NAME: DEFAULT_NAME,
            CONF_INTERVAL: DEFAULT_INTERVAL,
            CONF_TIMEOUT: DEFAULT_TIMEOUT,
            CONF_ZONE_ID: self._zone_list,
        }
        return self.async_show_form(
            step_id="zone",
            data_schema=_get_schema_zone(self.hass, user_input, defaults),
            errors=self._errors,
        )

    @staticmethod
    @callback
    def async_get_options_flow(config_entry: ConfigEntry) -> NWSAlertsOptionsFlow:
        return NWSAlertsOptionsFlow(config_entry)


class NWSAlertsOptionsFlow(config_entries.OptionsFlow):
    """Options flow for NWS Individual Alerts."""

    def __init__(self, config_entry: ConfigEntry) -> None:
        """Initialize."""
        self.config = config_entry
        self._data: dict[str, Any] = dict(config_entry.data)
        self._errors: dict[str, str] = {}

    async def async_step_init(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        """Manage options."""
        if user_input is not None:
            self._data.update(user_input)
            return self.async_create_entry(title="", data=self._data)
        return await self._show_options_form(user_input)

    async def async_step_gps_loc(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        """Handle GPS coordinates options."""
        self._errors = {}
        if user_input is not None:
            self._data.update(user_input)
            return self.async_create_entry(title="", data=self._data)
        return await self._show_options_form(user_input)

    async def async_step_gps_tracker(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        """Handle device tracker options."""
        self._errors = {}
        if user_input is not None:
            self._data.update(user_input)
            return self.async_create_entry(title="", data=self._data)
        return await self._show_options_form(user_input)

    async def async_step_zone(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        """Handle Zone ID options."""
        self._errors = {}
        if user_input is not None:
            self._data.update(user_input)
            return self.async_create_entry(title="", data=self._data)
        return await self._show_options_form(user_input)

    async def _show_options_form(
        self, user_input: dict[str, Any] | None
    ) -> FlowResult:
        """Show the options form matching the current lookup method."""
        if CONF_GPS_LOC in self.config.data:
            return self.async_show_form(
                step_id="gps_loc",
                data_schema=_get_schema_gps(self.hass, user_input, self._data),
                errors=self._errors,
            )
        if CONF_ZONE_ID in self.config.data:
            return self.async_show_form(
                step_id="zone",
                data_schema=_get_schema_zone(self.hass, user_input, self._data),
                errors=self._errors,
            )
        return self.async_show_form(
            step_id="gps_tracker",
            data_schema=_get_schema_tracker(self.hass, user_input, self._data),
            errors=self._errors,
        )
