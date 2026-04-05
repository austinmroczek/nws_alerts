"""Tests for integration setup and teardown."""

import pytest
from homeassistant.components.sensor import DOMAIN as SENSOR_DOMAIN
from pytest_homeassistant_custom_component.common import MockConfigEntry

from custom_components.nws_individual_alerts.alert_types import ALERT_GROUPS
from custom_components.nws_individual_alerts.const import DOMAIN
from tests.const import CONFIG_DATA, CONFIG_DATA_3

pytestmark = pytest.mark.asyncio

# 2 main sensors (Alerts + Last Updated) + one per alert group
EXPECTED_SENSOR_COUNT = 2 + len(ALERT_GROUPS)


async def test_setup_entry(hass, mock_api):
    """Integration sets up the correct number of sensors."""
    entry = MockConfigEntry(domain=DOMAIN, title="NWS Alerts", data=CONFIG_DATA)
    entry.add_to_hass(hass)

    assert await hass.config_entries.async_setup(entry.entry_id)
    await hass.async_block_till_done()

    assert "nws_individual_alerts" in hass.config.components
    assert len(hass.states.async_entity_ids(SENSOR_DOMAIN)) == EXPECTED_SENSOR_COUNT
    assert len(hass.config_entries.async_entries(DOMAIN)) == 1


async def test_setup_entry_gps(hass, mock_api):
    """Integration sets up correctly with a GPS location config."""
    entry = MockConfigEntry(domain=DOMAIN, title="NWS Alerts", data=CONFIG_DATA_3)
    entry.add_to_hass(hass)

    assert await hass.config_entries.async_setup(entry.entry_id)
    await hass.async_block_till_done()

    assert len(hass.states.async_entity_ids(SENSOR_DOMAIN)) == EXPECTED_SENSOR_COUNT


async def test_unload_entry(hass, mock_api):
    """Unloading an entry removes all sensor states."""
    entry = MockConfigEntry(domain=DOMAIN, title="NWS Alerts", data=CONFIG_DATA_3)
    entry.add_to_hass(hass)

    assert await hass.config_entries.async_setup(entry.entry_id)
    await hass.async_block_till_done()
    assert len(hass.states.async_entity_ids(SENSOR_DOMAIN)) == EXPECTED_SENSOR_COUNT

    entries = hass.config_entries.async_entries(DOMAIN)
    assert len(entries) == 1

    assert await hass.config_entries.async_unload(entries[0].entry_id)
    await hass.async_block_till_done()

    assert await hass.config_entries.async_remove(entries[0].entry_id)
    await hass.async_block_till_done()
    assert len(hass.states.async_entity_ids(SENSOR_DOMAIN)) == 0
