"""Switch platform for Waterco Electrochlor integration."""

from __future__ import annotations

import asyncio
import logging
import random
from typing import Any

import aiohttp

from homeassistant.components.switch import SwitchEntity

from .const import DOMAIN
from .device_icons import ICONS
from .device_info import make_device_info
from .helpers import find_key

_LOGGER = logging.getLogger(__name__)


SWITCH_CONFIG: list[dict[str, Any]] = [
    {
        "key": "pump",
        "name": "Pool Pump",
        "command_key": "state",
        "status_key": "status",
    },
    {
        "key": "light",
        "name": "Pool Lights",
        "command_key": "light",
        "status_key": "status",
    },
    {
        "key": "valve",
        "name": "Pool Valve",
        "command_key": "valve",
        "status_key": "status",
    },
]


POLL_INTERVAL = 3
POLL_TIMEOUT = 30


def extract_state(value: Any) -> bool:
    """Convert different types of values to a boolean."""
    if isinstance(value, bool):
        return value

    if isinstance(value, str):
        return value.lower() in ("true", "on", "1")

    if isinstance(value, (int, float)):
        return value != 0

    return False


async def async_setup_entry(
    hass,
    entry,
    async_add_entities,
) -> None:
    """Set up Electrochlor switches."""
    coordinator = hass.data[DOMAIN][entry.entry_id]

    switches = [
        GenericPoolSwitch(coordinator, entry, config)
        for config in SWITCH_CONFIG
    ]

    async_add_entities(switches)


class BaseSwitch(SwitchEntity):
    """Base switch class."""

    def __init__(self, coordinator, entry) -> None:
        """Initialize the base switch."""
        self.coordinator = coordinator
        self.entry = entry

    @property
    def available(self) -> bool:
        """Return whether the switch is available."""
        return bool(self.coordinator.data)

    @property
    def device_info(self):
        """Return device information."""
        return make_device_info(
            self.entry,
            self.coordinator.data,
        )

    async def _send_command(
        self,
        path: str,
        value: Any,
    ) -> bool:
        """Send a command to the Electrochlor controller."""
        boundary = (
            "----WebKitFormBoundary"
            + "".join(
                random.choices(
                    "abcdefghijklmnopqrstuvwxyz"
                    "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
                    "0123456789",
                    k=16,
                )
            )
        )

        url = (
            f"http://{self.coordinator.ip_address}:"
            f"{self.coordinator.port}/electrochlor/{path}"
        )

        data = (
            f"--{boundary}\r\n"
            f'Content-Disposition: form-data; name="value"\r\n'
            f"\r\n"
            f"{str(value).lower()}\r\n"
            f"--{boundary}--\r\n"
        )

        headers = {
            "Content-Type": (
                f"multipart/form-data; boundary={boundary}"
            )
        }

        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    url,
                    data=data.encode("utf-8"),
                    headers=headers,
                ) as resp:
                    text = await resp.text()

                    if resp.status != 200:
                        _LOGGER.error(
                            "Failed command to %s "
                            "(HTTP %s): %s",
                            path,
                            resp.status,
                            text.strip(),
                        )
                        return False

                    _LOGGER.debug(
                        "Successfully sent %s=%s to Electrochlor",
                        path,
                        value,
                    )

                    return True

        except aiohttp.ClientError as err:
            _LOGGER.error(
                "Error sending command to %s: %s",
                path,
                err,
            )
            return False

        except Exception:
            _LOGGER.exception(
                "Unexpected error sending command to %s",
                path,
            )
            return False

    async def _poll_until_state(
        self,
        key: str,
        desired_state: bool,
        status_key: str | None = None,
    ) -> bool:
        """Poll the device until the desired state is reached."""
        elapsed = 0

        while elapsed < POLL_TIMEOUT:
            await self.coordinator.async_request_refresh()

            data = self.coordinator.data or {}

            if status_key:
                # The coordinator returns the complete API document:
                #
                # {
                #     "result": {
                #         "status": {
                #             ...
                #         }
                #     },
                #     "error": false
                # }
                #
                # Therefore status is NOT at data["status"].
                # Search for it recursively instead.
                scoped = find_key(data, status_key)

                if isinstance(scoped, dict):
                    data = scoped

            value = find_key(data, key)

            if extract_state(value) == desired_state:
                _LOGGER.debug(
                    "Confirmed %s=%s after %s seconds",
                    key,
                    desired_state,
                    elapsed,
                )
                return True

            await asyncio.sleep(POLL_INTERVAL)
            elapsed += POLL_INTERVAL

        _LOGGER.warning(
            "Polling timeout for %s; state may not match desired state.",
            key,
        )

        return False


class GenericPoolSwitch(BaseSwitch):
    """Switch for pool components."""

    def __init__(
        self,
        coordinator,
        entry,
        config,
    ) -> None:
        """Initialize the pool switch."""
        super().__init__(coordinator, entry)

        self.config = config
        self._optimistic_state: bool | None = None

    @property
    def name(self) -> str:
        """Return the switch name."""
        return self.config["name"]

    @property
    def unique_id(self) -> str:
        """Return the unique ID."""
        return (
            f"{self.entry.entry_id}_"
            f"{self.config['key']}"
        )

    @property
    def is_on(self) -> bool:
        """Return the current switch state."""
        if self._optimistic_state is not None:
            return self._optimistic_state

        data = self.coordinator.data or {}

        value = find_key(
            data,
            self.config["key"],
        )

        return extract_state(value)

    @property
    def icon(self) -> str:
        """Return the appropriate icon."""
        key = self.config["key"]
        state = self.is_on
        icons_for_key = ICONS.get(key, {})

        if state and "on" in icons_for_key:
            return icons_for_key["on"]

        if not state and "off" in icons_for_key:
            return icons_for_key["off"]

        return icons_for_key.get(
            "default",
            "mdi:help-circle",
        )

    async def async_turn_on(self, **kwargs) -> None:
        """Turn the device on."""
        self._optimistic_state = True
        self.async_write_ha_state()

        success = await self._send_command(
            self.config.get(
                "command_key",
                self.config["key"],
            ),
            True,
        )

        if success:
            await self._poll_until_state(
                self.config["key"],
                True,
                status_key=self.config.get("status_key"),
            )

        self._optimistic_state = None
        self.async_write_ha_state()

    async def async_turn_off(self, **kwargs) -> None:
        """Turn the device off."""
        self._optimistic_state = False
        self.async_write_ha_state()

        success = await self._send_command(
            self.config.get(
                "command_key",
                self.config["key"],
            ),
            False,
        )

        if success:
            await self._poll_until_state(
                self.config["key"],
                False,
                status_key=self.config.get("status_key"),
            )

        self._optimistic_state = None
        self.async_write_ha_state()