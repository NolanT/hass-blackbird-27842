"""
Client wrapper to adapt pyavcontrol library to the expected API.
"""

import asyncio
import logging
from pyavcontrol import construct_async_client

_LOGGER = logging.getLogger(__name__)


class AsyncClientWrapper:
    """Wrapper to provide the expected API for Home Assistant integration"""
    
    def __init__(self, model_id: str):
        self.model_id = model_id
        self._client = None
        self._event_loop = None
    
    async def connect(self, host: str, port: int, timeout: float = 10.0):
        """Connect to the device"""
        self._event_loop = asyncio.get_event_loop()
        
        # Create connection URL in the format expected by pyserial
        url = f"socket://{host}:{port}"
        
        # Use the existing construct_async_client function
        self._client = await construct_async_client(
            self.model_id, 
            url, 
            self._event_loop,
            connection_config={"timeout": timeout}
        )
    
    async def disconnect(self):
        """Disconnect from the device"""
        if self._client and hasattr(self._client, '_connection'):
            # The connection cleanup is handled by the underlying connection
            pass
        self._client = None
    
    @property
    def api(self):
        """Access to the API methods"""
        if not self._client:
            raise RuntimeError("Client not connected. Call connect() first.")
        return self._client.api
    
    @property
    def is_connected(self):
        """Check if connected"""
        return self._client is not None


def get_async_client(model_id: str) -> AsyncClientWrapper:
    """
    Create an async client for the specified model.
    This function provides compatibility with the existing integration code.
    
    :param model_id: Model identifier for the device
    :return: AsyncClientWrapper instance
    """
    return AsyncClientWrapper(model_id)