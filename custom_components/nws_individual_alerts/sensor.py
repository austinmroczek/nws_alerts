from __future__ import annotations

import logging
from typing import Final

from homeassistant.components.sensor import (
    SensorDeviceClass,
    SensorEntity,
    SensorEntityDescription,
    SensorStateClass,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import CONF_NAME, EntityCategory
from homeassistant.core import HomeAssistant
from homeassistant.helpers.device_registry import DeviceEntryType, DeviceInfo
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity
from homeassistant.util import slugify

from .alert_types import ALERT_GROUPS
from .const import ATTRIBUTION, COORDINATOR, DOMAIN

SENSOR_TYPES: Final[dict[str, SensorEntityDescription]] = {
    "state": SensorEntityDescription(
        key="state",
        name="Alert Count",
        translation_key="alert_count",
        icon="mdi:alert",
        state_class=SensorStateClass.MEASUREMENT,
    ),
    "last_updated": SensorEntityDescription(
        key="last_updated",
        name="Last Updated",
        translation_key="last_updated",
        icon="mdi:update",
        device_class=SensorDeviceClass.TIMESTAMP,
        entity_category=EntityCategory.DIAGNOSTIC,
    ),
}

# ---------------------------------------------------------
# API Documentation
# ---------------------------------------------------------
# https://www.weather.gov/documentation/services-web-api
# ---------------------------------------------------------

_LOGGER = logging.getLogger(__name__)

# Severity rank used to pick the highest active level.
_SEVERITY: dict[str, int] = {"none": 0, "advisory": 1, "watch": 2, "warning": 3}


def _event_level(event: str) -> str:
    """Return advisory/watch/warning for a NWS event type name."""
    lower = event.lower()
    if lower.endswith("warning"):
        return "warning"
    if lower.endswith("watch"):
        return "watch"
    return "advisory"


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Setup the sensor platform."""
    coordinator = hass.data[DOMAIN][entry.entry_id][COORDINATOR]
    sensors: list[SensorEntity] = [
        NWSAlertSensor(hass, entry, sensor) for sensor in SENSOR_TYPES.values()
    ]
    sensors += [
        NWSAlertGroupSensor(coordinator, entry, name, alert_types)
        for name, alert_types in ALERT_GROUPS.items()
    ]
    async_add_entities(sensors, False)


def _device_info(entry: ConfigEntry) -> DeviceInfo:
    """Return device registry information shared by all sensors for this entry."""
    return DeviceInfo(
        entry_type=DeviceEntryType.SERVICE,
        identifiers={(DOMAIN, entry.entry_id)},
        manufacturer="NWS",
        name=entry.title,
    )


class NWSAlertSensor(CoordinatorEntity, SensorEntity):
    """Representation of a Sensor."""

    _attr_has_entity_name = True
    _attr_attribution = ATTRIBUTION

    def __init__(
        self,
        hass: HomeAssistant,
        entry: ConfigEntry,
        sensor_description: SensorEntityDescription,
    ) -> None:
        """Initialize the sensor."""
        super().__init__(hass.data[DOMAIN][entry.entry_id][COORDINATOR])
        self._config = entry
        self._key = sensor_description.key

        self._attr_icon = sensor_description.icon
        self._attr_name = sensor_description.name
        self._attr_translation_key = sensor_description.translation_key
        self._attr_device_class = sensor_description.device_class
        self._attr_state_class = sensor_description.state_class
        self._attr_entity_category = sensor_description.entity_category
        # Preserve the pre-existing unique_id format for backwards compatibility
        self._attr_unique_id = f"{slugify(f'{entry.data[CONF_NAME]} {sensor_description.name}')}_{entry.entry_id}"

    @property
    def native_value(self) -> int | None:
        """Return the state of the sensor."""
        if self.coordinator.data is None:
            return None
        elif self._key in self.coordinator.data:
            return self.coordinator.data[self._key]
        return None

    @property
    def extra_state_attributes(self) -> dict:
        """Return the state attributes."""
        attrs = {}
        if self.coordinator.data is None:
            return attrs
        if "alerts" in self.coordinator.data and self._key == "state":
            attrs["Alerts"] = self.coordinator.data["alerts"]
        return attrs

    @property
    def device_info(self) -> DeviceInfo:
        """Return device registry information."""
        return _device_info(self._config)


class NWSAlertGroupSensor(CoordinatorEntity, SensorEntity):
    """Sensor that reports the highest active severity level for one alert topic."""

    _attr_has_entity_name = True
    _attr_attribution = ATTRIBUTION
    _attr_device_class = SensorDeviceClass.ENUM
    _attr_options = ["none", "advisory", "watch", "warning"]

    _STATE_ICONS: dict[str, str] = {
        "advisory": "mdi:information",
        "watch":    "mdi:eye",
        "warning":  "mdi:alert",
    }

    @property
    def icon(self) -> str:
        """Return an icon reflecting the current severity level."""
        return self._STATE_ICONS.get(self.native_value, "mdi:check-circle-outline")

    def __init__(
        self,
        coordinator,
        entry: ConfigEntry,
        name: str,
        alert_types: frozenset[str],
    ) -> None:
        """Initialize the group sensor."""
        super().__init__(coordinator)
        self._config = entry
        self._alert_types = alert_types
        self._attr_name = name
        self._attr_translation_key = slugify(name)
        self._attr_unique_id = f"{slugify(name)}_{entry.entry_id}"

    @property
    def native_value(self) -> str:
        """Return the highest active severity level."""
        if self.coordinator.data is None or "alerts" not in self.coordinator.data:
            return "none"
        active = [
            alert for alert in self.coordinator.data["alerts"]
            if alert["Event"] in self._alert_types
        ]
        if not active:
            return "none"
        return max((_event_level(alert["Event"]) for alert in active), key=_SEVERITY.get)

    @property
    def extra_state_attributes(self) -> dict:
        """Return active alert event names and full details. Always present for template consistency."""
        if self.coordinator.data is None or "alerts" not in self.coordinator.data:
            return {"active_alerts": [], "alerts": []}
        active = [
            alert for alert in self.coordinator.data["alerts"]
            if alert["Event"] in self._alert_types
        ]
        return {
            "active_alerts": [alert["Event"] for alert in active],
            "alerts": active,
        }

    @property
    def device_info(self) -> DeviceInfo:
        """Return device registry information."""
        return _device_info(self._config)
