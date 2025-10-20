import voluptuous as vol
from homeassistant import config_entries
from homeassistant.core import callback
from homeassistant.helpers import selector

from .const import DOMAIN, CONF_IP_ADDRESS, CONF_PORT, DEFAULT_PORT, CONF_SCAN_INTERVAL, DEFAULT_SCAN_INTERVAL


class ElectrochlorConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle the config flow for Electrochlor."""

    VERSION = 1

    async def async_step_user(self, user_input=None):
        errors = {}

        if user_input is not None:
            # Use the IP address as unique id for this integration instance
            unique_id = user_input[CONF_IP_ADDRESS]
            await self.async_set_unique_id(unique_id)
            self._abort_if_unique_id_configured(updates=user_input)

            return self.async_create_entry(
                title=f"Electrochlor {user_input[CONF_IP_ADDRESS]}",
                data=user_input,
            )

        data_schema = vol.Schema(
            {
                vol.Required(CONF_IP_ADDRESS): str,
                vol.Optional(CONF_PORT, default=DEFAULT_PORT): int,
                vol.Optional(CONF_SCAN_INTERVAL, default=DEFAULT_SCAN_INTERVAL): int,
            }
        )

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

        data_schema = vol.Schema(
            {
                vol.Required(CONF_IP_ADDRESS, default=self.config_entry.data.get(CONF_IP_ADDRESS)): str,
                vol.Optional(CONF_PORT, default=self.config_entry.data.get(CONF_PORT, DEFAULT_PORT)): int,
                vol.Optional(CONF_SCAN_INTERVAL, default=self.config_entry.data.get(CONF_SCAN_INTERVAL, DEFAULT_SCAN_INTERVAL)): int,
            }
        )

        return self.async_show_form(step_id="init", data_schema=data_schema, errors=errors)
