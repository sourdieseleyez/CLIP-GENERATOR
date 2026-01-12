"""
Gemini API Key Rotation Manager - Python version for google-genai SDK (2025)

Manages multiple API keys and automatically rotates when rate limited.
Rate limits (429) are per-key, so switching keys is the only way to continue.

Features:
- Automatic key rotation on rate limit errors
- Cooldown management per key
- Primary/fallback model support with retry logic
- Health monitoring for all keys
- Thread-safe for concurrent requests
- Uses google-genai SDK (GA as of May 2025)
"""

import os
import time
import logging
from typing import Optional, List, Dict, Any, Callable, TypeVar
from dataclasses import dataclass, field
import threading

logger = logging.getLogger(__name__)

# Try to import the new SDK
try:
    from google import genai
    from google.genai import types
    GENAI_AVAILABLE = True
except ImportError:
    GENAI_AVAILABLE = False
    logger.warning("google-genai SDK not installed")

# Type variable for generic return type
T = TypeVar('T')

# Cooldown durations (in seconds)
RATE_LIMIT_COOLDOWN = 60          # 1 minute for 429
QUOTA_EXHAUSTED_COOLDOWN = 600    # 10 minutes for quota exhausted
INVALID_KEY_COOLDOWN = 86400      # 24 hours for invalid key

# Error patterns that indicate we should rotate keys
ROTATABLE_ERROR_PATTERNS = [
    'resource_exhausted',
    'rate_limit_exceeded',
    'quota',
    'rate limit',
    'too many requests',
    '429',
]

# Model aliases
MODELS = {
    'PRIMARY': 'gemini-2.5-flash',
    'FALLBACK': 'gemini-2.0-flash',
    'LITE': 'gemini-flash-lite-latest',  # Cheapest, auto-updates
    'PRO': 'gemini-2.5-pro',
}


@dataclass
class KeyState:
    """State tracking for a single API key"""
    key: str
    client: Any  # genai.Client
    is_healthy: bool = True
    cooldown_until: Optional[float] = None
    last_error: Optional[str] = None
    error_count: int = 0


