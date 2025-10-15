"""Sensor platform for Havvarsel."""
from __future__ import annotations

from datetime import datetime
import logging
from typing import Any

from homeassistant.components.sensor import (
    SensorDeviceClass,
    SensorEntity,
    SensorStateClass,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import UnitOfTemperature
from homeassistant.core import HomeAssistant
from homeassistant.helpers.device_registry import DeviceEntryType, DeviceInfo
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import CONF_SENSOR_NAME, DEFAULT_SENSOR_NAME, DOMAIN
from .coordinator import HavvarselDataUpdateCoordinator

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up the Havvarsel sensor."""
    coordinator: HavvarselDataUpdateCoordinator = hass.data[DOMAIN][entry.entry_id]

    async_add_entities(
        [HavvarselTemperatureSensor(coordinator, entry)],
        False,
    )


class HavvarselTemperatureSensor(
    CoordinatorEntity[HavvarselDataUpdateCoordinator], SensorEntity
):
    """Representation of a Havvarsel temperature sensor."""

    _attr_device_class = SensorDeviceClass.TEMPERATURE
    _attr_state_class = SensorStateClass.MEASUREMENT
    _attr_native_unit_of_measurement = UnitOfTemperature.CELSIUS
    _attr_has_entity_name = True

    def __init__(
        self,
        coordinator: HavvarselDataUpdateCoordinator,
        entry: ConfigEntry,
    ) -> None:
        """Initialize the sensor."""
        super().__init__(coordinator)
        
        sensor_name = entry.data.get(CONF_SENSOR_NAME, DEFAULT_SENSOR_NAME)
        
        self._attr_unique_id = f"{entry.entry_id}_temperature"
        self._attr_name = sensor_name
        
        self._attr_device_info = DeviceInfo(
            identifiers={(DOMAIN, entry.entry_id)},
            name=f"Havvarsel {sensor_name}",
            manufacturer="IMR, Norway",
            entry_type=DeviceEntryType.SERVICE,
            configuration_url="https://api.havvarsel.no",
        )

    @property
    def native_value(self) -> float | None:
        """Return the state of the sensor."""
        if self.coordinator.data:
            return self.coordinator.data.get("current_temperature")
        return None

    @property
    def extra_state_attributes(self) -> dict[str, Any] | None:
        """Return the state attributes."""
        if not self.coordinator.data:
            return None

        data = self.coordinator.data
        attributes = {
            "longitude": data.get("longitude"),
            "latitude": data.get("latitude"),
            "nearest_grid_lon": data.get("nearest_grid_lon"),
            "nearest_grid_lat": data.get("nearest_grid_lat"),
            "timestamp": data.get("timestamp"),
            "forecast": data.get("forecast", []),
        }

        return attributes

    @property
    def available(self) -> bool:
        """Return if entity is available."""
        return self.coordinator.last_update_success and self.coordinator.data is not None
