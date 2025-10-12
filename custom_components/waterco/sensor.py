"""
Custom integration to integrate the Waterco Electrochlor with Home Assistant.

For more details about this integration, please refer to
https://github.com/brezlord/hass-waterco-electrochlor

"""

import logging
import json
import os
from homeassistant.helpers.entity import Entity
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

SENSOR_CONFIG = [
    {"key": "temp", "name": "Pool Temperature", "unit": "°C", "round": 1},
    {"key": "ph", "name": "Pool pH", "unit": "pH", "round": 2},
    {"key": "chlorineProduction", "name": "Pool Chlorine Production"},
    {"key": "operation", "name": "Pool Operation Mode"},
    {"key": "operationType", "subkey": "name", "name": "Pool Operation Type"},
    {"key": "pumpSpeed", "name": "Pool Pump Speed", "unit": "RPM"},
    {"key": "lightColor", "name": "Pool Light Colour"},
    {"key": "saltStatus", "name": "Pool Salt Status"},
    {"key": "error", "name": "Pool Chlorinator Status", "special": "error"},
    {"key": "status", "name": "Pool Chlorinator Cell Direction", "special": "cell_direction"},
]

async def async_setup_entry(hass, entry, async_add_entities):
    coordinator = hass.data[DOMAIN][entry.entry_id]
    sensors = [GenericPoolSensor(coordinator, entry, config) for config in SENSOR_CONFIG]
    async_add_entities(sensors)

class GenericPoolSensor(Entity):
    """Generic sensor for all pool data points."""

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
    def state(self):
        key = self.config["key"]
        subkey = self.config.get("subkey")
        special = self.config.get("special")
        data = self.coordinator.data or {}

        # Special handling
        if special == "error":
            return "Error" if data.get("error") else "OK"
        if special == "cell_direction":
            status = data.get("status", {})
            if status.get("cellDirectionA"):
                return "A"
            elif status.get("cellDirectionB"):
                return "B"
            else:
                return "Off"

        value = data.get(key)
        if subkey and isinstance(value, dict):
            value = value.get(subkey)
        if value is None:
            return "unavailable"
        if "round" in self.config and isinstance(value, (int, float)):
            value = round(value, self.config["round"])
        return value

    @property
    def icon(self):
        key = self.config["key"]
        state_str = str(self.state).title()
        chosen_icon = None
        if key in ICONS:
            icons_for_key = ICONS[key]
            if state_str.lower() in ["true", "false", "on", "off"]:
                chosen_icon = icons_for_key.get("on") if state_str.lower() in ["true", "on"] else icons_for_key.get("off")
            elif state_str in icons_for_key:
                chosen_icon = icons_for_key[state_str]
            elif "default" in icons_for_key:
                chosen_icon = icons_for_key["default"]
        return chosen_icon or "mdi:help-circle"

    @property
    def unit_of_measurement(self):
        return self.config.get("unit")

    @property
    def available(self):
        return self.coordinator.last_update_success

    async def async_update(self):
        await self.coordinator.async_request_refresh()

    @property
    def device_info(self):
        return get_device_info(self.coordinator, self.entry)


