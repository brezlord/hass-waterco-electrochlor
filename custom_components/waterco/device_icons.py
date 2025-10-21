"""Dynamic icon definitions for Waterco Electrochlor integration."""

ICONS: dict[str, dict[str, str]] = {
    # Binary sensors / switches
    "pump": {
        "on": "mdi:pump",
        "off": "mdi:pump-off",
        "default": "mdi:pump",
    },
    "light": {
        "on": "mdi:lightbulb-on",
        "off": "mdi:lightbulb-off",
        "default": "mdi:lightbulb",
    },
    "phPump": {
        "on": "mdi:beaker",
        "off": "mdi:beaker-outline",
        "default": "mdi:beaker",
    },
    "valve": {
        "on": "mdi:valve-open",
        "off": "mdi:valve-closed",
        "default": "mdi:valve",
    },
    "aux2": {
        "on": "mdi:power-plug",
        "off": "mdi:power-plug-off",
        "default": "mdi:power-plug",
    },
    "cellDirectionA": {
        "on": "mdi:alpha-a-circle",
        "off": "mdi:alpha-a-circle-outline",
        "default": "mdi:alpha-a",
    },
    "cellDirectionB": {
        "on": "mdi:alpha-b-circle",
        "off": "mdi:alpha-b-circle-outline",
        "default": "mdi:alpha-b",
    },
    "error": {
        "on": "mdi:alert-circle-outline",
        "off": "mdi:check-circle-outline",
        "default": "mdi:alert",
    },
    "saltStatus": {
        "fault": "mdi:alert-octagon-outline",
        "normal": "mdi:check-decagram-outline",
        "default": "mdi:shaker-outline",
    },

    # Sensor readings
    "temp": {
        "default": "mdi:thermometer",
    },
    "ph": {
        "default": "mdi:ph",
    },
    "chlorineProduction": {
        "on": "mdi:chemical-weapon",
        "off": "mdi:flask-empty-outline",
        "default": "mdi:flask",
    },
    "operation": {
        "default": "mdi:cog-outline",
    },
    "operationType": {
        "default": "mdi:playlist-edit",
    },
    "pumpSpeed": {
        "default": "mdi:speedometer",
    },
    "lightColor": {
        "default": "mdi:palette-outline",
    },
    "saltStatus_sensor": {
        "default": "mdi:shaker-outline",
    },
    "status": {
        "A": "mdi:alpha-a-circle",
        "B": "mdi:alpha-b-circle",
        "Off": "mdi:power",
        "default": "mdi:information-outline",
    },
    "error_sensor": {
        "Error": "mdi:alert-octagon-outline",
        "OK": "mdi:check-circle-outline",
        "default": "mdi:alert",
    },
}
