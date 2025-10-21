"""Coordinator for fetching Electrochlor data using DataUpdateCoordinator."""
from __future__ import annotations
import asyncio
import logging
from datetime import timedelta
from typing import Any
import aiohttp
import async_timeout

from homeassistant.core import HomeAssistant
from homeassistant.helpers.aiohttp_client import async_get_clientsession
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed
from homeassistant.config_entries import ConfigEntry

from .const import (
    CONF_IP_ADDRESS,
    CONF_PORT,
    CONF_SCAN_INTERVAL,
    DEFAULT_PORT,
    DEFAULT_SCAN_INTERVAL,
    API_PATH,
)

_LOGGER = logging.getLogger(__name__)
REQUEST_TIMEOUT = 10  # seconds


class ElectrochlorDataUpdateCoordinator(DataUpdateCoordinator):
    """Coordinator for fetching data from Waterco Electrochlor."""

    def __init__(self, hass: HomeAssistant, entry: ConfigEntry) -> None:
        self.hass = hass
        self.entry = entry
        data = entry.data
        options = entry.options

        self.ip_address: str = data.get(CONF_IP_ADDRESS)
        self.port: int = int(data.get(CONF_PORT, DEFAULT_PORT))
        self._update_interval = timedelta(
            seconds=int(
                options.get(
                    CONF_SCAN_INTERVAL, data.get(CONF_SCAN_INTERVAL, DEFAULT_SCAN_INTERVAL)
                )
            )
        )
        self.api_url: str = f"http://{self.ip_address}:{self.port}{API_PATH}"

        super().__init__(
            hass,
            _LOGGER,
            name=f"Electrochlor {self.ip_address}",
            update_interval=self._update_interval,
        )

    async def async_setup(self) -> None:
        """Initial setup of the coordinator by fetching data once."""
        await self.async_refresh()

    async def _async_update_data(self) -> dict[str, Any]:
        """Fetch data from the Electrochlor device."""
        session = async_get_clientsession(self.hass)
        try:
            async with async_timeout.timeout(REQUEST_TIMEOUT):
                resp = await session.get(self.api_url)
                resp.raise_for_status()
                data = await resp.json()
        except asyncio.TimeoutError as err:
            raise UpdateFailed(f"Timeout fetching data from {self.api_url}") from err
        except aiohttp.ClientResponseError as err:
            raise UpdateFailed(f"HTTP error fetching data from {self.api_url}: {err.status}") from err
        except aiohttp.ClientError as err:
            raise UpdateFailed(f"Connection error fetching data from {self.api_url}") from err
        except ValueError as err:
            raise UpdateFailed("Received invalid JSON from device") from err

        if not isinstance(data, dict):
            raise UpdateFailed("Unexpected data format from device: expected JSON object")

        return data

    def update_from_entry(self, entry: ConfigEntry) -> None:
        """Update coordinator settings from updated config entry options."""
        data = entry.data
        options = entry.options

        self.ip_address = data.get(CONF_IP_ADDRESS, self.ip_address)
        self.port = int(data.get(CONF_PORT, self.port))
        self._update_interval = timedelta(
            seconds=int(
                options.get(
                    CONF_SCAN_INTERVAL, data.get(CONF_SCAN_INTERVAL, DEFAULT_SCAN_INTERVAL)
                )
            )
        )
        self.update_interval = self._update_interval
        self.api_url = f"http://{self.ip_address}:{self.port}{API_PATH}"
