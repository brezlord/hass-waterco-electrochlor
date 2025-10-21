"""Sensor platform for Waterco Electrochlor integration."""
from __future__ import annotations

import logging
from typing import Any

from homeassistant.components.sensor import SensorEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import DOMAIN
from .coordinator import ElectrochlorDataUpdateCoordinator
from .device_info import make_device_info
from .device_icons import ICONS

_LOGGER = logging.getLogger(__name__)

SENSOR_CONFIG: list[dict[str, Any]] = [
    {"key": "temp", "name": "Pool Temperature", "unit": "°C", "round": 1},
    {"key": "ph", "name": "Pool pH", "unit": "pH", "round": 2},
    {"key": "chlorineProduction", "name": "Pool Chlorine Production"},
    {"key": "operation", "name": "Pool Operation Mode"},
    {"key": "operationType", "name": "Pool Operation Type"},
    {"key": "pumpSpeed", "name": "Pool Pump Speed", "unit": "RPM"},
    {"key": "lightColor", "name": "Pool Light Colour"},
    {"key": "saltStatus", "name": "Pool Salt Status"},
    {"key": "error", "name": "Pool Chlorinator Status", "special": "error"},
    {"key": "status", "name": "Pool Chlorinator Cell Direction", "special": "cell_direction"},
]


def find_key(data: dict[str, Any], target_key: str) -> Any:
    """
    Recursively search for a key in nested dictionaries.
    Returns the value if found, else None.
    """
    if isinstance(data, dict):
        if target_key in data:
            return data[target_key]
        for value in data.values():
            found = find_key(value, target_key)
            if found is not None:
                return found
    return None


async def async_setup_entry(
    hass: HomeAssistant, entry: ConfigEntry, async_add_entities: AddEntitiesCallback
) -> None:
    """Set up Electrochlor sensors."""
    coordinator: ElectrochlorDataUpdateCoordinator = hass.data[DOMAIN][entry.entry_id]
    sensors = [GenericPoolSensor(coordinator, entry, cfg) for cfg in SENSOR_CONFIG]
    async_add_entities(sensors)


class GenericPoolSensor(CoordinatorEntity[ElectrochlorDataUpdateCoordinator], SensorEntity):
    """Generic pool sensor entity with dynamic icons and auto key detection."""

    def __init__(
        self,
        coordinator: ElectrochlorDataUpdateCoordinator,
        entry: ConfigEntry,
        config: dict[str, Any],
    ) -> None:
        super().__init__(coordinator)
        self._entry = entry
        self.config = config
        self._attr_name = config["name"]
        self._attr_unique_id = f"{entry.entry_id}_{config['key']}"
        self._attr_native_unit_of_measurement = config.get("unit")

    @property
    def native_value(self) -> Any:
        """Return the sensor's current state using auto key detection."""
        data = self.coordinator.data or {}
        key = self.config["key"]
        special = self.config.get("special")

        if special == "error":
            return "Error" if find_key(data, "error") else "OK"

        if special == "cell_direction":
            status = find_key(data, "status") or {}
            if status.get("cellDirectionA"):
                return "A"
            elif status.get("cellDirectionB"):
                return "B"
            return "Off"

        value = find_key(data, key)

        if value is None:
            _LOGGER.debug("Sensor %s (%s) is unavailable, data: %s", self.name, key, data)
            return "unavailable"

        # Round numeric values if requested
        if "round" in self.config and isinstance(value, (int, float)):
            value = round(value, self.config["round"])

        return value

    @property
    def icon(self) -> str:
        key = self.config["key"]
        value = self.native_value
        icons_for_key = ICONS.get(key, {})
        if str(value).lower() in ["true", "on"]:
            return icons_for_key.get("on", icons_for_key.get("default", "mdi:help-circle"))
        if str(value).lower() in ["false", "off"]:
            return icons_for_key.get("off", icons_for_key.get("default", "mdi:help-circle"))
        if value in icons_for_key:
            return icons_for_key[value]
        return icons_for_key.get("default", "mdi:help-circle")

    @property
    def available(self) -> bool:
        return self.coordinator.last_update_success

    async def async_update(self) -> None:
        await self.coordinator.async_request_refresh()

    @property
    def device_info(self):
        api_data = self.coordinator.data if isinstance(self.coordinator.data, dict) else None
        return make_device_info(self._entry, api_data)
