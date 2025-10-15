"""Config flow for Havvarsel integration."""
from __future__ import annotations

import logging
from typing import Any

import voluptuous as vol

from homeassistant import config_entries
from homeassistant.const import CONF_LATITUDE, CONF_LONGITUDE
from homeassistant.core import HomeAssistant
from homeassistant.data_entry_flow import FlowResult
from homeassistant.helpers.aiohttp_client import async_get_clientsession
import homeassistant.helpers.config_validation as cv

from .api import HavvarselApiClient
from .const import (
    CONF_DEPTH,
    CONF_SENSOR_NAME,
    DEFAULT_DEPTH,
    DEFAULT_SENSOR_NAME,
    DOMAIN,
)

_LOGGER = logging.getLogger(__name__)

STEP_USER_DATA_SCHEMA = vol.Schema(
    {
        vol.Required(CONF_SENSOR_NAME, default=DEFAULT_SENSOR_NAME): cv.string,
        vol.Required(CONF_LONGITUDE): cv.longitude,
        vol.Required(CONF_LATITUDE): cv.latitude,
        vol.Optional(CONF_DEPTH, default=DEFAULT_DEPTH): cv.positive_int,
    }
)


async def validate_input(hass: HomeAssistant, data: dict[str, Any]) -> dict[str, Any]:
    """Validate the user input allows us to connect.

    Data has the keys from STEP_USER_DATA_SCHEMA with values provided by the user.
    """
    session = async_get_clientsession(hass)
    api = HavvarselApiClient(
        session=session,
        longitude=data[CONF_LONGITUDE],
        latitude=data[CONF_LATITUDE],
        depth=data.get(CONF_DEPTH, DEFAULT_DEPTH),
    )

    # Test the connection by fetching data
    await api.async_get_temperature_data()

    # Return info that you want to store in the config entry.
    return {
        "title": data[CONF_SENSOR_NAME],
    }


class ConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a config flow for Havvarsel."""

    VERSION = 1

    async def async_step_user(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        """Handle the initial step."""
        errors: dict[str, str] = {}
        
        if user_input is not None:
            try:
                info = await validate_input(self.hass, user_input)
            except Exception:  # pylint: disable=broad-except
                _LOGGER.exception("Unexpected exception")
                errors["base"] = "cannot_connect"
            else:
                # Create a unique ID based on location and depth
                unique_id = f"{user_input[CONF_LATITUDE]}_{user_input[CONF_LONGITUDE]}_{user_input.get(CONF_DEPTH, DEFAULT_DEPTH)}"
                await self.async_set_unique_id(unique_id)
                self._abort_if_unique_id_configured()
                
                return self.async_create_entry(title=info["title"], data=user_input)

        return self.async_show_form(
            step_id="user",
            data_schema=STEP_USER_DATA_SCHEMA,
            errors=errors,
        )
