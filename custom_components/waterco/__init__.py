"""The Waterco Electrochlor integration."""

from __future__ import annotations

import logging

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.exceptions import ConfigEntryNotReady

from .const import (
    CONF_DEVICE_NAME,
    CONF_IP_ADDRESS,
    CONF_PORT,
    CONF_SCAN_INTERVAL,
    DEFAULT_DEVICE_NAME,
    DEFAULT_PORT,
    DEFAULT_SCAN_INTERVAL,
    DOMAIN,
    PLATFORMS,
)
from .coordinator import ElectrochlorDataUpdateCoordinator

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
) -> bool:
    """Set up Waterco Electrochlor from a config entry."""

    hass.data.setdefault(DOMAIN, {})

    # Ensure older entries have a device name.
    if CONF_DEVICE_NAME not in entry.options:
        device_name = entry.data.get(
            CONF_DEVICE_NAME,
            DEFAULT_DEVICE_NAME,
        )

        hass.config_entries.async_update_entry(
            entry,
            options={
                **entry.options,
                CONF_DEVICE_NAME: device_name,
            },
        )

    coordinator = ElectrochlorDataUpdateCoordinator(
        hass,
        entry,
    )

    try:
        await coordinator.async_setup()

    except Exception as err:
        _LOGGER.error(
            "Unable to connect to Waterco Electrochlor: %s",
            err,
        )
        raise ConfigEntryNotReady from err

    hass.data[DOMAIN][entry.entry_id] = coordinator

    await hass.config_entries.async_forward_entry_setups(
        entry,
        PLATFORMS,
    )

    entry.async_on_unload(
        entry.add_update_listener(
            _async_update_options,
        )
    )

    return True


async def async_unload_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
) -> bool:
    """Unload a config entry."""

    unload_ok = await hass.config_entries.async_unload_platforms(
        entry,
        PLATFORMS,
    )

    if unload_ok:
        hass.data[DOMAIN].pop(
            entry.entry_id,
            None,
        )

        if not hass.data[DOMAIN]:
            hass.data.pop(DOMAIN)

    return unload_ok


async def async_migrate_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
) -> bool:
    """Migrate an existing Waterco config entry."""

    _LOGGER.debug(
        "Migrating Waterco config entry %s from version %s",
        entry.entry_id,
        entry.version,
    )

    if entry.version == 1:
        options = dict(entry.options)

        # Add the new user-defined device name.
        options.setdefault(
            CONF_DEVICE_NAME,
            entry.data.get(
                CONF_DEVICE_NAME,
                DEFAULT_DEVICE_NAME,
            ),
        )

        # Move the existing connection settings into options.
        options.setdefault(
            CONF_IP_ADDRESS,
            entry.data.get(
                CONF_IP_ADDRESS,
                "",
            ),
        )

        options.setdefault(
            CONF_PORT,
            entry.data.get(
                CONF_PORT,
                DEFAULT_PORT,
            ),
        )

        options.setdefault(
            CONF_SCAN_INTERVAL,
            entry.data.get(
                CONF_SCAN_INTERVAL,
                DEFAULT_SCAN_INTERVAL,
            ),
        )

        hass.config_entries.async_update_entry(
            entry,
            options=options,
            version=2,
        )

        _LOGGER.info(
            "Migrated Waterco Electrochlor config entry %s "
            "from version 1 to version 2",
            entry.entry_id,
        )

    return True


async def _async_update_options(
    hass: HomeAssistant,
    entry: ConfigEntry,
) -> None:
    """Update the coordinator after options change."""

    coordinator: ElectrochlorDataUpdateCoordinator | None = (
        hass.data
        .get(DOMAIN, {})
        .get(entry.entry_id)
    )

    if coordinator is None:
        _LOGGER.warning(
            "Could not find coordinator for Waterco entry %s",
            entry.entry_id,
        )
        return

    # Update the coordinator with the new name, IP,
    # port and polling interval.
    coordinator.update_from_entry(entry)

    # Refresh immediately using the new settings.
    await coordinator.async_request_refresh()