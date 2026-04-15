"""Tests for the AlertsDataUpdateCoordinator and API fetch logic."""

import pytest
from homeassistant.helpers.update_coordinator import UpdateFailed
from pytest_homeassistant_custom_component.common import MockConfigEntry

from custom_components.nws_individual_alerts.const import DOMAIN
from custom_components.nws_individual_alerts.coordinator import async_fetch_alerts, async_get_alerts
from tests.conftest import POINT_URL, ZONE_URL
from tests.const import CONFIG_DATA, CONFIG_DATA_3

TEST_USER_AGENT = "github.com/austinmroczek/nws_alerts (test-entry-id)"

pytestmark = pytest.mark.asyncio


# ---------------------------------------------------------------------------
# async_get_alerts — low-level API function
# ---------------------------------------------------------------------------

async def test_async_get_alerts_zone_returns_data(hass, mock_api):
    """Fetching by zone ID returns parsed alert data."""
    result = await async_get_alerts(hass, TEST_USER_AGENT, zone_id="AZZ540,AZC013")
    assert result["state"] == 2
    assert len(result["alerts"]) == 2
    assert "last_updated" in result


async def test_async_get_alerts_point_returns_data(hass, mock_api):
    """Fetching by GPS coordinates returns parsed alert data."""
    result = await async_get_alerts(hass, TEST_USER_AGENT, gps_loc="123,-456")
    assert result["state"] == 2
    assert len(result["alerts"]) == 2


async def test_async_get_alerts_empty_response(hass, mock_api_empty):
    """Empty features list returns state=0 and empty alerts list."""
    result = await async_get_alerts(hass, TEST_USER_AGENT, zone_id="AZZ540,AZC013")
    assert result["state"] == 0
    assert result["alerts"] == []


async def test_async_get_alerts_no_args_returns_empty(hass, mock_aioclient):
    """Calling with no zone_id or gps_loc returns an empty dict without hitting the API."""
    result = await async_get_alerts(hass, TEST_USER_AGENT)
    assert result == {}


async def test_async_get_alerts_api_error_raises(hass, mock_api_error):
    """Non-200 API response raises UpdateFailed."""
    with pytest.raises(UpdateFailed, match="HTTP 500"):
        await async_get_alerts(hass, TEST_USER_AGENT, zone_id="AZZ540,AZC013")


async def test_async_get_alerts_unknown_event_logs_warning(hass, mock_api_unknown_event, caplog):
    """Alert types not in any sensor group emit a warning log."""
    import logging
    with caplog.at_level(logging.WARNING, logger="custom_components.nws_individual_alerts.coordinator"):
        await async_get_alerts(hass, TEST_USER_AGENT, zone_id="AZZ540,AZC013")
    assert "Completely Unknown Event Warning" in caplog.text
    assert "not mapped to any sensor group" in caplog.text


async def test_async_get_alerts_known_event_no_warning(hass, mock_api, caplog):
    """Known alert types do not emit an unknown-type warning."""
    import logging
    with caplog.at_level(logging.WARNING, logger="custom_components.nws_individual_alerts.coordinator"):
        await async_get_alerts(hass, TEST_USER_AGENT, zone_id="AZZ540,AZC013")
    assert "not mapped to any sensor group" not in caplog.text


# ---------------------------------------------------------------------------
# async_fetch_alerts — routing based on config
# ---------------------------------------------------------------------------

async def test_async_fetch_alerts_routes_zone(hass, mock_aioclient):
    """Zone ID config calls the zone URL."""
    mock_aioclient.get(ZONE_URL, status=200, body='{"features": []}')
    result = await async_fetch_alerts(hass, CONFIG_DATA, None, TEST_USER_AGENT)
    assert result["state"] == 0


async def test_async_fetch_alerts_routes_gps(hass, mock_aioclient):
    """GPS location config calls the point URL."""
    mock_aioclient.get(POINT_URL, status=200, body='{"features": []}')
    result = await async_fetch_alerts(hass, CONFIG_DATA_3, None, TEST_USER_AGENT)
    assert result["state"] == 0


async def test_async_fetch_alerts_uses_tracker_coords(hass, mock_aioclient):
    """Tracker config uses the provided coords instead of stored gps_loc."""
    tracker_url = "https://api.weather.gov/alerts/active?point=45,-90"
    mock_aioclient.get(tracker_url, status=200, body='{"features": []}')
    tracker_config = {"name": "Home", "tracker": "device_tracker.phone"}
    result = await async_fetch_alerts(hass, tracker_config, "45,-90", TEST_USER_AGENT)
    assert result["state"] == 0


# ---------------------------------------------------------------------------
# Coordinator — error recovery
# ---------------------------------------------------------------------------

async def test_coordinator_preserves_state_on_api_error(hass, mock_api, mock_aioclient):
    """After a successful load, a failed refresh keeps the last known state."""
    entry = MockConfigEntry(domain=DOMAIN, title="NWS Alerts", data=CONFIG_DATA)
    entry.add_to_hass(hass)
    assert await hass.config_entries.async_setup(entry.entry_id)
    await hass.async_block_till_done()

    from custom_components.nws_individual_alerts.const import COORDINATOR
    coordinator = hass.data[DOMAIN][entry.entry_id][COORDINATOR]

    # Confirm initial data loaded successfully
    assert coordinator.data["state"] == 2

    # Now make the API fail and trigger a refresh
    mock_aioclient.get(ZONE_URL, status=500)
    await coordinator.async_refresh()
    await hass.async_block_till_done()

    # Data should be preserved from the last successful fetch
    assert coordinator.data["state"] == 2
