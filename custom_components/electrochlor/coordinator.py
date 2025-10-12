"""
Custom integration to integrate the Waterco Electrochlor with Home Assistant.

For more details about this integration, please refer to
https://github.com/brezlord/hass-waterco-electrochlor

"""

import logging
from datetime import timedelta
import aiohttp
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed
from .const import DOMAIN, DEFAULT_SCAN_INTERVAL

_LOGGER = logging.getLogger(__name__)

class ElectrochlorDataUpdateCoordinator(DataUpdateCoordinator):
    def __init__(self, hass, config, options=None):
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
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(self.url, timeout=10) as response:
                    data = await response.json()
                    if data.get("error"):
                        raise UpdateFailed("Electrochlor API returned error")
                    return data["result"]
        except Exception as e:
            _LOGGER.error("Error fetching Electrochlor data: %s", e)
            raise UpdateFailed(e)

    def update_options(self, options):
        """Update coordinator IP/port from options flow."""
        self.ip_address = options.get("ip_address", self.ip_address)
        self.port = options.get("port", self.port)
        self.url = f"http://{self.ip_address}:{self.port}/electrochlor"

