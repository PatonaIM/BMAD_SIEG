"""Conversation memory management for LangChain integration."""
from typing import Any

import structlog
import tiktoken
from langchain_classic.memory import ConversationBufferMemory
from langchain_core.messages import AIMessage, HumanMessage, SystemMessage

from app.core.config import settings

logger = structlog.get_logger().bind(service="conversation_memory")

# Token limits for models (80% of actual limits for safety margin)
MODEL_TOKEN_LIMITS = {
    "gpt-4o-mini": 102_400,  # 80% of 128K
    "gpt-4": 102_400,        # 80% of 128K
    "gpt-3.5-turbo": 12_800  # 80% of 16K
}

MAX_MESSAGES_AFTER_TRUNCATION = 10


class ConversationMemoryManager:
    """
    Manages LangChain conversation memory serialization and token counting.
    
    Features:
    - Serialize/deserialize LangChain ConversationBufferMemory to/from JSON
    - Token counting using tiktoken
    - Automatic conversation truncation when approaching context limits
    - Session state validation with defensive defaults
    
    Usage:
        manager = ConversationMemoryManager()
        
        # Serialize memory to store in database
        memory_dict = manager.serialize_memory(langchain_memory)
        
        # Deserialize memory from database
        langchain_memory = manager.deserialize_memory(memory_dict)
        
        # Check if truncation needed
        if manager.should_truncate(memory_dict):
            memory_dict = manager.truncate_memory(memory_dict)
    """

    def __init__(self, model_name: str | None = None):
        """
        Initialize conversation memory manager.
        
        Args:
            model_name: OpenAI model name (defaults to settings.openai_model)
        """
        self.model_name = model_name or settings.openai_model
        self.token_limit = MODEL_TOKEN_LIMITS.get(self.model_name, 102_400)

        try:
            self.encoding = tiktoken.encoding_for_model(self.model_name)
        except KeyError:
            # Fallback to cl100k_base for unknown models
            logger.warning(
                "model_not_found_using_fallback",
                model=self.model_name
            )
            self.encoding = tiktoken.get_encoding("cl100k_base")

    def serialize_memory(self, memory: ConversationBufferMemory) -> dict[str, Any]:
        """
        Serialize LangChain memory to JSON-compatible dictionary.
        
        Args:
            memory: LangChain ConversationBufferMemory instance
            
        Returns:
            Dictionary with messages and metadata
        """
        try:
            # Extract message history
            messages = []
            for message in memory.chat_memory.messages:
                if isinstance(message, SystemMessage):
                    messages.append({"role": "system", "content": message.content})
                elif isinstance(message, HumanMessage):
                    messages.append({"role": "user", "content": message.content})
                elif isinstance(message, AIMessage):
                    messages.append({"role": "assistant", "content": message.content})

            # Count tokens
            token_count = self._count_tokens(messages)

            serialized = {
                "messages": messages,
                "metadata": {
                    "token_count": token_count,
                    "message_count": len(messages),
                    "model": self.model_name
                }
            }

            logger.info(
                "memory_serialized",
                message_count=len(messages),
                token_count=token_count
            )

            return serialized

        except Exception as e:
            logger.error("memory_serialization_failed", error=str(e))
            raise

    def deserialize_memory(
        self,
        data: dict[str, Any] | None
    ) -> ConversationBufferMemory:
        """
        Reconstruct LangChain memory from stored JSON.
        
        Args:
            data: Dictionary with messages and metadata (or None for new session)
            
        Returns:
            ConversationBufferMemory with restored history
        """
        memory = ConversationBufferMemory(return_messages=True)

        # Handle empty/new sessions
        if not data or "messages" not in data:
            logger.info("deserializing_empty_memory")
            return memory

        try:
            # Restore messages
            messages = data.get("messages", [])
            for msg in messages:
                role = msg.get("role")
                content = msg.get("content", "")

                if role == "system":
                    memory.chat_memory.add_message(SystemMessage(content=content))
                elif role == "user":
                    memory.chat_memory.add_message(HumanMessage(content=content))
                elif role == "assistant":
                    memory.chat_memory.add_message(AIMessage(content=content))

            token_count = data.get("metadata", {}).get("token_count", 0)
            logger.info(
                "memory_deserialized",
                message_count=len(messages),
                token_count=token_count
            )

            return memory

        except Exception as e:
            logger.error(
                "memory_deserialization_failed",
                error=str(e),
                falling_back_to_empty=True
            )
            # Return empty memory on corruption (defensive coding)
            return ConversationBufferMemory(return_messages=True)

    def _count_tokens(self, messages: list[dict[str, str]]) -> int:
        """
        Count tokens in message list using tiktoken.
        
        Args:
            messages: List of message dictionaries with role and content
            
        Returns:
            Total token count
        """
        total_tokens = 0

        for message in messages:
            # Tokens per message: role (4) + content + formatting (3)
            role_tokens = len(self.encoding.encode(message.get("role", "")))
            content_tokens = len(self.encoding.encode(message.get("content", "")))
            total_tokens += role_tokens + content_tokens + 7  # Formatting overhead

        # Add 3 tokens for the assistant reply primer
        total_tokens += 3

        return total_tokens

    def should_truncate(self, memory_data: dict[str, Any]) -> bool:
        """
        Check if conversation should be truncated.
        
        Args:
            memory_data: Serialized memory dictionary
            
        Returns:
            True if token count exceeds 80% of limit
        """
        token_count = memory_data.get("metadata", {}).get("token_count", 0)
        return token_count > self.token_limit

    def truncate_memory(
        self,
        memory_data: dict[str, Any],
        keep_last_n: int = MAX_MESSAGES_AFTER_TRUNCATION
    ) -> dict[str, Any]:
        """
        Truncate conversation history to prevent context overflow.
        
        Keeps system prompt + last N messages.
        
        Args:
            memory_data: Serialized memory dictionary
            keep_last_n: Number of recent messages to keep
            
        Returns:
            Truncated memory dictionary
        """
        messages = memory_data.get("messages", [])

        if len(messages) <= keep_last_n:
            return memory_data

        # Separate system messages from conversation
        system_messages = [m for m in messages if m.get("role") == "system"]
        conversation_messages = [m for m in messages if m.get("role") != "system"]

        # Keep system messages + last N conversation messages
        truncated_messages = system_messages + conversation_messages[-keep_last_n:]

        # Recalculate token count
        token_count = self._count_tokens(truncated_messages)

        truncated_data = {
            "messages": truncated_messages,
            "metadata": {
                "token_count": token_count,
                "message_count": len(truncated_messages),
                "model": self.model_name,
                "truncated": True,
                "original_message_count": len(messages)
            }
        }

        logger.warning(
            "memory_truncated",
            original_count=len(messages),
            truncated_count=len(truncated_messages),
            tokens_after_truncation=token_count
        )

        return truncated_data

    def validate_session_state(
        self,
        session_state: dict[str, Any]
    ) -> dict[str, Any]:
        """
        Validate and provide defaults for session state fields.
        
        Defensive coding to handle missing or corrupted state.
        
        Args:
            session_state: Session state dictionary (may be incomplete)
            
        Returns:
            Validated session state with defaults
        """
        defaults = {
            "current_difficulty_level": "warmup",
            "questions_asked_count": 0,
            "skill_boundaries_identified": {},
            "progression_state": {
                "response_scores": [],
                "avg_score_by_level": {},
                "concepts_demonstrated": [],
                "level_transitions": []
            }
        }

        # Merge with defaults (session_state takes precedence)
        validated = {**defaults, **session_state}

        logger.debug(
            "session_state_validated",
            has_boundaries=bool(validated["skill_boundaries_identified"]),
            questions_asked=validated["questions_asked_count"]
        )

        return validated

    def add_system_message(
        self,
        memory_data: dict[str, Any],
        system_prompt: str
    ) -> dict[str, Any]:
        """
        Add or update system message at the beginning of conversation.
        
        Args:
            memory_data: Serialized memory dictionary
            system_prompt: System prompt text
            
        Returns:
            Updated memory dictionary
        """
        messages = memory_data.get("messages", [])

        # Remove existing system messages
        messages = [m for m in messages if m.get("role") != "system"]

        # Add new system message at the beginning
        messages.insert(0, {"role": "system", "content": system_prompt})

        # Update token count
        token_count = self._count_tokens(messages)

        return {
            "messages": messages,
            "metadata": {
                "token_count": token_count,
                "message_count": len(messages),
                "model": self.model_name
            }
        }
