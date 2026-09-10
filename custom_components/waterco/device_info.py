"""Device info helper for Waterco Electrochlor integration."""

from __future__ import annotations

from typing import Any

from homeassistant.config_entries import ConfigEntry
from homeassistant.helpers.entity import DeviceInfo

from .const import (
    CONF_DEVICE_NAME,
    CONF_IP_ADDRESS,
    DOMAIN,
    DEFAULT_DEVICE_NAME,
)


def make_device_info(
    entry: ConfigEntry,
    api_data: dict[str, Any] | None = None,
) -> DeviceInfo:
    """Generate device information for Electrochlor entities."""

    device_name = entry.options.get(
        CONF_DEVICE_NAME,
        entry.data.get(
            CONF_DEVICE_NAME,
            DEFAULT_DEVICE_NAME,
        ),
    )

    ip_address = entry.options.get(
        CONF_IP_ADDRESS,
        entry.data.get(
            CONF_IP_ADDRESS,
        ),
    )

    return DeviceInfo(
        identifiers={
            (DOMAIN, entry.entry_id),
        },
        name=device_name,
        manufacturer="Waterco",
        model=(
            api_data.get("model")
            if api_data
            else "Electrochlor"
        ),
        sw_version=(
            api_data.get("version")
            if api_data
            else None
        ),
        configuration_url=(
            f"http://{ip_address}"
            if ip_address
            else None
        ),
    )