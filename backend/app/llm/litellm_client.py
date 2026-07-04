"""
LiteLLM Client for Groq Integration with Google ADK
Bridges Google ADK framework with Groq LLM via LiteLLM
"""
import os
from litellm import completion
from typing import List, Dict, Any, Optional


class LiteLLMGroqClient:
    """
    LiteLLM wrapper for Groq that's compatible with Google ADK
    """
    
    def __init__(self, model: str = "groq/llama-3.3-70b-versatile"):
        """
        Initialize LiteLLM client for Groq
        
        Args:
            model: Groq model to use (prefixed with 'groq/')
        """
        self.model = model
        self.api_key = os.getenv("GROQ_API_KEY")
        
        if not self.api_key:
            raise ValueError("GROQ_API_KEY environment variable not set")
    
    def chat_completion(
        self,
        messages: List[Dict[str, str]],
        temperature: float = 0.7,
        max_tokens: Optional[int] = None,
        **kwargs
    ) -> Dict[str, Any]:
        """
        Generate chat completion using Groq via LiteLLM
        
        Args:
            messages: List of message dicts with 'role' and 'content'
            temperature: Sampling temperature
            max_tokens: Maximum tokens to generate
            **kwargs: Additional parameters for litellm.completion
        
        Returns:
            Response dict with 'content' and metadata
        """
        try:
            response = completion(
                model=self.model,
                messages=messages,
                temperature=temperature,
                max_tokens=max_tokens,
                api_key=self.api_key,
                **kwargs
            )
            
            # Extract content from response
            content = response.choices[0].message.content
            
            return {
                "content": content,
                "model": self.model,
                "usage": response.usage._asdict() if hasattr(response, 'usage') else {},
                "finish_reason": response.choices[0].finish_reason
            }
            
        except Exception as e:
            raise Exception(f"LiteLLM Groq completion failed: {str(e)}")
    
    def get_completion(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        temperature: float = 0.7,
        max_tokens: Optional[int] = None
    ) -> str:
        """
        Simple completion interface (backward compatible with GroqClient)
        
        Args:
            prompt: User prompt
            system_prompt: Optional system prompt
            temperature: Sampling temperature
            max_tokens: Maximum tokens
        
        Returns:
            Generated text content
        """
        messages = []
        
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        
        messages.append({"role": "user", "content": prompt})
        
        response = self.chat_completion(
            messages=messages,
            temperature=temperature,
            max_tokens=max_tokens
        )
        
        return response["content"]


# Singleton instance
_client = None

def get_litellm_client() -> LiteLLMGroqClient:
    """Get or create LiteLLM client instance"""
    global _client
    if _client is None:
        _client = LiteLLMGroqClient()
    return _client
