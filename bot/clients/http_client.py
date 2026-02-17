# bot/clients/http_client.py
import aiohttp
from typing import ClassVar, Optional, Any
import logging

logger = logging.getLogger(__name__)


class HTTPClient:
    """Singleton HTTP client with connection pooling"""
    
    _session: ClassVar[Optional[aiohttp.ClientSession]] = None
    
    @classmethod
    async def get_session(cls) -> aiohttp.ClientSession:
        """Get or create HTTP session"""
        if cls._session is None or cls._session.closed:
            cls._session = aiohttp.ClientSession(
                connector=aiohttp.TCPConnector(
                    limit=100,
                    limit_per_host=30
                ),
                timeout=aiohttp.ClientTimeout(total=10)
            )
            logger.info("Created new HTTP session")
        
        return cls._session
    
    @classmethod
    async def request(
        cls,
        method: str,
        url: str,
        params: Optional[dict] = None,
        json: Optional[dict] = None,
        headers: Optional[dict] = None
    ) -> Any:
        """
        Make HTTP request
        
        Args:
            method: HTTP method (GET, POST, PATCH, DELETE)
            url: Full URL
            params: Query parameters (for URL)
            json: JSON body (for POST/PATCH)
            headers: HTTP headers
            
        Returns:
            Parsed JSON response or None
        """
        session = await cls.get_session()
        
        default_headers = {
            'Content-Type': 'application/json',
            'Accept': 'application/json'
        }
        
        if headers:
            default_headers.update(headers)
        
        try:
            logger.debug(f"{method} {url} - params={params}, json={json}")
            
            async with session.request(
                method=method,
                url=url,
                params=params,  # query params in URL
                json=json,      # JSON body
                headers=default_headers
            ) as response:
                
                # Log response
                logger.info(f"{method} {url} - {response.status}")
                
                # Handle errors
                if response.status >= 400:
                    error_text = await response.text()
                    logger.error(
                        f"HTTP request failed: {method} {url} - "
                        f"{response.status}, body: {error_text}"
                    )
                    response.raise_for_status()
                
                # Return JSON for successful responses
                if response.status == 204:  # No Content
                    return None
                
                return await response.json()
                
        except aiohttp.ClientError as e:
            logger.error(f"HTTP request failed: {method} {url} - {e}")
            raise
        except Exception as e:
            logger.error(f"Unexpected error in HTTP request: {e}")
            raise
    
    @classmethod
    async def close_session(cls):
        """Close HTTP session"""
        if cls._session and not cls._session.closed:
            await cls._session.close()
            logger.info("HTTP session closed")
            cls._session = None