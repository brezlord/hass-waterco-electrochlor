from __future__ import annotations

import logging
from homeassistant.components.binary_sensor import BinarySensorEntity
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import DOMAIN
from .device_info import get_device_info
from .device_icons import ICONS

_LOGGER = logging.getLogger(__name__)

BINARY_SENSOR_CONFIG = [
    {"key": "pump", "name": "Pool Pump", "device_class": "running", "status_key": "status"},
    {"key": "light", "name": "Pool Light", "status_key": "status"},
    {"key": "phPump", "name": "Pool pH Pump", "device_class": "running", "status_key": "status"},
    {"key": "valve", "name": "Pool Valve", "status_key": "status"},
    {"key": "aux2", "name": "Pool Aux2", "status_key": "status"},
    {"key": "cellDirectionA", "name": "Pool Chlorinator Cell Direction A", "status_key": "status"},
    {"key": "cellDirectionB", "name": "Pool Chlorinator Cell Direction B", "status_key": "status"},
    {"key": "error", "name": "Pool Chlorinator Error", "device_class": "problem"},
    {"key": "saltStatus", "name": "Pool Salt Fault", "device_class": "problem", "special": "salt_fault"},
]


async def async_setup_entry(hass, entry, async_add_entities):
    coordinator = hass.data[DOMAIN][entry.entry_id]
    sensors = [GenericBinarySensor(coordinator, entry, config) for config in BINARY_SENSOR_CONFIG]
    async_add_entities(sensors)


class GenericBinarySensor(CoordinatorEntity, BinarySensorEntity):
    """Generic binary sensor for pool components."""

    def __init__(self, coordinator, entry, config):
        super().__init__(coordinator)
        self.coordinator = coordinator
        self.config = config
        self.entry = entry

    @property
    def name(self):
        return self.config["name"]

    @property
    def unique_id(self):
        # Use the entry_id + key for a stable unique id
        return f"{self.coordinator.device_id}_{self.config['key']}"

    @property
    def is_on(self):
        key = self.config["key"]
        status_key = self.config.get("status_key")
        special = self.config.get("special")
        data = self.coordinator.data or {}

        if status_key:
            data = data.get(status_key, {})

        if special == "salt_fault":
            # treat anything other than NORMAL as a fault
            return data.get(key) not in (None, "NORMAL", "Ok", "OK")
        return bool(data.get(key))

    @property
    def icon(self):
        """Return dynamic icon based on state using ICONS dict."""
        key = self.config["key"]
        special = self.config.get("special")
        state = self.is_on
        icons_for_key = ICONS.get(key, {})

        if special == "salt_fault":
            return icons_for_key.get("fault") if state else icons_for_key.get("normal", icons_for_key.get("default", "mdi:help-circle"))

        if state and "on" in icons_for_key:
            return icons_for_key["on"]
        if not state and "off" in icons_for_key:
            return icons_for_key["off"]

        return icons_for_key.get("default", "mdi:help-circle")

    @property
    def device_class(self):
        return self.config.get("device_class")

    @property
    def available(self):
        # CoordinatorEntity already offers coordinator last_update_success, but this is explicit
        return self.coordinator.last_update_success

    @property
    def device_info(self):
        return get_device_info(self.coordinator, self.entry)
