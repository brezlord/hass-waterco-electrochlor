"""Config flow for Waterco Electrochlor integration."""

from __future__ import annotations

from typing import Any

import voluptuous as vol
from homeassistant import config_entries
from homeassistant.const import CONF_PORT
from homeassistant.core import callback
from homeassistant.data_entry_flow import FlowResult

from .const import (
    CONF_DEVICE_NAME,
    CONF_IP_ADDRESS,
    CONF_SCAN_INTERVAL,
    DEFAULT_DEVICE_NAME,
    DEFAULT_PORT,
    DEFAULT_SCAN_INTERVAL,
    DOMAIN,
)


class ElectrochlorConfigFlow(
    config_entries.ConfigFlow,
    domain=DOMAIN,
):
    """Handle a config flow for Waterco Electrochlor."""

    VERSION = 3

    async def async_step_user(
        self,
        user_input: dict[str, Any] | None = None,
    ) -> FlowResult:
        """Handle the initial setup step."""

        if user_input is not None:
            await self.async_set_unique_id(
                user_input[CONF_IP_ADDRESS]
            )
            self._abort_if_unique_id_configured(
                updates=user_input,
            )

            return self.async_create_entry(
                title=user_input[CONF_DEVICE_NAME],
                data=user_input,
            )

        data_schema = vol.Schema(
            {
                vol.Required(
                    CONF_DEVICE_NAME,
                    default=DEFAULT_DEVICE_NAME,
                ): str,
                vol.Required(
                    CONF_IP_ADDRESS,
                ): str,
                vol.Required(
                    CONF_PORT,
                    default=DEFAULT_PORT,
                ): vol.Coerce(int),
                vol.Required(
                    CONF_SCAN_INTERVAL,
                    default=DEFAULT_SCAN_INTERVAL,
                ): vol.Coerce(int),
            }
        )

        return self.async_show_form(
            step_id="user",
            data_schema=data_schema,
        )

    @staticmethod
    @callback
    def async_get_options_flow(
        config_entry: config_entries.ConfigEntry,
    ) -> config_entries.OptionsFlow:
        """Return the options flow handler."""

        return ElectrochlorOptionsFlowHandler()


class ElectrochlorOptionsFlowHandler(
    config_entries.OptionsFlow,
):
    """Handle options flow for Waterco Electrochlor."""

    async def async_step_init(
        self,
        user_input: dict[str, Any] | None = None,
    ) -> FlowResult:
        """Manage the Electrochlor options."""

        if user_input is not None:
            return self.async_create_entry(
                title="",
                data=user_input,
            )

        # Get the current values from options first.
        # Fall back to the original config data for
        # existing installations that have not migrated yet.
        current_name = self.config_entry.options.get(
            CONF_DEVICE_NAME,
            self.config_entry.data.get(
                CONF_DEVICE_NAME,
                DEFAULT_DEVICE_NAME,
            ),
        )

        current_ip = self.config_entry.options.get(
            CONF_IP_ADDRESS,
            self.config_entry.data.get(
                CONF_IP_ADDRESS,
                "",
            ),
        )

        current_port = self.config_entry.options.get(
            CONF_PORT,
            self.config_entry.data.get(
                CONF_PORT,
                DEFAULT_PORT,
            ),
        )

        current_scan_interval = self.config_entry.options.get(
            CONF_SCAN_INTERVAL,
            self.config_entry.data.get(
                CONF_SCAN_INTERVAL,
                DEFAULT_SCAN_INTERVAL,
            ),
        )

        data_schema = vol.Schema(
            {
                vol.Required(
                    CONF_DEVICE_NAME,
                    default=current_name,
                ): str,
                vol.Required(
                    CONF_IP_ADDRESS,
                    default=current_ip,
                ): str,
                vol.Required(
                    CONF_PORT,
                    default=current_port,
                ): vol.Coerce(int),
                vol.Required(
                    CONF_SCAN_INTERVAL,
                    default=current_scan_interval,
                ): vol.Coerce(int),
            }
        )

        return self.async_show_form(
            step_id="init",
            data_schema=data_schema,
        )