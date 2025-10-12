"""
Custom integration to integrate the Waterco Electrochlor with Home Assistant.

For more details about this integration, please refer to
https://github.com/brezlord/hass-waterco-electrochlor

"""

import voluptuous as vol
from homeassistant import config_entries
from homeassistant.core import callback
from .const import DOMAIN, CONF_IP_ADDRESS, CONF_PORT, DEFAULT_PORT

class ElectrochlorConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle the config flow for Electrochlor."""

    VERSION = 1

    async def async_step_user(self, user_input=None):
        errors = {}
        if user_input is not None:
            return self.async_create_entry(
                title=f"Electrochlor {user_input[CONF_IP_ADDRESS]}",
                data=user_input
            )

        data_schema = vol.Schema({
            vol.Required(CONF_IP_ADDRESS): str,
            vol.Optional(CONF_PORT, default=DEFAULT_PORT): int
        })
        return self.async_show_form(step_id="user", data_schema=data_schema, errors=errors)

    @staticmethod
    @callback
    def async_get_options_flow(config_entry):
        """Return the options flow handler."""
        return ElectrochlorOptionsFlowHandler(config_entry)


class ElectrochlorOptionsFlowHandler(config_entries.OptionsFlow):
    """Handle options flow for Electrochlor."""

    def __init__(self, config_entry):
        self.config_entry = config_entry

    async def async_step_init(self, user_input=None):
        errors = {}

        if user_input is not None:
            return self.async_create_entry(title="", data=user_input)

        data_schema = vol.Schema({
            vol.Required(CONF_IP_ADDRESS, default=self.config_entry.data.get(CONF_IP_ADDRESS)): str,
            vol.Optional(CONF_PORT, default=self.config_entry.data.get(CONF_PORT, DEFAULT_PORT)): int
        })

        return self.async_show_form(step_id="init", data_schema=data_schema, errors=errors)
