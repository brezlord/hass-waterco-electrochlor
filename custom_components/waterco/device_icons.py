"""
Custom integration to integrate the Waterco Electrochlor with Home Assistant.

For more details about this integration, please refer to
https://github.com/brezlord/hass-waterco-electrochlor

Dynamic icons for Electrochlor sensors and binary sensor
"""

ICONS = {
    "pump": {"on": "mdi:pump", "off": "mdi:pump-off"},
    "phPump": {"on": "mdi:heat-pump", "off": "mdi:heat-pump-outline"},
    "light": {"on": "mdi:lightbulb-on", "off": "mdi:lightbulb-off"},
    "valve": {"on": "mdi:valve-open", "off": "mdi:valve-closed"},
    "aux2": {"on": "mdi:power-plug", "off": "mdi:power-plug-off"},
    "cellDirectionA": {"on": "mdi:arrow-left-bold-circle", "off": "mdi:arrow-left-circle-outline"},
    "cellDirectionB": {"on": "mdi:arrow-right-bold-circle", "off": "mdi:arrow-right-circle-outline"},
    "error": {"on": "mdi:alert-circle", "off": "mdi:check-circle", "Error": "mdi:alert-circle", "OK": "mdi:check-circle"},
    "saltStatus": {"fault": "mdi:alert-circle", "normal": "mdi:check-circle"},
    "temp": {"default": "mdi:thermometer"},
    "ph": {"default": "mdi:ph"},
    "chlorineProduction": {"default": "mdi:chemical-weapon"},
    "operation": {"Manual Standby": "mdi:pause-circle-outline", "Manual On": "mdi:play-circle-outline", "default": "mdi:help-circle-outline"},
    "operationType": {"Manual": "mdi:hand-back-left", "Automatic": "mdi:robot", "default": "mdi:help-circle-outline"},
    "pumpSpeed": {"default": "mdi:speedometer"},
    "lightColor": {"default": "mdi:palette"},
    "status": {"A": "mdi:arrow-left-bold-circle", "B": "mdi:arrow-right-bold-circle", "Off": "mdi:power-off", "default": "mdi:help-circle-outline"}
}
