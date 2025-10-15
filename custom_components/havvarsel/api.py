"""API client for Havvarsel."""
from __future__ import annotations

from datetime import datetime, UTC as dtUTC
import logging
from typing import Any

import aiohttp
import async_timeout

_LOGGER = logging.getLogger(__name__)


class HavvarselApiClient:
    """API client for Havvarsel."""

    def __init__(
        self,
        session: aiohttp.ClientSession,
        longitude: float,
        latitude: float,
        depth: int = 0,
    ) -> None:
        """Initialize the API client."""
        self._session = session
        self._longitude = longitude
        self._latitude = latitude
        self._depth = depth
        self._base_url = "https://api.havvarsel.no/apis/duapi/havvarsel/v2/"
        self._projection_url = f"{self._base_url}temperatureprojection"
        self._variables_url = f"{self._base_url}variables"

    async def async_get_units(self) -> str:
        """Get the unit of measurement for temperature from the API."""
        try:
            headers = {
                "User-agent": "Home Assistant",
                "Content-type": "application/json",
            }
            async with async_timeout.timeout(10):
                async with self._session.get(
                    self._variables_url, headers=headers
                ) as response:
                    response.raise_for_status()
                    data = await response.json()
                    
                    variables = data.get("row", [])
                    for variable in variables:
                        if variable.get("variableName") == "temperature":
                            metadata = variable.get("metadata", [])
                            for meta in metadata:
                                if meta.get("key") == "units":
                                    return meta.get("value", "°C")
                    
                    return "°C"  # Default fallback
        except Exception as err:
            _LOGGER.error("Error fetching units: %s", err)
            return "°C"

    async def async_get_temperature_data(self) -> dict[str, Any]:
        """Fetch temperature data from Havvarsel API."""
        url = f"{self._projection_url}/{self._longitude}/{self._latitude}"
        params = {"depth": self._depth}
        
        headers = {
            "User-agent": "Home Assistant",
            "Content-type": "application/json",
        }

        try:
            async with async_timeout.timeout(10):
                async with self._session.get(
                    url, params=params, headers=headers
                ) as response:
                    response.raise_for_status()
                    data = await response.json()
                    return self._parse_response(data)
        except aiohttp.ClientError as err:
            _LOGGER.error("Error fetching temperature data: %s", err)
            raise
        except Exception as err:
            _LOGGER.error("Unexpected error: %s", err)
            raise

    def _parse_response(self, data: dict[str, Any]) -> dict[str, Any]:
        """Parse the API response."""
        try:
            variables = data.get("variables", [])
            if not variables:
                raise ValueError("No variables in response")

            temperature_data = variables[0].get("data", [])
            if not temperature_data:
                raise ValueError("No temperature data in response")

            # Find the temperature closest to current time
            current_time = datetime.now(dtUTC).timestamp() * 1000
            nearest = min(temperature_data, key=lambda x: abs(x.get("rawTime", 0) - current_time))
            
            current_temp = nearest.get("value")
            nearest_time = datetime.fromtimestamp(
                nearest.get("rawTime", 0) / 1000, tz=dtUTC
            ).isoformat()

            # Build forecast list
            forecast = []
            for projection in temperature_data:
                raw_time = projection.get("rawTime", 0)
                dt = datetime.fromtimestamp(raw_time / 1000, tz=dtUTC)
                forecast.append({
                    "timestamp": dt.isoformat(),
                    "temperature": projection.get("value"),
                })

            # Sort forecast by timestamp
            forecast.sort(key=lambda x: x["timestamp"])

            # Get closest grid point
            closest_grid = data.get(
                "closestGridPointWithData",
                {"lat": self._latitude, "lon": self._longitude},
            )

            return {
                "current_temperature": current_temp,
                "timestamp": nearest_time,
                "longitude": self._longitude,
                "latitude": self._latitude,
                "nearest_grid_lon": closest_grid.get("lon"),
                "nearest_grid_lat": closest_grid.get("lat"),
                "forecast": forecast,
            }

        except (KeyError, ValueError, IndexError) as err:
            _LOGGER.error("Error parsing response: %s", err)
            raise
