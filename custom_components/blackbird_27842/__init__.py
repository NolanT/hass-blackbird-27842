"""
Monoprice Blackbird 27842 HDMI Matrix integration for Home Assistant.
"""

import logging
from typing import Dict, Any

from homeassistant.config_entries import ConfigEntry
from homeassistant.const import CONF_HOST, CONF_PORT
from homeassistant.core import HomeAssistant
from homeassistant.exceptions import ConfigEntryNotReady

from .const import DOMAIN

_LOGGER = logging.getLogger(__name__)

PLATFORMS = ["select", "switch"]


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up Blackbird from a config entry."""
    try:
        from .client_wrapper import get_async_client
        
        # Create the client
        client = get_async_client("monoprice_blackbird_27842")
        
        # Test connection
        await client.connect(
            entry.data[CONF_HOST], 
            entry.data[CONF_PORT], 
            timeout=10.0
        )
        
        # Store client in hass data
        hass.data.setdefault(DOMAIN, {})
        hass.data[DOMAIN][entry.entry_id] = {
            "client": client,
            "host": entry.data[CONF_HOST],
            "port": entry.data[CONF_PORT],
        }
        
        # Set up platforms
        await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)
        
        return True
        
    except Exception as exc:
        _LOGGER.error("Failed to set up Blackbird integration: %s", exc)
        raise ConfigEntryNotReady from exc


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload a config entry."""
    # Unload platforms
    unload_ok = await hass.config_entries.async_unload_platforms(entry, PLATFORMS)
    
    if unload_ok:
        # Disconnect client
        if entry.entry_id in hass.data[DOMAIN]:
            client = hass.data[DOMAIN][entry.entry_id]["client"]
            try:
                await client.disconnect()
            except Exception as exc:
                _LOGGER.warning("Error disconnecting client: %s", exc)
            
            # Remove from hass data
            hass.data[DOMAIN].pop(entry.entry_id)
    
    return unload_ok