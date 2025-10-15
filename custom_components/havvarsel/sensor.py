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
from homeassistant.const import UnitOfTemperature, UnitOfLength, UnitOfSpeed
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

    # Create one entity per available variable. The coordinator's data will
    # contain 'variables' mapping after the first refresh. We register a
    # sensor entity for each variable; temperature sensor is enabled by
    # default, others are created disabled so the user can enable them
    # in the integration options.
    entities: list[HavvarselVariableSensor] = []

    # If coordinator already has data, instantiate sensors; otherwise create
    # a placeholder temperature sensor which will become available after first update.
    variables = coordinator.data.get("variables") if coordinator.data else None
    if variables:
        for varname in variables:
            entities.append(HavvarselVariableSensor(coordinator, entry, varname))
        _LOGGER.debug(
            "Havvarsel: creating sensors for variables: %s",
            ", ".join(list(variables.keys())),
        )
    else:
        # Create a temperature sensor as placeholder; after first update the
        # platform will be unloaded and reloaded with all available variables.
        entities.append(HavvarselVariableSensor(coordinator, entry, "temperature"))
        _LOGGER.debug(
            "Havvarsel: coordinator had no variables yet; created placeholder temperature sensor"
        )

    async_add_entities(entities, False)
    # Log which entities are created and their default enabled state
    try:
        for ent in entities:
            default_enabled = getattr(ent, "_attr_entity_registry_enabled_default", True)
            _LOGGER.debug(
                "Havvarsel: added entity for variable '%s' (enabled_by_default=%s)",
                getattr(ent, 'variable_name', 'temperature'),
                default_enabled,
            )
    except Exception:
        _LOGGER.debug("Havvarsel: failed to log entities added", exc_info=True)


class HavvarselVariableSensor(
    CoordinatorEntity[HavvarselDataUpdateCoordinator], SensorEntity
):
    """Generic sensor for a single Havvarsel variable."""

    _attr_has_entity_name = True

    def __init__(
        self,
        coordinator: HavvarselDataUpdateCoordinator,
        entry: ConfigEntry,
        variable_name: str,
    ) -> None:
        """Initialize the sensor for a variable (e.g. temperature)."""
        super().__init__(coordinator)
        self.variable_name = variable_name

        sensor_name = entry.data.get(CONF_SENSOR_NAME, DEFAULT_SENSOR_NAME)
        slug = entry.data.get("slug") or sensor_name.replace(" ", "_").lower()

        # Unique id includes slug, entry id and variable name
        self._attr_unique_id = f"{slug}_{entry.entry_id}_{variable_name}"

        # Device is the location, entity name is the measurement type
        self._attr_name = variable_name.replace("_", " ").capitalize()

        # Device info
        self._attr_device_info = DeviceInfo(
            identifiers={(DOMAIN, entry.entry_id)},
            name=f"Havvarsel {sensor_name}",
            manufacturer="IMR, Norway",
            entry_type=DeviceEntryType.SERVICE,
            configuration_url="https://api.havvarsel.no",
        )

        # By default only temperature will be enabled; others are created disabled
        if variable_name != "temperature":
            self._attr_entity_registry_enabled_default = False

        # Device class for temperature and state class for numeric measurements
        if variable_name == "temperature":
            self._attr_device_class = SensorDeviceClass.TEMPERATURE
            self._attr_state_class = SensorStateClass.MEASUREMENT

        else:
            # Default to MEASUREMENT for other numeric variables
            self._attr_state_class = SensorStateClass.MEASUREMENT

        # Do not set static native unit here; we will determine it dynamically
        # from the API metadata via the native_unit_of_measurement property.

    @property
    def native_value(self) -> float | None:
        """Return the current value for this variable from coordinator data."""
        data = self.coordinator.data
        if not data:
            return None

        variables = data.get("variables", {})
        var = variables.get(self.variable_name)
        if not var:
            return None

        return var.get("current")

    @property
    def native_unit_of_measurement(self) -> str | None:
        """Return the unit of measurement for this variable based on API metadata."""
        data = self.coordinator.data
        if not data:
            return None

        variables = data.get("variables", {})
        var = variables.get(self.variable_name)
        if not var:
            return None

        # metadata is a list of dicts with keys 'key' and 'value'
        metadata = var.get("metadata", [])
        units = None
        for meta in metadata:
            if meta.get("key") == "units":
                units = meta.get("value")
                break

        if not units:
            # No units provided
            return None

        # Normalize and map API unit strings to HA unit constants
        u = str(units).strip().lower()

        # Common mappings
        if u in ("°c", "c", "celsius", "degc") or "c" == u:
            return UnitOfTemperature.CELSIUS
        if u in ("m", "meter", "metre", "meters", "metres"):
            return UnitOfLength.METERS
        if u in ("m/s", "m s-1", "ms-1") or "/s" in u:
            return UnitOfSpeed.METERS_PER_SECOND

        # Fall back to raw units string if no mapping exists (HA expects standard units; unknown units will be left unset)
        return None

    @property
    def extra_state_attributes(self) -> dict[str, Any] | None:
        """Return attributes including the forecast series and location info."""
        data = self.coordinator.data
        if not data:
            return None

        variables = data.get("variables", {})
        var = variables.get(self.variable_name)
        if not var:
            return None

        attrs = {
            "metadata": var.get("metadata", []),
            "series": var.get("series", []),
            "longitude": data.get("longitude"),
            "latitude": data.get("latitude"),
            "nearest_grid": data.get("nearest_grid"),
        }

        return attrs

    @property
    def available(self) -> bool:
        return self.coordinator.last_update_success and self.coordinator.data is not None
