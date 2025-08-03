"""Config flow for Blackbird integration."""

import logging
from typing import Any, Dict, Optional

import voluptuous as vol
from homeassistant import config_entries, core, exceptions
from homeassistant.const import CONF_HOST, CONF_PORT
from homeassistant.core import callback
import homeassistant.helpers.config_validation as cv

from .const import (
    DOMAIN,
    DEFAULT_PORT,
    DEFAULT_TIMEOUT,
    CONF_INPUT_NAMES,
    CONF_OUTPUT_NAMES,
    MAX_INPUTS,
    MAX_OUTPUTS,
)

_LOGGER = logging.getLogger(__name__)

DATA_SCHEMA = vol.Schema({
    vol.Required(CONF_HOST): str,
    vol.Optional(CONF_PORT, default=DEFAULT_PORT): int,
})


async def validate_input(hass: core.HomeAssistant, data: Dict[str, Any]) -> Dict[str, Any]:
    """Validate the user input allows us to connect."""
    try:
        from pyavcontrol import get_async_client
        
        client = get_async_client("monoprice_blackbird_27842")
        await client.connect(data[CONF_HOST], data[CONF_PORT], timeout=DEFAULT_TIMEOUT)
        
        # Test basic communication
        await client.api.device_info.model()
        await client.disconnect()
        
        return {"title": f"Blackbird Matrix ({data[CONF_HOST]})"}
    except Exception as exc:
        _LOGGER.error("Failed to connect to Blackbird matrix: %s", exc)
        raise CannotConnect from exc


class CannotConnect(exceptions.HomeAssistantError):
    """Error to indicate we cannot connect."""


class ConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a config flow for Blackbird."""

    VERSION = 1

    def __init__(self):
        """Initialize the config flow."""
        self._host: Optional[str] = None
        self._port: int = DEFAULT_PORT

    async def async_step_user(self, user_input: Optional[Dict[str, Any]] = None):
        """Handle the initial step."""
        errors: Dict[str, str] = {}
        
        if user_input is not None:
            try:
                info = await validate_input(self.hass, user_input)
                
                # Store connection info for next step
                self._host = user_input[CONF_HOST]
                self._port = user_input[CONF_PORT]
                
                # Set unique ID to prevent duplicate entries
                await self.async_set_unique_id(f"{self._host}:{self._port}")
                self._abort_if_unique_id_configured()
                
                # Move to names configuration step
                return await self.async_step_names()
                
            except CannotConnect:
                errors["base"] = "cannot_connect"
            except Exception:  # pylint: disable=broad-except
                _LOGGER.exception("Unexpected exception")
                errors["base"] = "unknown"

        return self.async_show_form(
            step_id="user", 
            data_schema=DATA_SCHEMA, 
            errors=errors
        )

    async def async_step_names(self, user_input: Optional[Dict[str, Any]] = None):
        """Handle the names configuration step."""
        if user_input is not None:
            # Prepare input and output names
            input_names = {}
            output_names = {}
            
            for i in range(1, MAX_INPUTS + 1):
                name = user_input.get(f"input_{i}", f"Input {i}")
                if name.strip():
                    input_names[i] = name.strip()
                else:
                    input_names[i] = f"Input {i}"
            
            for i in range(1, MAX_OUTPUTS + 1):
                name = user_input.get(f"output_{i}", f"Output {i}")
                if name.strip():
                    output_names[i] = name.strip()
                else:
                    output_names[i] = f"Output {i}"
            
            # Create the config entry
            return self.async_create_entry(
                title=f"Blackbird Matrix ({self._host})",
                data={
                    CONF_HOST: self._host,
                    CONF_PORT: self._port,
                    CONF_INPUT_NAMES: input_names,
                    CONF_OUTPUT_NAMES: output_names,
                }
            )

        # Create schema for names step
        names_schema = {}
        for i in range(1, MAX_INPUTS + 1):
            names_schema[vol.Optional(f"input_{i}", default=f"Input {i}")] = str
        for i in range(1, MAX_OUTPUTS + 1):
            names_schema[vol.Optional(f"output_{i}", default=f"Output {i}")] = str

        return self.async_show_form(
            step_id="names",
            data_schema=vol.Schema(names_schema)
        )