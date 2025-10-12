"""
Custom integration to integrate the Waterco Electrochlor with Home Assistant.

For more details about this integration, please refer to
https://github.com/brezlord/hass-waterco-electrochlor

"""

from homeassistant.helpers.entity import DeviceInfo
from .const import DOMAIN

def get_device_info(coordinator, entry):
    """Return device info for all Electrochlor entities."""
    ip_address = entry.data.get("ip_address")
    return DeviceInfo(
        identifiers={(DOMAIN, entry.entry_id)},  # all entities share the same identifier
        name=f"Electrochlor {ip_address}",
        manufacturer="Waterco",
        model="Electrochlor Pool Controller",
        sw_version="1.81",
        configuration_url=f"http://{ip_address}",  # Visit link
    )
