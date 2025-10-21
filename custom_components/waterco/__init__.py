"""The Waterco Electrochlor integration."""
from __future__ import annotations
import logging
from typing import Final
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.const import Platform
from homeassistant.exceptions import ConfigEntryNotReady

from .const import DOMAIN, PLATFORMS
from .coordinator import ElectrochlorDataUpdateCoordinator

_LOGGER = logging.getLogger(__name__)

async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up Waterco Electrochlor from a config entry."""
    hass.data.setdefault(DOMAIN, {})

    coordinator = ElectrochlorDataUpdateCoordinator(hass, entry)
    try:
        await coordinator.async_setup()
    except Exception as err:
        raise ConfigEntryNotReady from err

    hass.data[DOMAIN][entry.entry_id] = coordinator

    # Forward platforms
    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)
    entry.add_update_listener(_async_update_options)

    return True

async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload a config entry."""
    unload_ok = await hass.config_entries.async_unload_platforms(entry, PLATFORMS)
    if unload_ok:
        hass.data[DOMAIN].pop(entry.entry_id, None)
        if not hass.data[DOMAIN]:
            hass.data.pop(DOMAIN)
    return unload_ok

async def _async_update_options(hass: HomeAssistant, entry: ConfigEntry) -> None:
    """Update options."""
    coordinator: ElectrochlorDataUpdateCoordinator | None = hass.data.get(DOMAIN, {}).get(entry.entry_id)
    if coordinator is None:
        return
    coordinator.update_from_entry(entry)
    await coordinator.async_request_refresh()
