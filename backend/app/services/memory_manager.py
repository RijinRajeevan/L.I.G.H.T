import logging
from typing import List, Dict

logger = logging.getLogger(__name__)

class MemoryManager:
    """
    Sliding-window memory manager to prevent context overflow for LLM generation.
    Retains recent interactions while gracefully truncating older history.
    """
    def __init__(self, max_tokens=6000):
        # 6000 token limit applies to the history window.
        self.max_tokens = max_tokens

    def _approximate_tokens(self, text: str) -> int:
        # A rough approximation: 1 token ~= 4 chars
        # This keeps the dependency tree light without needing heavy tiktoken natively.
        return len(text) // 4

    def manage_history(self, history: List[Dict[str, str]]) -> List[Dict[str, str]]:
        if not history:
            return []
            
        total_tokens = sum(self._approximate_tokens(msg.get("text", "")) for msg in history)
        
        if total_tokens <= self.max_tokens:
            return history
            
        logger.warning(f"Session history exceeds {self.max_tokens} tokens ({total_tokens}). Truncating sliding window.")
        
        retained = []
        current_tokens = 0
        
        # Traverse history backwards to keep the most recent messages
        for msg in reversed(history):
            msg_tokens = self._approximate_tokens(msg.get("text", ""))
            if current_tokens + msg_tokens > self.max_tokens:
                break
            retained.insert(0, msg)
            current_tokens += msg_tokens
            
        # Optional: Ensure we don't start with an assistant message if strict LLM prompt ordering is required
        if retained and retained[0].get("role") == "model":
            retained.pop(0)

        return retained
