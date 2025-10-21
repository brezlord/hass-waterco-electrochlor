"""Config flow for Waterco Electrochlor integration."""
from __future__ import annotations
import logging
from typing import Any
import voluptuous as vol

from homeassistant import config_entries
from homeassistant.const import CONF_PORT
from homeassistant.data_entry_flow import FlowResult
from homeassistant.core import callback

from .const import DOMAIN, CONF_IP_ADDRESS, DEFAULT_PORT, DEFAULT_SCAN_INTERVAL, CONF_SCAN_INTERVAL

_LOGGER = logging.getLogger(__name__)


class ElectrochlorConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a config flow for Waterco Electrochlor."""

    VERSION = 1
    CONNECTION_CLASS = config_entries.CONN_CLASS_LOCAL_POLL  # Fixed from CONN_CLASS_LOCAL_POLLING

    async def async_step_user(self, user_input: dict[str, Any] | None = None) -> FlowResult:
        """Handle the initial step."""
        errors: dict[str, str] = {}

        if user_input is not None:
            await self.async_set_unique_id(user_input[CONF_IP_ADDRESS])
            self._abort_if_unique_id_configured(updates=user_input)
            return self.async_create_entry(
                title=f"Electrochlor {user_input[CONF_IP_ADDRESS]}", data=user_input
            )

        data_schema = vol.Schema({
            vol.Required(CONF_IP_ADDRESS): str,
            vol.Optional(CONF_PORT, default=DEFAULT_PORT): int,
            vol.Optional(CONF_SCAN_INTERVAL, default=DEFAULT_SCAN_INTERVAL): int,
        })

        return self.async_show_form(step_id="user", data_schema=data_schema, errors=errors)

    @staticmethod
    @callback
    def async_get_options_flow(config_entry: config_entries.ConfigEntry) -> config_entries.OptionsFlow:
        """Return the options flow handler."""
        return ElectrochlorOptionsFlowHandler(config_entry)


class ElectrochlorOptionsFlowHandler(config_entries.OptionsFlow):
    """Handle options flow for Waterco Electrochlor."""

    def __init__(self, config_entry: config_entries.ConfigEntry) -> None:
        self.config_entry = config_entry

    async def async_step_init(self, user_input: dict[str, Any] | None = None) -> FlowResult:
        """Manage the options."""
        if user_input is not None:
            return self.async_create_entry(title="", data=user_input)

        data_schema = vol.Schema({
            vol.Optional(
                CONF_SCAN_INTERVAL,
                default=self.config_entry.options.get(CONF_SCAN_INTERVAL, DEFAULT_SCAN_INTERVAL)
            ): int,
        })

        return self.async_show_form(step_id="init", data_schema=data_schema)
