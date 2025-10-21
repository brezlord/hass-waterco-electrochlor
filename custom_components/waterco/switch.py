"""Switch platform for Waterco Electrochlor integration."""
import logging
import aiohttp
import asyncio
import random
from typing import Any

from homeassistant.components.switch import SwitchEntity
from .const import DOMAIN
from .device_info import make_device_info
from .device_icons import ICONS

_LOGGER = logging.getLogger(__name__)

SWITCH_CONFIG = [
    {"key": "pump", "name": "Pool Pump", "command_key": "state", "status_key": "status"},
    {"key": "light", "name": "Pool Lights", "command_key": "light", "status_key": "status"},
]

POLL_INTERVAL = 3
POLL_TIMEOUT = 30

def find_key(data: dict[str, Any], target_key: str) -> Any:
    """Recursively search for a key in nested dictionaries."""
    if isinstance(data, dict):
        if target_key in data:
            return data[target_key]
        for value in data.values():
            found = find_key(value, target_key)
            if found is not None:
                return found
    return None

def extract_state(value: Any) -> bool:
    """Convert different types of values to boolean."""
    if isinstance(value, bool):
        return value
    if isinstance(value, str):
        return value.lower() in ["true", "on", "1"]
    if isinstance(value, (int, float)):
        return value != 0
    return False

async def async_setup_entry(hass, entry, async_add_entities):
    coordinator = hass.data[DOMAIN][entry.entry_id]
    switches = [GenericPoolSwitch(coordinator, entry, config) for config in SWITCH_CONFIG]
    async_add_entities(switches)

class BaseSwitch(SwitchEntity):
    """Base switch class."""

    def __init__(self, coordinator, entry):
        self.coordinator = coordinator
        self.entry = entry

    @property
    def available(self):
        # Available if coordinator has any data
        return bool(self.coordinator.data)

    @property
    def device_info(self):
        return make_device_info(self.entry, self.coordinator.data)

    async def _send_command(self, path: str, value: Any):
        boundary = "----WebKitFormBoundary" + "".join(
            random.choices("abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789", k=16)
        )
        url = f"http://{self.coordinator.ip_address}:{self.coordinator.port}/electrochlor/{path}"
        data = (
            f"--{boundary}\r\n"
            f'Content-Disposition: form-data; name="value"\r\n\r\n'
            f"{str(value).lower()}\r\n"
            f"--{boundary}--\r\n"
        )
        headers = {"Content-Type": f"multipart/form-data; boundary={boundary}"}

        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(url, data=data.encode("utf-8"), headers=headers) as resp:
                    text = await resp.text()
                    if resp.status != 200:
                        _LOGGER.error(
                            "Failed command to %s (HTTP %s): %s", path, resp.status, text.strip()
                        )
        except Exception as e:
            _LOGGER.error("Error sending command to %s: %s", path, e)

    async def _poll_until_state(self, key: str, desired_state: bool, status_key: str | None = None) -> bool:
        """Poll the device until the desired state is reached or timeout occurs."""
        elapsed = 0
        while elapsed < POLL_TIMEOUT:
            await self.coordinator.async_request_refresh()
            data = self.coordinator.data or {}
            if status_key:
                data = data.get(status_key, {})
            value = find_key(data, key)
            if extract_state(value) == desired_state:
                return True
            await asyncio.sleep(POLL_INTERVAL)
            elapsed += POLL_INTERVAL
        _LOGGER.warning("Polling timeout for %s; state may not match desired state.", key)
        return False

class GenericPoolSwitch(BaseSwitch):
    """Switch for pool components with dynamic icons and optimistic updates."""

    def __init__(self, coordinator, entry, config):
        super().__init__(coordinator, entry)
        self.config = config
        self._optimistic_state: bool | None = None

    @property
    def name(self):
        return self.config["name"]

    @property
    def unique_id(self):
        return f"{self.entry.entry_id}_{self.config['key']}"

    @property
    def is_on(self):
        if self._optimistic_state is not None:
            return self._optimistic_state
        data = self.coordinator.data or {}
        value = find_key(data, self.config["key"])
        return extract_state(value)

    @property
    def icon(self):
        key = self.config["key"]
        state = self.is_on
        icons_for_key = ICONS.get(key, {})
        if state and "on" in icons_for_key:
            return icons_for_key["on"]
        if not state and "off" in icons_for_key:
            return icons_for_key["off"]
        return icons_for_key.get("default", "mdi:help-circle")

    async def async_turn_on(self, **kwargs):
        self._optimistic_state = True
        self.async_write_ha_state()
        await self._send_command(self.config.get("command_key", self.config["key"]), True)
        await self._poll_until_state(self.config["key"], True, status_key=self.config.get("status_key"))
        self._optimistic_state = None
        self.async_write_ha_state()

    async def async_turn_off(self, **kwargs):
        self._optimistic_state = False
        self.async_write_ha_state()
        await self._send_command(self.config.get("command_key", self.config["key"]), False)
        await self._poll_until_state(self.config["key"], False, status_key=self.config.get("status_key"))
        self._optimistic_state = None
        self.async_write_ha_state()
