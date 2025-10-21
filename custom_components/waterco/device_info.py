"""Device info helper for Waterco Electrochlor integration."""
from __future__ import annotations
from typing import Any
from homeassistant.config_entries import ConfigEntry
from homeassistant.helpers.entity import DeviceInfo

from .const import DOMAIN

def make_device_info(entry: ConfigEntry, api_data: dict[str, Any] | None = None) -> DeviceInfo:
    """Generate device_info for all Electrochlor entities."""
    ip = entry.data.get("ip_address") if entry else None
    return DeviceInfo(
        identifiers={(DOMAIN, entry.entry_id)},
        name=f"Electrochlor {ip}" if ip else "Electrochlor",
        manufacturer="Waterco",
        model=api_data.get("model") if api_data else "Electrochlor",
        sw_version=api_data.get("version") if api_data else None,
        configuration_url=f"http://{ip}" if ip else None,  # <-- Added
    )
