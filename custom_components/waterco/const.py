"""Constants for the Waterco Electrochlor integration."""
from __future__ import annotations
from datetime import timedelta
from homeassistant.const import Platform

DOMAIN = "waterco"
CONF_IP_ADDRESS = "ip_address"
CONF_PORT = "port"
CONF_SCAN_INTERVAL = "scan_interval"
DEFAULT_PORT = 90
DEFAULT_SCAN_INTERVAL = 60
API_PATH = "/electrochlor"

# Use Home Assistant Platform constants consistently
PLATFORMS = [Platform.SENSOR, Platform.SWITCH, Platform.BINARY_SENSOR]

LOGO = "mdi:water"
