"""Fixtures for tests."""

import os
from unittest.mock import patch

import pytest
from aioresponses import aioresponses

pytest_plugins = "pytest_homeassistant_custom_component"

API_URL = "https://api.weather.gov"
ZONE_URL = "https://api.weather.gov/alerts/active?zone=AZZ540,AZC013"
POINT_URL = "https://api.weather.gov/alerts/active?point=123,-456"


# This fixture enables loading custom integrations in all tests.
@pytest.fixture(autouse=True)
def auto_enable_custom_integrations(enable_custom_integrations):
    """Enable custom integration tests."""
    yield


# Prevent HomeAssistant from attempting to create/dismiss persistent notifications.
@pytest.fixture(name="skip_notifications", autouse=True)
def skip_notifications_fixture():
    """Skip notification calls."""
    with patch("homeassistant.components.persistent_notification.async_create"), patch(
        "homeassistant.components.persistent_notification.async_dismiss"
    ):
        yield


def load_fixture(filename):
    """Load a fixture file as a string."""
    path = os.path.join(os.path.dirname(__file__), "fixtures", filename)
    with open(path, encoding="utf-8") as fptr:
        return fptr.read()


@pytest.fixture
def mock_aioclient():
    """Fixture to mock aiohttp calls."""
    with aioresponses() as m:
        yield m


@pytest.fixture(name="mock_api")
def mock_api(mock_aioclient):
    """Mock the NWS API with two active alerts (Excessive Heat Warning + Air Quality Alert)."""
    mock_aioclient.get(ZONE_URL, status=200, body=load_fixture("api.json"), repeat=True)
    mock_aioclient.get(POINT_URL, status=200, body=load_fixture("api.json"), repeat=True)
    yield mock_aioclient


@pytest.fixture(name="mock_api_empty")
def mock_api_empty(mock_aioclient):
    """Mock the NWS API with no active alerts."""
    mock_aioclient.get(ZONE_URL, status=200, body=load_fixture("empty_api.json"), repeat=True)
    mock_aioclient.get(POINT_URL, status=200, body=load_fixture("empty_api.json"), repeat=True)
    yield mock_aioclient


@pytest.fixture(name="mock_api_tornado")
def mock_api_tornado(mock_aioclient):
    """Mock the NWS API with a Tornado Warning and a Flood Watch."""
    mock_aioclient.get(ZONE_URL, status=200, body=load_fixture("tornado_warning_api.json"), repeat=True)
    mock_aioclient.get(POINT_URL, status=200, body=load_fixture("tornado_warning_api.json"), repeat=True)
    yield mock_aioclient


@pytest.fixture(name="mock_api_unknown_event")
def mock_api_unknown_event(mock_aioclient):
    """Mock the NWS API with an alert type not in any sensor group."""
    mock_aioclient.get(ZONE_URL, status=200, body=load_fixture("unknown_event_api.json"), repeat=True)
    mock_aioclient.get(POINT_URL, status=200, body=load_fixture("unknown_event_api.json"), repeat=True)
    yield mock_aioclient


@pytest.fixture(name="mock_api_error")
def mock_api_error(mock_aioclient):
    """Mock the NWS API returning HTTP 500."""
    mock_aioclient.get(ZONE_URL, status=500, repeat=True)
    mock_aioclient.get(POINT_URL, status=500, repeat=True)
    yield mock_aioclient
