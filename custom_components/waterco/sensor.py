import logging
from homeassistant.helpers.entity import Entity
from .const import DOMAIN
from .device_info import get_device_info
from .device_icons import ICONS  # <- dynamic icons

_LOGGER = logging.getLogger(__name__)

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
        value = self.state
        icons_for_key = ICONS.get(key, {})

        if str(value).lower() in ["true", "on"]:
            return icons_for_key.get("on", icons_for_key.get("default", "mdi:help-circle"))
        if str(value).lower() in ["false", "off"]:
            return icons_for_key.get("off", icons_for_key.get("default", "mdi:help-circle"))
        if value in icons_for_key:
            return icons_for_key[value]

        return icons_for_key.get("default", "mdi:help-circle")

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
