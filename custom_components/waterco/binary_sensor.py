"""
Custom integration to integrate the Waterco Electrochlor with Home Assistant.

For more details about this integration, please refer to
https://github.com/brezlord/hass-waterco-electrochlor
"""

import logging
from homeassistant.components.binary_sensor import BinarySensorEntity
from .const import DOMAIN
from .device_info import get_device_info
from .device_icons import ICONS  # <- dynamic icons

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

class GenericBinarySensor(BinarySensorEntity):
    """Generic binary sensor for pool components."""

    def __init__(self, coordinator, entry, config):
        self.coordinator = coordinator
        self.config = config
        self.entry = entry

    @property
    def name(self):
        return self.config["name"]

    @property
    def unique_id(self):
        return f"{self.coordinator.device_id}_{self.config['name'].lower().replace(' ', '_')}"

    @property
    def is_on(self):
        key = self.config["key"]
        status_key = self.config.get("status_key")
        special = self.config.get("special")
        data = self.coordinator.data or {}
        if status_key:
            data = data.get(status_key, {})

        if special == "salt_fault":
            return data.get(key) != "NORMAL"
        return data.get(key, False)

    @property
    def icon(self):
        """Return dynamic icon based on state using Python ICONS dict."""
        key = self.config["key"]
        special = self.config.get("special")
        state = self.is_on
        icons_for_key = ICONS.get(key, {})

        if special == "salt_fault":
            return icons_for_key.get("fault") if state else icons_for_key.get("normal", icons_for_key.get("default", "mdi:help-circle"))

        # on/off icons for normal binary sensors
        if state and "on" in icons_for_key:
            return icons_for_key["on"]
        if not state and "off" in icons_for_key:
            return icons_for_key["off"]

        # fallback
        return icons_for_key.get("default", "mdi:help-circle")

    @property
    def device_class(self):
        return self.config.get("device_class")

    @property
    def available(self):
        return self.coordinator.last_update_success

    async def async_update(self):
        await self.coordinator.async_request_refresh()

    @property
    def device_info(self):
        return get_device_info(self.coordinator, self.entry)
