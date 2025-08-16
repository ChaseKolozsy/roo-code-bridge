"""Provider configuration management for Roo-Code bridge."""

import json
from typing import Dict, List, Optional, Any
from datetime import datetime
import logging

from messages.types import ProviderConfig

logger = logging.getLogger(__name__)


class ProviderManager:
    """Manages provider configuration for Roo-Code."""
    
    def __init__(self):
        self.active_configs: Dict[str, ProviderConfig] = {}
        self.available_providers = {
            "anthropic": {
                "models": ["claude-3-opus", "claude-3-sonnet", "claude-3-haiku", "claude-2.1", "claude-2"],
                "default_max_tokens": 4096,
                "default_temperature": 0.7,
                "supports_vision": True,
                "max_context": 200000
            },
            "openai": {
                "models": ["gpt-4-turbo", "gpt-4", "gpt-3.5-turbo", "gpt-4-vision-preview"],
                "default_max_tokens": 4096,
                "default_temperature": 0.7,
                "supports_vision": True,
                "max_context": 128000
            },
            "gemini": {
                "models": ["gemini-pro", "gemini-pro-vision", "gemini-1.5-pro"],
                "default_max_tokens": 8192,
                "default_temperature": 0.7,
                "supports_vision": True,
                "max_context": 1000000
            },
            "ollama": {
                "models": ["llama2", "codellama", "mistral", "mixtral", "deepseek-coder"],
                "default_max_tokens": 4096,
                "default_temperature": 0.7,
                "supports_vision": False,
                "max_context": 32000
            },
            "azure": {
                "models": ["gpt-4", "gpt-35-turbo"],
                "default_max_tokens": 4096,
                "default_temperature": 0.7,
                "supports_vision": False,
                "max_context": 32000
            },
            "openai-compatible": {
                "models": ["qwen-3-coder", "qwen-2.5-coder", "deepseek-coder", "codellama", "custom"],
                "default_max_tokens": 4096,
                "default_temperature": 0.7,
                "supports_vision": False,
                "max_context": 131000,
                "default_base_url": "http://localhost:3000/v1"
            }
        }
        
    async def set_provider(self, client_id: str, config: Dict[str, Any]) -> Dict[str, Any]:
        """Set provider configuration for a client."""
        
        # Validate provider
        provider = config.get("provider")
        if provider not in self.available_providers:
            raise ValueError(f"Unknown provider: {provider}")
            
        # Validate model
        model = config.get("model")
        if model and model not in self.available_providers[provider]["models"]:
            logger.warning(f"Model {model} not in known models for {provider}, allowing anyway")
            
        # Apply defaults if not specified
        provider_info = self.available_providers[provider]
        if "max_tokens" not in config:
            config["max_tokens"] = provider_info["default_max_tokens"]
        if "temperature" not in config:
            config["temperature"] = provider_info["default_temperature"]
        if "context_length" not in config:
            config["context_length"] = provider_info["max_context"]
        
        # Set default base URL for OpenAI compatible providers
        if provider == "openai-compatible" and "base_url" not in config:
            config["base_url"] = provider_info["default_base_url"]
            
        # Create and store configuration
        provider_config = ProviderConfig(**config)
        self.active_configs[client_id] = provider_config
        
        logger.info(f"Set provider config for {client_id}: {provider}/{model}")
        
        # Return formatted message for Roo-Code
        return {
            "type": "saveApiConfiguration",
            "data": {
                "apiProvider": provider_config.provider,
                "apiModelId": provider_config.model,
                "apiKey": provider_config.api_key,
                "apiUrl": provider_config.base_url,
                "maxTokens": provider_config.max_tokens,
                "temperature": provider_config.temperature,
                "contextLength": provider_config.context_length,
                "topP": provider_config.top_p,
                "topK": provider_config.top_k,
                "customInstructions": provider_config.custom_instructions,
            }
        }
        
    async def get_provider(self, client_id: str) -> Optional[ProviderConfig]:
        """Get current provider configuration for a client."""
        return self.active_configs.get(client_id)
        
    async def get_available_models(self, provider: str) -> List[str]:
        """Get list of available models for a provider."""
        if provider not in self.available_providers:
            return []
        return self.available_providers[provider]["models"]
        
    async def get_available_providers(self) -> Dict[str, Any]:
        """Get information about all available providers."""
        return {
            name: {
                "models": info["models"],
                "supports_vision": info["supports_vision"],
                "max_context": info["max_context"]
            }
            for name, info in self.available_providers.items()
        }
        
    def validate_config(self, config: Dict[str, Any]) -> bool:
        """Validate a provider configuration."""
        try:
            # Check required fields
            if "provider" not in config or "model" not in config:
                return False
                
            # Validate provider
            if config["provider"] not in self.available_providers:
                return False
                
            # Validate numeric constraints
            if "max_tokens" in config:
                if not isinstance(config["max_tokens"], (int, float)) or config["max_tokens"] <= 0:
                    return False
                    
            if "temperature" in config:
                if not isinstance(config["temperature"], (int, float)) or not (0 <= config["temperature"] <= 2):
                    return False
                    
            if "context_length" in config:
                provider_max = self.available_providers[config["provider"]]["max_context"]
                if config["context_length"] > provider_max:
                    logger.warning(f"Context length {config['context_length']} exceeds provider max {provider_max}")
                    
            return True
            
        except Exception as e:
            logger.error(f"Config validation error: {e}")
            return False
            
    def get_default_config(self, provider: str = "openai-compatible") -> Dict[str, Any]:
        """Get default configuration for a provider."""
        if provider not in self.available_providers:
            provider = "openai-compatible"
            
        info = self.available_providers[provider]
        config = {
            "provider": provider,
            "model": "qwen-3-coder",  # Default to qwen-3-coder
            "max_tokens": info["default_max_tokens"],
            "temperature": info["default_temperature"],
            "context_length": 131000  # Set to your preferred context length
        }
        
        # Add base URL for OpenAI compatible providers
        if provider == "openai-compatible":
            config["base_url"] = "http://localhost:3000/v1"
            
        return config