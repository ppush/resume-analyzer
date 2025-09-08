import httpx
import asyncio
import logging
from typing import Optional
from config import (
    LM_STUDIO_URL, 
    DEFAULT_MODEL, 
    DEFAULT_MAX_TOKENS, 
    DEFAULT_TEMPERATURE, 
    DEFAULT_SEED,
    LLM_TIMEOUT
)

logger = logging.getLogger(__name__)

class LLMConnectionError(Exception):
    """Exception for LLM connection errors"""
    pass

class LLMClient:
    """Client for working with LLM through LM Studio"""
    
    def __init__(self, base_url: str = LM_STUDIO_URL, model: str = DEFAULT_MODEL):
        self.base_url = base_url
        self.model = model
        self.timeout = LLM_TIMEOUT
        self._connection_checked = False
        self._is_available = False
    
    async def check_connection(self) -> bool:
        """Checks LM Studio availability"""
        if self._connection_checked:
            return self._is_available
            
        try:
            async with httpx.AsyncClient(timeout=5) as client:
                # Simple request to check availability
                response = await client.get(self.base_url.replace("/v1/chat/completions", "/v1/models"))
                self._is_available = response.status_code == 200
                self._connection_checked = True
                
                                            # LM Studio available
                    
        except Exception as e:
            self._is_available = False
            self._connection_checked = True
            logger.error(f"❌ LM Studio connection error: {e}")
            logger.error("💡 Make sure LM Studio is running on http://localhost:1234")
            
        return self._is_available
    
    async def query_llm(
        self, 
        prompt: str, 
        model: Optional[str] = None,
        max_tokens: int = DEFAULT_MAX_TOKENS,
        temperature: float = DEFAULT_TEMPERATURE,
        seed: int = DEFAULT_SEED
    ) -> str:
        """
        Sends request to LLM through LM Studio API
        
        Args:
            prompt: Prompt text
            model: Model to use (if not specified, default is used)
            max_tokens: Maximum number of tokens in response
            temperature: Generation temperature (0.0 = deterministic, 1.0 = creative)
            seed: Fixed seed for reproducible results
        
        Returns:
            Response from LLM
        """
        # Check LM Studio availability
        if not await self.check_connection():
            error_msg = "LM Studio unavailable. Start LM Studio on http://localhost:1234"
            logger.error(error_msg)
            raise LLMConnectionError(error_msg)
        
        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                payload = {
                    "model": model or self.model,
                    "messages": [
                        {
                            "role": "user",
                            "content": prompt
                        }
                    ],
                    "max_tokens": max_tokens,
                    "temperature": temperature,
                    "seed": seed,  # Fixed seed for determinism
                    "stream": False
                }
                
                # Send request to LLM
                # LLM parameters configured
                response = await client.post(self.base_url, json=payload)
                response.raise_for_status()
                
                result = response.json()
                
                # Extract response text
                if "choices" in result and len(result["choices"]) > 0:
                    content = result["choices"][0].get("message", {}).get("content", "")
                    logger.debug(f"Received response from LLM: {len(content)} characters")
                    
                    # Add detailed LLM response logging
                    # Received response from LLM
                    
                    return content
                else:
                    logger.warning("No choices in LLM response")
                    return ""
                    
        except httpx.TimeoutException:
            error_msg = "LLM request timed out"
            logger.error(error_msg)
            raise LLMConnectionError(error_msg)
        except httpx.HTTPStatusError as e:
            error_msg = f"HTTP error from LLM: {e.response.status_code}"
            logger.error(error_msg)
            raise LLMConnectionError(error_msg)
        except LLMConnectionError:
            # Re-raise our own errors
            raise
        except Exception as e:
            error_msg = f"Error querying LLM: {e}"
            logger.error(error_msg)
            raise LLMConnectionError(error_msg)

# Global client instance for backward compatibility
_llm_client = LLMClient()

async def query_llm(prompt: str, model: str = DEFAULT_MODEL, temperature: float = DEFAULT_TEMPERATURE, seed: int = DEFAULT_SEED) -> str:
    """
    Convenient function for quick LLM request
    
    Args:
        prompt: Prompt text
        model: Model to use
        temperature: Generation temperature (0.0 = deterministic)
        seed: Fixed seed for reproducibility
    
    Returns:
        Response from LLM
    """
    return await _llm_client.query_llm(prompt, model, temperature=temperature, seed=seed)
