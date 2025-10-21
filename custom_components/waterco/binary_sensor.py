"""Binary sensor platform for Waterco Electrochlor integration."""
from __future__ import annotations

import logging
from typing import Any

from homeassistant.components.binary_sensor import BinarySensorEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import DOMAIN
from .coordinator import ElectrochlorDataUpdateCoordinator
from .device_info import make_device_info
from .device_icons import ICONS

_LOGGER = logging.getLogger(__name__)

BINARY_SENSOR_CONFIG: list[dict[str, Any]] = [
    {"key": "pump", "name": "Pool Pump", "device_class": "running"},
    {"key": "light", "name": "Pool Light"},
    {"key": "phPump", "name": "Pool pH Pump", "device_class": "running"},
    {"key": "valve", "name": "Pool Valve"},
    {"key": "aux2", "name": "Pool Aux2"},
    {"key": "cellDirectionA", "name": "Pool Chlorinator Cell Direction A"},
    {"key": "cellDirectionB", "name": "Pool Chlorinator Cell Direction B"},
    {"key": "error", "name": "Pool Chlorinator Error", "device_class": "problem", "special": "error"},
    {"key": "saltStatus", "name": "Pool Salt Fault", "device_class": "problem", "special": "salt_fault"},
]

async def async_setup_entry(
    hass: HomeAssistant, entry: ConfigEntry, async_add_entities: AddEntitiesCallback
) -> None:
    """Set up Electrochlor binary sensors."""
    coordinator: ElectrochlorDataUpdateCoordinator = hass.data[DOMAIN][entry.entry_id]
    sensors = [GenericPoolBinarySensor(coordinator, entry, cfg) for cfg in BINARY_SENSOR_CONFIG]
    async_add_entities(sensors)


class GenericPoolBinarySensor(CoordinatorEntity[ElectrochlorDataUpdateCoordinator], BinarySensorEntity):
    """Binary sensor entity with dynamic icons."""

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
        self._attr_device_class = config.get("device_class")
        self._optimistic_state: bool | None = None

    @property
    def is_on(self) -> bool:
        """Return True if the binary sensor is on."""
        if self._optimistic_state is not None:
            return self._optimistic_state

        data = self.coordinator.data or {}
        result = data.get("result", {})
        status = result.get("status", {})
        key = self.config["key"]
        special = self.config.get("special")

        if special == "salt_fault":
            return result.get("saltStatus") == "FAULT" or result.get("saltStatus") == "fault"

        if special == "error":
            return bool(data.get("error", False))

        if key in ["cellDirectionA", "cellDirectionB"]:
            return bool(status.get(key, False))

        return bool(status.get(key, False))

    @property
    def icon(self) -> str:
        key = self.config["key"]
        state = self.is_on
        icons_for_key = ICONS.get(key, {})
        if state and "on" in icons_for_key:
            return icons_for_key["on"]
        if not state and "off" in icons_for_key:
            return icons_for_key["off"]
        return icons_for_key.get("default", "mdi:help-circle")

    @property
    def available(self) -> bool:
        return self.coordinator.last_update_success

    @property
    def device_info(self):
        api_data = self.coordinator.data.get("result") if isinstance(self.coordinator.data, dict) else None
        return make_device_info(self._entry, api_data)

    async def async_update(self) -> None:
        await self.coordinator.async_request_refresh()
