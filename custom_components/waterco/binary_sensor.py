"""
Custom integration to integrate the Waterco Electrochlor with Home Assistant.

For more details about this integration, please refer to
https://github.com/brezlord/hass-waterco-electrochlor

"""

import logging
import json
import os
from homeassistant.components.binary_sensor import BinarySensorEntity
from .const import DOMAIN
from .device_info import get_device_info

_LOGGER = logging.getLogger(__name__)

# Load icons.json
ICONS = {}
ICONS_PATH = os.path.join(os.path.dirname(__file__), "icons.json")
if os.path.exists(ICONS_PATH):
    with open(ICONS_PATH, "r") as f:
        ICONS = json.load(f)
    _LOGGER.debug("Loaded icons.json: %s", ICONS)
else:
    _LOGGER.warning("icons.json not found at %s", ICONS_PATH)

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
        data = self.coordinator.data
        if status_key:
            data = data.get(status_key, {})

        if special == "salt_fault":
            return data.get(key) != "NORMAL"
        return data.get(key, False)

    @property
    def icon(self):
        key = self.config["key"]
        special = self.config.get("special")
        state = self.is_on
        chosen_icon = None
        if key in ICONS:
            if special == "salt_fault":
                chosen_icon = ICONS[key].get("fault") if state else ICONS[key].get("normal")
            else:
                chosen_icon = ICONS[key].get("on") if state else ICONS[key].get("off")
        return chosen_icon or "mdi:help-circle"

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

