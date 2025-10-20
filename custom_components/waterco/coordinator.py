"""DataUpdateCoordinator for the Waterco Electrochlor integration."""

from __future__ import annotations

import logging
from datetime import timedelta
import asyncio

import async_timeout
from homeassistant.helpers.update_coordinator import (
    DataUpdateCoordinator,
    UpdateFailed,
)
from homeassistant.helpers.aiohttp_client import async_get_clientsession

from .const import DOMAIN, DEFAULT_SCAN_INTERVAL

_LOGGER = logging.getLogger(__name__)


class ElectrochlorDataUpdateCoordinator(DataUpdateCoordinator):
    """Coordinator to fetch Electrochlor data from the device."""

    def __init__(self, hass, config: dict, options: dict | None = None) -> None:
        self.hass = hass
        self.ip_address = (options or config).get("ip_address", config["ip_address"])
        self.port = (options or config).get("port", config.get("port", 90))
        self.url = f"http://{self.ip_address}:{self.port}/electrochlor"

        super().__init__(
            hass,
            _LOGGER,
            name="Electrochlor",
            update_interval=timedelta(seconds=DEFAULT_SCAN_INTERVAL),
        )

    async def _async_update_data(self):
        """Fetch data from the Electrochlor device."""
        session = async_get_clientsession(self.hass)

        try:
            # use async_timeout to bound the request
            async with async_timeout.timeout(10):
                resp = await session.get(self.url)
                # will raise for non-2xx status
                resp.raise_for_status()
                data = await resp.json()

            # device-level error handling
            if data is None:
                raise UpdateFailed("No data returned from Electrochlor device")
            if isinstance(data, dict) and data.get("error"):
                raise UpdateFailed("Electrochlor API returned error")

            return data.get("result", data)
        except asyncio.TimeoutError as err:
            _LOGGER.debug("Timeout fetching Electrochlor data from %s: %s", self.url, err)
            raise UpdateFailed("Timeout fetching Electrochlor data") from err
        except (asyncio.CancelledError):
            # propagate
            raise
        except Exception as err:
            _LOGGER.error("Error fetching Electrochlor data: %s", err)
            raise UpdateFailed(err) from err

    def update_options(self, options: dict) -> None:
        """Update coordinator IP/port from options flow and update URL."""
        self.ip_address = options.get("ip_address", self.ip_address)
        self.port = options.get("port", self.port)
        self.url = f"http://{self.ip_address}:{self.port}/electrochlor"
