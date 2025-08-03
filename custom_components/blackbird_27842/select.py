"""Select platform for Blackbird integration."""

import logging
from typing import List, Optional

from homeassistant.components.select import SelectEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import CONF_HOST
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.entity import DeviceInfo

from .const import (
    DOMAIN,
    DEVICE_MANUFACTURER,
    DEVICE_MODEL,
    CONF_INPUT_NAMES,
    CONF_OUTPUT_NAMES,
    MAX_INPUTS,
    MAX_OUTPUTS,
)

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(
    hass: HomeAssistant,
    config_entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up Blackbird select entities."""
    client = hass.data[DOMAIN][config_entry.entry_id]["client"]
    host = hass.data[DOMAIN][config_entry.entry_id]["host"]
    
    input_names = config_entry.data.get(CONF_INPUT_NAMES, {})
    output_names = config_entry.data.get(CONF_OUTPUT_NAMES, {})
    
    # Create select entities for each output
    entities = []
    for output_num in range(1, MAX_OUTPUTS + 1):
        output_name = output_names.get(output_num, f"Output {output_num}")
        entities.append(
            BlackbirdInputSelect(
                client, 
                host, 
                config_entry.entry_id,
                output_num, 
                output_name, 
                input_names
            )
        )
    
    async_add_entities(entities)


class BlackbirdInputSelect(SelectEntity):
    """Representation of a Blackbird input selector for an output."""

    def __init__(
        self, 
        client, 
        host: str, 
        entry_id: str,
        output_num: int, 
        output_name: str, 
        input_names: dict
    ):
        """Initialize the select entity."""
        self._client = client
        self._host = host
        self._entry_id = entry_id
        self._output_num = output_num
        self._output_name = output_name
        self._input_names = input_names
        self._current_option = None
        self._available = True

    @property
    def name(self) -> str:
        """Return the name of the select entity."""
        return f"{self._output_name} Input"

    @property
    def unique_id(self) -> str:
        """Return unique ID for the select entity."""
        return f"{self._host}_output_{self._output_num}_input"

    @property
    def device_info(self) -> DeviceInfo:
        """Return device information."""
        return DeviceInfo(
            identifiers={(DOMAIN, self._host)},
            name=f"Blackbird Matrix ({self._host})",
            manufacturer=DEVICE_MANUFACTURER,
            model=DEVICE_MODEL,
        )

    @property
    def options(self) -> List[str]:
        """Return the list of available options."""
        options = []
        for input_num in range(1, MAX_INPUTS + 1):
            input_name = self._input_names.get(input_num, f"Input {input_num}")
            options.append(input_name)
        return options

    @property
    def current_option(self) -> Optional[str]:
        """Return the current selected option."""
        return self._current_option

    @property
    def available(self) -> bool:
        """Return True if entity is available."""
        return self._available

    async def async_select_option(self, option: str) -> None:
        """Change the selected option."""
        try:
            # Find the input number for the selected option
            input_num = None
            for num in range(1, MAX_INPUTS + 1):
                input_name = self._input_names.get(num, f"Input {num}")
                if input_name == option:
                    input_num = num
                    break
            
            if input_num is None:
                _LOGGER.error("Invalid input option selected: %s", option)
                return
            
            # Send routing command
            await self._client.api.routing.set(output=self._output_num, input=input_num)
            self._current_option = option
            self._available = True
            
        except Exception as exc:
            _LOGGER.error("Failed to set input for output %d: %s", self._output_num, exc)
            self._available = False

    async def async_update(self) -> None:
        """Update the select entity state."""
        try:
            # Get current routing status
            # Note: The API returns status for all outputs, we need to parse it
            status_response = await self._client.api.status.video()
            
            # The response format is: "Output XX Switch To In YY!"
            # We need to find the line for our output
            if isinstance(status_response, dict) and "input" in status_response:
                # If we get a single response, check if it's for our output
                if status_response.get("output") == f"{self._output_num:02d}":
                    input_num = int(status_response["input"])
                    input_name = self._input_names.get(input_num, f"Input {input_num}")
                    self._current_option = input_name
            
            self._available = True
            
        except Exception as exc:
            _LOGGER.error("Failed to update input status for output %d: %s", self._output_num, exc)
            self._available = False