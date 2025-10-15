"""DataUpdateCoordinator for Havvarsel."""
from __future__ import annotations

from datetime import timedelta
import logging
from typing import Any

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.aiohttp_client import async_get_clientsession
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed

from .api import HavvarselApiClient
from .const import (
    CONF_DEPTH,
    CONF_LATITUDE,
    CONF_LONGITUDE,
    DEFAULT_DEPTH,
    DOMAIN,
    UPDATE_INTERVAL,
)

_LOGGER = logging.getLogger(__name__)


class HavvarselDataUpdateCoordinator(DataUpdateCoordinator[dict[str, Any]]):
    """Class to manage fetching Havvarsel data."""

    def __init__(self, hass: HomeAssistant, entry: ConfigEntry) -> None:
        """Initialize the coordinator."""
        self.entry = entry
        self.api = HavvarselApiClient(
            session=async_get_clientsession(hass),
            longitude=entry.data[CONF_LONGITUDE],
            latitude=entry.data[CONF_LATITUDE],
            depth=entry.data.get(CONF_DEPTH, DEFAULT_DEPTH),
        )

        super().__init__(
            hass,
            _LOGGER,
            name=DOMAIN,
            update_interval=timedelta(seconds=UPDATE_INTERVAL),
        )

    async def _async_update_data(self) -> dict[str, Any]:
        """Fetch data from API."""
        try:
            data = await self.api.async_get_temperature_data()
            return data
        except Exception as err:
            raise UpdateFailed(f"Error communicating with API: {err}") from err
