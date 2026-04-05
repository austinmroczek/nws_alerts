"""Tests for NWS Individual Alerts sensors."""

import pytest
from homeassistant.helpers import entity_registry as er
from pytest_homeassistant_custom_component.common import MockConfigEntry

from custom_components.nws_individual_alerts.const import DOMAIN
from tests.const import CONFIG_DATA, CONFIG_DATA_3

pytestmark = pytest.mark.asyncio

# Entity IDs use pattern: sensor.{device_name}_{entity_name} (slugified)
# Device name is "NWS Alerts", so prefix is "nws_alerts"
MAIN_SENSOR = "sensor.nws_alerts_alerts"
LAST_UPDATED_SENSOR = "sensor.nws_alerts_last_updated"

# Category sensors — fixture has Excessive Heat Warning + Air Quality Alert
HEAT_SENSOR = "sensor.nws_alerts_heat"
AIR_QUALITY_SENSOR = "sensor.nws_alerts_air_quality"
FLOOD_SENSOR = "sensor.nws_alerts_flood"
TORNADO_SENSOR = "sensor.nws_alerts_tornado"
WINTER_WEATHER_SENSOR = "sensor.nws_alerts_winter_weather"


async def _setup_entry(hass, data=CONFIG_DATA):
    entry = MockConfigEntry(domain=DOMAIN, title="NWS Alerts", data=data)
    entry.add_to_hass(hass)
    assert await hass.config_entries.async_setup(entry.entry_id)
    await hass.async_block_till_done()
    return entry


# ---------------------------------------------------------------------------
# Main sensor
# ---------------------------------------------------------------------------

async def test_main_sensor_count(hass, mock_api):
    """Main sensor state equals the number of active alerts."""
    await _setup_entry(hass)
    state = hass.states.get(MAIN_SENSOR)
    assert state is not None
    assert state.state == "2"


async def test_main_sensor_alerts_attribute(hass, mock_api):
    """Alerts attribute contains full detail for each active alert."""
    await _setup_entry(hass)
    state = hass.states.get(MAIN_SENSOR)
    alerts = state.attributes["Alerts"]
    assert len(alerts) == 2

    events = {a["Event"] for a in alerts}
    assert "Excessive Heat Warning" in events
    assert "Air Quality Alert" in events


async def test_main_sensor_alert_fields(hass, mock_api):
    """Each alert entry exposes all expected fields."""
    await _setup_entry(hass)
    alerts = hass.states.get(MAIN_SENSOR).attributes["Alerts"]
    heat_alert = next(a for a in alerts if a["Event"] == "Excessive Heat Warning")

    assert heat_alert["ID"] == "7681487b-41c6-0308-1a00-3cade72982c1"
    assert heat_alert["Type"] == "Update"
    assert heat_alert["Status"] == "Actual"
    assert heat_alert["Severity"] == "Severe"
    assert heat_alert["Certainty"] == "Likely"
    assert "AreasAffected" in heat_alert
    assert "Description" in heat_alert
    assert "Instruction" in heat_alert
    assert "Sent" in heat_alert
    assert "Onset" in heat_alert
    assert "Expires" in heat_alert
    assert "Ends" in heat_alert


async def test_main_sensor_registered(hass, mock_api):
    """Main sensor is registered in the entity registry."""
    await _setup_entry(hass)
    registry = er.async_get(hass)
    entity = registry.async_get(MAIN_SENSOR)
    assert entity is not None


async def test_main_sensor_empty_alerts(hass, mock_api_empty):
    """Main sensor shows 0 when there are no active alerts."""
    await _setup_entry(hass)
    state = hass.states.get(MAIN_SENSOR)
    assert state.state == "0"
    assert state.attributes.get("Alerts") == []


async def test_main_sensor_gps_lookup(hass, mock_api):
    """Main sensor works correctly with GPS coordinate lookup."""
    await _setup_entry(hass, data=CONFIG_DATA_3)
    state = hass.states.get(MAIN_SENSOR)
    assert state is not None
    assert state.state == "2"


# ---------------------------------------------------------------------------
# Category sensors — severity levels
# ---------------------------------------------------------------------------

async def test_category_sensor_warning(hass, mock_api):
    """Heat sensor reports 'warning' when an Excessive Heat Warning is active."""
    await _setup_entry(hass)
    state = hass.states.get(HEAT_SENSOR)
    assert state is not None
    assert state.state == "warning"


async def test_category_sensor_advisory(hass, mock_api):
    """Air Quality sensor reports 'advisory' when an Air Quality Alert is active."""
    await _setup_entry(hass)
    state = hass.states.get(AIR_QUALITY_SENSOR)
    assert state is not None
    assert state.state == "advisory"


async def test_category_sensor_none(hass, mock_api):
    """Sensors with no matching alerts report 'none'."""
    await _setup_entry(hass)
    for entity_id in (FLOOD_SENSOR, TORNADO_SENSOR, WINTER_WEATHER_SENSOR):
        state = hass.states.get(entity_id)
        assert state is not None, f"{entity_id} not found"
        assert state.state == "none", f"{entity_id} expected 'none', got {state.state!r}"


async def test_category_sensor_active_alerts_attribute(hass, mock_api):
    """Active category sensor exposes active_alerts and alerts attributes."""
    await _setup_entry(hass)
    state = hass.states.get(HEAT_SENSOR)
    assert state.attributes["active_alerts"] == ["Excessive Heat Warning"]
    assert len(state.attributes["alerts"]) == 1
    assert state.attributes["alerts"][0]["Event"] == "Excessive Heat Warning"


async def test_category_sensor_inactive_has_no_attributes(hass, mock_api):
    """Inactive category sensor has no active_alerts or alerts attributes."""
    await _setup_entry(hass)
    state = hass.states.get(FLOOD_SENSOR)
    assert "active_alerts" not in state.attributes
    assert "alerts" not in state.attributes


async def test_category_sensor_watch_level(hass, mock_api_tornado):
    """Flood sensor reports 'watch' when only a Flood Watch is active."""
    await _setup_entry(hass)
    state = hass.states.get(FLOOD_SENSOR)
    assert state.state == "watch"


async def test_category_sensor_warning_beats_watch(hass, mock_api_tornado):
    """Tornado sensor reports 'warning' (highest severity wins)."""
    await _setup_entry(hass)
    state = hass.states.get(TORNADO_SENSOR)
    assert state.state == "warning"


async def test_category_sensor_all_none_when_empty(hass, mock_api_empty):
    """All category sensors report 'none' when there are no active alerts."""
    await _setup_entry(hass)
    for entity_id in (HEAT_SENSOR, AIR_QUALITY_SENSOR, FLOOD_SENSOR, TORNADO_SENSOR):
        state = hass.states.get(entity_id)
        assert state is not None
        assert state.state == "none"