class GeminiKeyManager:
    """
    Manages multiple Gemini API keys with automatic rotation on rate limits.
    
    Usage:
        manager = GeminiKeyManager()
        
        # Simple usage
        result = await manager.generate_content("Hello, world!")
        
        # With retry logic
        result = await manager.execute_with_retry(
            lambda client: client.models.generate_content(
                model='gemini-flash-lite-latest',
                contents='Hello!'
            )
        )
    """
    
    def __init__(self):
        self._keys: List[KeyState] = []
        self._current_index: int = 0
        self._initialized: bool = False
        self._lock = threading.Lock()
        self._load_keys()
    
    def _load_keys(self) -> None:
        """Load API keys from environment variables"""
        if not GENAI_AVAILABLE:
            logger.error("google-genai SDK not available")
            return
        
        # Support multiple API keys
        key_env_vars = [
            'GEMINI_API_KEY',
            'GOOGLE_GENERATIVE_AI_API_KEY',
            'GOOGLE_AI_API_KEY',
            'GEMINI_API_KEY_2',
            'GEMINI_API_KEY_3',
            'GEMINI_API_KEY_4',
            'GEMINI_API_KEY_5',
            'GEMINI_API_KEY_6',
            'GEMINI_API_KEY_7',
            'GEMINI_API_KEY_8',
        ]
        
        seen_keys = set()
        
        for env_var in key_env_vars:
            key = os.getenv(env_var)
            if key and len(key) > 10 and key not in seen_keys:
                seen_keys.add(key)
                try:
                    client = genai.Client(api_key=key)
                    self._keys.append(KeyState(
                        key=key,
                        client=client,
                    ))
                except Exception as e:
                    logger.warning(f"Failed to initialize key from {env_var}: {e}")
        
        if not self._keys:
            logger.error("🚨 No Gemini API keys configured!")
        else:
            logger.info(f"✅ Loaded {len(self._keys)} Gemini API key(s)")
            self._initialized = True
    
    def is_rotatable_error(self, error: Exception) -> bool:
        """Check if an error should trigger key rotation"""
        error_str = str(error).lower()
        
        # Check for 429 status
        if '429' in error_str:
            return True
        
        # Check error message patterns
        return any(pattern in error_str for pattern in ROTATABLE_ERROR_PATTERNS)
    
    def _check_cooldowns(self) -> None:
        """Check and clear expired cooldowns"""
        now = time.time()
        for i, key_state in enumerate(self._keys):
            if key_state.cooldown_until and now > key_state.cooldown_until:
                key_state.cooldown_until = None
                key_state.is_healthy = True
                logger.info(f"✅ Key {i + 1} cooldown expired, marking healthy")
    
    def _get_healthy_key(self) -> Optional[KeyState]:
        """Get the first healthy key"""
        # First try current key
        if self._keys and self._keys[self._current_index].is_healthy:
            return self._keys[self._current_index]
        
        # Otherwise find any healthy key
        for i, key_state in enumerate(self._keys):
            if key_state.is_healthy:
                self._current_index = i
                return key_state
        
        return None
    
    def get_current_client(self) -> Optional[Any]:
        """Get the current healthy key's client"""
        with self._lock:
            self._check_cooldowns()
            healthy_key = self._get_healthy_key()
            
            if not healthy_key:
                logger.error("🚨 No healthy Gemini API keys available!")
                return None
            
            return healthy_key.client
    
    def rotate_on_error(self, error: Exception) -> bool:
        """
        Mark current key as rate limited and rotate to next.
        Returns True if rotation was successful.
        """
        with self._lock:
            if not self._keys:
                return False
            
            current_key = self._keys[self._current_index]
            
            # Idempotency check
            if not current_key.is_healthy:
                return self._rotate_to_next_healthy_key()
            
            error_message = str(error)
            
            # Determine cooldown duration
            cooldown = RATE_LIMIT_COOLDOWN
            if 'quota' in error_message.lower():
                cooldown = QUOTA_EXHAUSTED_COOLDOWN
            elif '401' in error_message or 'invalid' in error_message.lower():
                cooldown = INVALID_KEY_COOLDOWN
            
            # Mark current key as unhealthy
            current_key.is_healthy = False
            current_key.cooldown_until = time.time() + cooldown
            current_key.last_error = error_message
            current_key.error_count += 1
            
            logger.warning(
                f"🔄 Key {self._current_index + 1} rate limited. "
                f"Cooldown: {cooldown}s, Error count: {current_key.error_count}"
            )
            
            # Try to find next healthy key
            rotated = self._rotate_to_next_healthy_key()
            
            if rotated:
                logger.info(f"✅ Rotated to key {self._current_index + 1}")
            else:
                logger.error("🚨 No healthy keys available after rotation!")
            
            return rotated
    
    def _rotate_to_next_healthy_key(self) -> bool:
        """Rotate to the next healthy key"""
        self._check_cooldowns()
        
        start_index = self._current_index
        attempts = 0
        
        while attempts < len(self._keys):
            self._current_index = (self._current_index + 1) % len(self._keys)
            if self._keys[self._current_index].is_healthy:
                return True
            attempts += 1
        
        # No healthy keys found
        self._current_index = start_index
        return False
    
    async def generate_content(
        self,
        contents: str,
        model: str = MODELS['LITE'],
        config: Optional[Dict[str, Any]] = None
    ) -> Any:
        """
        Generate content using the current healthy key.
        
        Args:
            contents: The prompt/content to send
            model: Model name (default: gemini-flash-lite-latest)
            config: Optional generation config
        """
        client = self.get_current_client()
        if not client:
            raise RuntimeError("No healthy Gemini API keys available")
        
        return client.models.generate_content(
            model=model,
            contents=contents,
            config=config
        )
    
    async def generate_content_stream(
        self,
        contents: str,
        model: str = MODELS['LITE'],
        config: Optional[Dict[str, Any]] = None
    ):
        """Generate content with streaming"""
        client = self.get_current_client()
        if not client:
            raise RuntimeError("No healthy Gemini API keys available")
        
        return client.models.generate_content_stream(
            model=model,
            contents=contents,
            config=config
        )
    
    def execute_with_retry(
        self,
        operation: Callable[[Any], T],
        max_retries: int = 3
    ) -> T:
        """
        Execute a Gemini call with automatic key rotation on failure.
        
        This is the main method to use for all Gemini calls with retry logic.
        
        Args:
            operation: A callable that takes a genai.Client and returns a result
            max_retries: Maximum number of retry attempts
            
        Returns:
            The result of the operation
            
        Example:
            result = manager.execute_with_retry(
                lambda client: client.models.generate_content(
                    model='gemini-flash-lite-latest',
                    contents='Hello!'
                )
            )
        """
        last_error: Optional[Exception] = None
        
        for attempt in range(max_retries):
            client = self.get_current_client()
            if not client:
                raise RuntimeError("No healthy Gemini API keys available")
            
            try:
                return operation(client)
            except Exception as error:
                last_error = error
                
                if self.is_rotatable_error(error):
                    rotated = self.rotate_on_error(error)
                    if rotated:
                        logger.info(f"Retrying with new key (attempt {attempt + 1}/{max_retries})")
                        continue
                
                # If not rotatable or couldn't rotate, raise
                raise
        
        raise last_error or RuntimeError("All Gemini keys exhausted")
    
    async def execute_with_retry_async(
        self,
        operation: Callable[[Any], T],
        max_retries: int = 3
    ) -> T:
        """Async version of execute_with_retry"""
        last_error: Optional[Exception] = None
        
        for attempt in range(max_retries):
            client = self.get_current_client()
            if not client:
                raise RuntimeError("No healthy Gemini API keys available")
            
            try:
                result = operation(client)
                # Handle coroutines
                if hasattr(result, '__await__'):
                    return await result
                return result
            except Exception as error:
                last_error = error
                
                if self.is_rotatable_error(error):
                    rotated = self.rotate_on_error(error)
                    if rotated:
                        logger.info(f"Retrying with new key (attempt {attempt + 1}/{max_retries})")
                        continue
                
                raise
        
        raise last_error or RuntimeError("All Gemini keys exhausted")
    
    def get_key_status(self) -> List[Dict[str, Any]]:
        """Get status of all keys (for health endpoint)"""
        with self._lock:
            self._check_cooldowns()
            now = time.time()
            
            return [
                {
                    'index': i + 1,
                    'is_healthy': key.is_healthy,
                    'in_cooldown': key.cooldown_until is not None and key.cooldown_until > now,
                    'cooldown_remaining': max(0, key.cooldown_until - now) if key.cooldown_until else None,
                    'last_error': key.last_error,
                    'error_count': key.error_count,
                }
                for i, key in enumerate(self._keys)
            ]
    
    def get_healthy_key_count(self) -> int:
        """Get count of healthy keys"""
        with self._lock:
            self._check_cooldowns()
            return sum(1 for k in self._keys if k.is_healthy)
    
    def get_total_key_count(self) -> int:
        """Get total key count"""
        return len(self._keys)
    
    def has_available_keys(self) -> bool:
        """Check if any keys are available"""
        return self.get_healthy_key_count() > 0
    
    def is_initialized(self) -> bool:
        """Check if manager is initialized with at least one key"""
        return self._initialized and len(self._keys) > 0


# Singleton instance
gemini_key_manager = GeminiKeyManager()


# Convenience functions
def get_gemini_client():
    """Get the current healthy Gemini client"""
    return gemini_key_manager.get_current_client()


def execute_gemini_with_retry(operation: Callable[[Any], T], max_retries: int = 3) -> T:
    """Execute a Gemini operation with automatic key rotation"""
    return gemini_key_manager.execute_with_retry(operation, max_retries)
