"""Switch platform for Blackbird integration."""

import logging
from typing import Any, Optional

from homeassistant.components.switch import SwitchEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import CONF_HOST
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.entity import DeviceInfo

from .const import (
    DOMAIN,
    DEVICE_MANUFACTURER,
    DEVICE_MODEL,
)

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(
    hass: HomeAssistant,
    config_entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up Blackbird switch entities."""
    client = hass.data[DOMAIN][config_entry.entry_id]["client"]
    host = hass.data[DOMAIN][config_entry.entry_id]["host"]
    
    # Create power switch entity
    async_add_entities([BlackbirdPowerSwitch(client, host, config_entry.entry_id)])


class BlackbirdPowerSwitch(SwitchEntity):
    """Representation of the Blackbird matrix power switch."""

    def __init__(self, client, host: str, entry_id: str):
        """Initialize the switch."""
        self._client = client
        self._host = host
        self._entry_id = entry_id
        self._is_on = None
        self._available = True

    @property
    def name(self) -> str:
        """Return the name of the switch."""
        return "Matrix Power"

    @property
    def unique_id(self) -> str:
        """Return unique ID for the switch."""
        return f"{self._host}_power"

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
    def is_on(self) -> Optional[bool]:
        """Return true if the switch is on."""
        return self._is_on

    @property
    def available(self) -> bool:
        """Return True if entity is available."""
        return self._available

    async def async_turn_on(self, **kwargs: Any) -> None:
        """Turn the matrix on."""
        try:
            await self._client.api.power.on()
            self._is_on = True
            self._available = True
        except Exception as exc:
            _LOGGER.error("Failed to turn on matrix: %s", exc)
            self._available = False

    async def async_turn_off(self, **kwargs: Any) -> None:
        """Turn the matrix off."""
        try:
            await self._client.api.power.off()
            self._is_on = False
            self._available = True
        except Exception as exc:
            _LOGGER.error("Failed to turn off matrix: %s", exc)
            self._available = False

    async def async_update(self) -> None:
        """Update the switch state."""
        try:
            # Get status to determine if matrix is powered on
            status = await self._client.api.status.full()
            # Check if "Power ON!" is in the status response
            self._is_on = "Power ON!" in status.get("status", "")
            self._available = True
        except Exception as exc:
            _LOGGER.error("Failed to update matrix status: %s", exc)
            self._available = False