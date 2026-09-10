"""Constants for the Waterco Electrochlor integration."""

from __future__ import annotations

from homeassistant.const import Platform

DOMAIN = "waterco"

CONF_DEVICE_NAME = "device_name"
CONF_IP_ADDRESS = "ip_address"
CONF_PORT = "port"
CONF_SCAN_INTERVAL = "scan_interval"

DEFAULT_DEVICE_NAME = "Pool 1"
DEFAULT_PORT = 90
DEFAULT_SCAN_INTERVAL = 60

API_PATH = "/electrochlor"

PLATFORMS = [
    Platform.SENSOR,
    Platform.SWITCH,
    Platform.BINARY_SENSOR,
]

LOGO = "mdi:water"