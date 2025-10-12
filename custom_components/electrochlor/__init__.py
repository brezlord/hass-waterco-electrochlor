"""
Custom integration to integrate the Waterco Electrochlor with Home Assistant.

For more details about this integration, please refer to
https://github.com/brezlord/hass-waterco-electrochlor

"""

import logging
from homeassistant.core import HomeAssistant
from homeassistant.config_entries import ConfigEntry
from .const import DOMAIN
from .coordinator import ElectrochlorDataUpdateCoordinator

_LOGGER = logging.getLogger(__name__)
PLATFORMS = ["sensor", "switch", "binary_sensor"]

async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up the Waterco Electrochlor integration."""
    coordinator = ElectrochlorDataUpdateCoordinator(hass, entry.data, options=entry.options)
    coordinator.device_id = entry.entry_id
    await coordinator.async_config_entry_first_refresh()
    hass.data.setdefault(DOMAIN, {})[entry.entry_id] = coordinator

    # Forward platforms
    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)

    # Listen for options update
    entry.add_update_listener(async_options_updated)

    _LOGGER.info("Waterco Electrochlor setup complete for %s", entry.data.get("ip_address"))
    return True

async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload a config entry."""
    unload_ok = all(
        await hass.config_entries.async_forward_entry_unload(entry, platform)
        for platform in PLATFORMS
    )
    if unload_ok:
        hass.data[DOMAIN].pop(entry.entry_id)
    return unload_ok

async def async_options_updated(hass: HomeAssistant, entry: ConfigEntry):
    """Reload coordinator when options are updated."""
    coordinator = hass.data[DOMAIN][entry.entry_id]
    coordinator.update_options(entry.options)
    await coordinator.async_request_refresh()

