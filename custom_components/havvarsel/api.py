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

    async def async_get_projection(self) -> dict[str, Any]:
        """Fetch full projection data for all variables and parse into a structured dict."""
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
                    return self._parse_projection_response(data)
        except aiohttp.ClientError as err:
            _LOGGER.error("Error fetching projection data: %s", err)
            raise
        except Exception as err:
            _LOGGER.error("Unexpected error: %s", err)
            raise

    def _parse_projection_response(self, data: dict[str, Any]) -> dict[str, Any]:
        """Parse projection response into variables dict and meta info."""
        try:
            variables_list = data.get("variables", [])
            variables: dict[str, Any] = {}

            for var in variables_list:
                # variableName seems to be the key used by the API
                name = var.get("variableName") or var.get("variable")
                metadata = var.get("metadata", [])
                series = []
                for projection in var.get("data", []):
                    raw_time = projection.get("rawTime", 0)
                    dt = datetime.fromtimestamp(raw_time / 1000, tz=dtUTC)
                    series.append({
                        "timestamp": dt.isoformat(),
                        "value": projection.get("value"),
                    })

                # Determine nearest/current value (closest to now)
                current_value = None
                if series:
                    now_ms = datetime.now(dtUTC).timestamp() * 1000
                    nearest = min(var.get("data", []), key=lambda x: abs(x.get("rawTime", 0) - now_ms))
                    current_value = nearest.get("value")

                variables[name] = {
                    "metadata": metadata,
                    "series": series,
                    "current": current_value,
                }

            closest_grid = data.get(
                "closestGridPointWithData",
                {"lat": self._latitude, "lon": self._longitude},
            )

            return {
                "variables": variables,
                "nearest_grid": closest_grid,
                "longitude": self._longitude,
                "latitude": self._latitude,
            }

        except Exception as err:
            _LOGGER.error("Error parsing projection response: %s", err)
            raise

    async def async_get_temperature_data(self) -> dict[str, Any]:
        """Fetch only temperature-centric data for compatibility.

        This wraps the full projection call but returns a similar shape to the
        original async_get_temperature_data for existing callers (title/nearest
        info)."""
        projection = await self.async_get_projection()

        # Try to extract temperature info for backward compatibility
        variables = projection.get("variables", {})
        temp = variables.get("temperature") or next(iter(variables.values()), None)

        current_temp = None
        timestamp = None
        forecast = []
        if temp:
            current_temp = temp.get("current")
            # Convert series to old forecast format if present
            for entry in temp.get("series", []):
                forecast.append({"timestamp": entry.get("timestamp"), "temperature": entry.get("value")})

            if temp.get("series"):
                # Find nearest timestamp from series
                now_iso = datetime.now(dtUTC).isoformat()
                timestamp = temp.get("series")[0].get("timestamp")

        nearest_grid = projection.get("nearest_grid", {})

        return {
            "current_temperature": current_temp,
            "timestamp": timestamp,
            "longitude": projection.get("longitude"),
            "latitude": projection.get("latitude"),
            "nearest_grid_lon": nearest_grid.get("lon"),
            "nearest_grid_lat": nearest_grid.get("lat"),
            "forecast": forecast,
        }
