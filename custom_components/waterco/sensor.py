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
from .helpers import find_key

_LOGGER = logging.getLogger(__name__)


SENSOR_CONFIG: list[dict[str, Any]] = [
    {
        "key": "temp",
        "name": "Pool Temperature",
        "unit": "°C",
        "round": 1,
    },
    {
        "key": "ph",
        "name": "Pool pH",
        "unit": "pH",
        "round": 2,
    },
    {
        "key": "chlorineProduction",
        "name": "Pool Chlorine Production",
    },
    {
        "key": "operation",
        "name": "Pool Operation Mode",
    },
    {
        "key": "operationType",
        "name": "Pool Operation Type",
    },
    {
        "key": "pumpSpeed",
        "name": "Pool Pump Speed",
        "unit": "RPM",
    },
    {
        "key": "lightColor",
        "name": "Pool Light Colour",
    },
    {
        "key": "saltStatus",
        "name": "Pool Salt Status",
    },
    {
        "key": "error",
        "name": "Pool Chlorinator Status",
        "special": "error",
    },
    {
        "key": "status",
        "name": "Pool Chlorinator Cell Direction",
        "special": "cell_direction",
    },
]


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up Electrochlor sensors."""
    coordinator: ElectrochlorDataUpdateCoordinator = hass.data[DOMAIN][
        entry.entry_id
    ]

    sensors = [
        GenericPoolSensor(coordinator, entry, config)
        for config in SENSOR_CONFIG
    ]

    async_add_entities(sensors)


class GenericPoolSensor(
    CoordinatorEntity[ElectrochlorDataUpdateCoordinator],
    SensorEntity,
):
    """Generic pool sensor entity with dynamic icons and auto key detection."""

    def __init__(
        self,
        coordinator: ElectrochlorDataUpdateCoordinator,
        entry: ConfigEntry,
        config: dict[str, Any],
    ) -> None:
        """Initialize the sensor."""
        super().__init__(coordinator)

        self._entry = entry
        self.config = config

        self._attr_name = config["name"]
        self._attr_unique_id = f"{entry.entry_id}_{config['key']}"
        self._attr_native_unit_of_measurement = config.get("unit")

    @property
    def native_value(self) -> Any:
        """Return the sensor's current state."""
        data = self.coordinator.data or {}
        key = self.config["key"]
        special = self.config.get("special")

        # Chlorinator error status.
        if special == "error":
            return "Error" if find_key(data, "error") else "OK"

        # Cell direction.
        if special == "cell_direction":
            status = find_key(data, "status")

            if not isinstance(status, dict):
                return "Off"

            if status.get("cellDirectionA"):
                return "A"

            if status.get("cellDirectionB"):
                return "B"

            return "Off"

        value = find_key(data, key)

        if value is None:
            _LOGGER.debug(
                "Sensor %s (%s) is unavailable, data: %s",
                self.name,
                key,
                data,
            )
            return "unavailable"

        # Some Waterco API values are objects rather than scalar values.
        #
        # For example:
        #
        # "operationType": {
        #     "tag": "AUTO",
        #     "name": "Auto",
        #     ...
        # }
        #
        # Home Assistant sensors need a scalar state, so use the
        # human-readable name first, then the tag as a fallback.
        if isinstance(value, dict):
            value = (
                value.get("name")
                or value.get("tag")
                or str(value)
            )

        # Round numeric values if requested.
        if "round" in self.config and isinstance(value, (int, float)):
            value = round(value, self.config["round"])

        return value

    @property
    def icon(self) -> str:
        """Return the appropriate icon for the current sensor state."""
        key = self.config["key"]
        value = self.native_value
        icons_for_key = ICONS.get(key, {})

        value_string = str(value).lower()

        if value_string in ("true", "on"):
            return icons_for_key.get(
                "on",
                icons_for_key.get("default", "mdi:help-circle"),
            )

        if value_string in ("false", "off"):
            return icons_for_key.get(
                "off",
                icons_for_key.get("default", "mdi:help-circle"),
            )

        # Only dictionary-lookup hashable/string values.
        #
        # This prevents the original TypeError:
        # TypeError: cannot use 'dict' as a dict key
        if isinstance(value, str) and value in icons_for_key:
            return icons_for_key[value]

        return icons_for_key.get(
            "default",
            "mdi:help-circle",
        )

    @property
    def available(self) -> bool:
        """Return whether the coordinator is available."""
        return self.coordinator.last_update_success

    async def async_update(self) -> None:
        """Request an update from the coordinator."""
        await self.coordinator.async_request_refresh()

    @property
    def device_info(self):
        """Return device information."""
        api_data = (
            self.coordinator.data
            if isinstance(self.coordinator.data, dict)
            else None
        )

        return make_device_info(self._entry, api_data)