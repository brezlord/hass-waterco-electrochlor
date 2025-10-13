"""
Custom integration to integrate the Waterco Electrochlor with Home Assistant.

For more details about this integration, please refer to
https://github.com/brezlord/hass-waterco-electrochlor
"""

import logging
import aiohttp
import asyncio
import random
from homeassistant.components.switch import SwitchEntity
from .const import DOMAIN
from .device_info import get_device_info
from .device_icons import ICONS  # <- use dynamic icons

_LOGGER = logging.getLogger(__name__)

SWITCH_CONFIG = [
    {"key": "pump", "name": "Pool Pump", "command_key": "state", "status_key": "status"},
    {"key": "light", "name": "Pool Lights", "command_key": "light", "status_key": "status"},
    {"key": "valve", "name": "Pool Valve", "command_key": "state", "status_key": "status"},
    {"key": "aux2", "name": "Pool Aux2", "command_key": "state", "status_key": "status"},
]

POLL_INTERVAL = 3
POLL_TIMEOUT = 30

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
        return self.coordinator.last_update_success

    @property
    def device_info(self):
        return get_device_info(self.coordinator, self.entry)

    async def _send_command(self, path, value):
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
                        _LOGGER.error("Failed command to %s (HTTP %s): %s", path, resp.status, text.strip())
        except Exception as e:
            _LOGGER.error("Error sending command to %s: %s", path, e)

    async def _poll_until_state(self, key, desired_state, status_key=None):
        elapsed = 0
        while elapsed < POLL_TIMEOUT:
            await self.coordinator.async_request_refresh()
            data = self.coordinator.data
            if status_key:
                data = data.get(status_key, {})
            if data.get(key) == desired_state:
                return True
            await asyncio.sleep(POLL_INTERVAL)
            elapsed += POLL_INTERVAL
        _LOGGER.warning("Polling timeout for %s; state may not match desired state.", key)
        return False

class GenericPoolSwitch(BaseSwitch):
    """Switch for pool components using dynamic icons."""

    def __init__(self, coordinator, entry, config):
        super().__init__(coordinator, entry)
        self.config = config
        self._optimistic_state = None

    @property
    def name(self):
        return self.config["name"]

    @property
    def unique_id(self):
        return f"{self.coordinator.device_id}_{self.config['name'].lower().replace(' ', '_')}"

    @property
    def is_on(self):
        if self._optimistic_state is not None:
            return self._optimistic_state
        data = self.coordinator.data.get(self.config.get("status_key", ""), {})
        return data.get(self.config["key"], False)

    @property
    def icon(self):
        """Return icon based on state using device_icons.py."""
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
