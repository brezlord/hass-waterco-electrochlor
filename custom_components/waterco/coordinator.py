"""Coordinator for fetching Electrochlor data."""

from __future__ import annotations

import asyncio
import logging
from datetime import timedelta
from typing import Any

import aiohttp
import async_timeout

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.aiohttp_client import (
    async_get_clientsession,
)
from homeassistant.helpers.update_coordinator import (
    DataUpdateCoordinator,
    UpdateFailed,
)

from .const import (
    API_PATH,
    CONF_IP_ADDRESS,
    CONF_PORT,
    CONF_SCAN_INTERVAL,
    DEFAULT_PORT,
    DEFAULT_SCAN_INTERVAL,
)

_LOGGER = logging.getLogger(__name__)

REQUEST_TIMEOUT = 10


class ElectrochlorDataUpdateCoordinator(
    DataUpdateCoordinator[dict[str, Any]]
):
    """Coordinator for fetching data from Waterco Electrochlor."""

    def __init__(
        self,
        hass: HomeAssistant,
        entry: ConfigEntry,
    ) -> None:
        """Initialize the coordinator."""

        self.hass = hass
        self.entry = entry

        self._update_settings(entry)

        super().__init__(
            hass,
            _LOGGER,
            name=f"Electrochlor {self.device_name}",
            update_interval=self._update_interval,
        )

    def _update_settings(
        self,
        entry: ConfigEntry,
    ) -> None:
        """Update connection settings from the config entry."""

        data = entry.data
        options = entry.options

        self.device_name = options.get(
            "device_name",
            data.get(
                "device_name",
                "Pool 1",
            ),
        )

        self.ip_address = options.get(
            CONF_IP_ADDRESS,
            data.get(
                CONF_IP_ADDRESS,
                "",
            ),
        )

        self.port = int(
            options.get(
                CONF_PORT,
                data.get(
                    CONF_PORT,
                    DEFAULT_PORT,
                ),
            )
        )

        scan_interval = int(
            options.get(
                CONF_SCAN_INTERVAL,
                data.get(
                    CONF_SCAN_INTERVAL,
                    DEFAULT_SCAN_INTERVAL,
                ),
            )
        )

        self._update_interval = timedelta(
            seconds=scan_interval,
        )

        self.api_url = (
            f"http://{self.ip_address}:"
            f"{self.port}"
            f"{API_PATH}"
        )

    async def async_setup(self) -> None:
        """Perform the initial coordinator refresh."""
        await self.async_refresh()

    async def _async_update_data(self) -> dict[str, Any]:
        """Fetch data from the Electrochlor device."""

        session = async_get_clientsession(self.hass)

        try:
            async with async_timeout.timeout(
                REQUEST_TIMEOUT
            ):
                response = await session.get(
                    self.api_url
                )

                response.raise_for_status()

                data = await response.json()

        except asyncio.TimeoutError as err:
            raise UpdateFailed(
                f"Timeout fetching data from {self.api_url}"
            ) from err

        except aiohttp.ClientResponseError as err:
            raise UpdateFailed(
                "HTTP error fetching data from "
                f"{self.api_url}: {err.status}"
            ) from err

        except aiohttp.ClientError as err:
            raise UpdateFailed(
                f"Connection error fetching data from "
                f"{self.api_url}"
            ) from err

        except ValueError as err:
            raise UpdateFailed(
                "Received invalid JSON from device"
            ) from err

        if not isinstance(data, dict):
            raise UpdateFailed(
                "Unexpected data format from device: "
                "expected JSON object"
            )

        return data

    def update_from_entry(
        self,
        entry: ConfigEntry,
    ) -> None:
        """Update coordinator settings after options change."""

        self.entry = entry

        self._update_settings(entry)

        self.update_interval = self._update_interval

        _LOGGER.debug(
            "Electrochlor configuration updated: "
            "name=%s, ip=%s, port=%s, interval=%ss",
            self.device_name,
            self.ip_address,
            self.port,
            self._update_interval.total_seconds(),
        )