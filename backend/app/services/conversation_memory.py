"""Conversation memory management using LangChain."""

from datetime import datetime
from typing import Any

import structlog
from langchain_core.messages import AIMessage, BaseMessage, HumanMessage, SystemMessage

logger = structlog.get_logger()


class ConversationMemoryManager:
    """
    Manages conversation memory for interview sessions.

    Features:
    - Stores complete conversation history
    - Serializes to/from JSON for database persistence
    - Truncates history to prevent context length errors
    - Integrates with InterviewSession.conversation_memory JSONB field

    JSONB Schema:
    {
        "messages": [
            {"role": "system", "content": "You are an AI interviewer..."},
            {"role": "assistant", "content": "Tell me about your React experience..."},
            {"role": "user", "content": "I have 3 years experience..."}
        ],
        "memory_metadata": {
            "created_at": "2025-10-29T12:00:00Z",
            "last_updated": "2025-10-29T12:05:00Z",
            "message_count": 5,
            "truncation_count": 0
        }
    }

    Usage:
        # Initialize new conversation
        memory_manager = ConversationMemoryManager()

        # Save exchange
        memory_manager.save_context(
            inputs={"user": "Tell me about React hooks"},
            outputs={"assistant": "React hooks are..."}
        )

        # Serialize for database
        json_data = memory_manager.serialize_to_json()

        # Later: deserialize from database
        memory_manager = ConversationMemoryManager.deserialize_from_json(json_data)
    """

    def __init__(self, messages: list[BaseMessage] = None):
        """
        Initialize conversation memory manager.

        Args:
            messages: Existing list of messages or None for new conversation
        """
        self.messages = messages or []
        self.created_at = datetime.utcnow()
        self.last_updated = datetime.utcnow()
        self.truncation_count = 0

        logger.info(
            "conversation_memory_initialized",
            created_at=self.created_at.isoformat(),
        )

    def save_context(self, inputs: dict[str, Any], outputs: dict[str, Any]) -> None:
        """
        Save a conversation exchange to memory.

        Args:
            inputs: User input dict (e.g., {"user": "message"})
            outputs: AI output dict (e.g., {"assistant": "response"})
        """
        # Add user message
        if "user" in inputs:
            self.messages.append(HumanMessage(content=inputs["user"]))

        # Add assistant message
        if "assistant" in outputs:
            self.messages.append(AIMessage(content=outputs["assistant"]))

        self.last_updated = datetime.utcnow()

        logger.debug(
            "context_saved",
            message_count=len(self.messages),
            last_updated=self.last_updated.isoformat(),
        )

    def load_memory_variables(self) -> dict[str, Any]:
        """
        Load memory variables for passing to LLM.

        Returns:
            Dict containing chat history
        """
        return {"chat_history": self.messages}

    def get_messages(self) -> list[dict[str, str]]:
        """
        Get all messages in standard format.

        Returns:
            List of message dicts with 'role' and 'content'
        """
        messages = []
        for msg in self.messages:
            role = self._get_message_role(msg)
            messages.append({
                "role": role,
                "content": msg.content,
            })
        return messages

    def serialize_to_json(self) -> dict[str, Any]:
        """
        Serialize conversation memory to JSON for database storage.

        Returns:
            Dict suitable for JSONB storage in InterviewSession.conversation_memory
        """
        messages = self.get_messages()

        json_data = {
            "messages": messages,
            "memory_metadata": {
                "created_at": self.created_at.isoformat(),
                "last_updated": self.last_updated.isoformat(),
                "message_count": len(messages),
                "truncation_count": self.truncation_count,
            },
        }

        logger.debug(
            "memory_serialized",
            message_count=len(messages),
            truncation_count=self.truncation_count,
        )

        return json_data

    @classmethod
    def deserialize_from_json(cls, data: dict[str, Any]) -> "ConversationMemoryManager":
        """
        Deserialize conversation memory from database JSON.

        Args:
            data: JSON data from InterviewSession.conversation_memory

        Returns:
            ConversationMemoryManager instance with restored conversation
        """
        messages_data = data.get("messages", [])
        messages = []

        # Restore messages
        for msg in messages_data:
            role = msg["role"]
            content = msg["content"]

            # Reconstruct message based on role
            if role == "system":
                messages.append(SystemMessage(content=content))
            elif role == "user":
                messages.append(HumanMessage(content=content))
            elif role == "assistant":
                messages.append(AIMessage(content=content))

        # Create manager instance
        manager = cls(messages=messages)

        # Restore metadata
        metadata = data.get("memory_metadata", {})
        if "created_at" in metadata:
            manager.created_at = datetime.fromisoformat(metadata["created_at"])
        if "last_updated" in metadata:
            manager.last_updated = datetime.fromisoformat(metadata["last_updated"])
        if "truncation_count" in metadata:
            manager.truncation_count = metadata["truncation_count"]

        logger.info(
            "memory_deserialized",
            message_count=len(messages),
            truncation_count=manager.truncation_count,
        )

        return manager

    def truncate_history(self, keep_last_n: int = 5) -> None:
        """
        Truncate conversation history to prevent context length errors.

        Keeps system prompt (first message) + last N user/assistant exchanges.
        This prevents hitting model context limits while maintaining recent context.

        Args:
            keep_last_n: Number of recent exchanges to keep (default: 5)
        """
        if len(self.messages) <= (keep_last_n * 2 + 1):
            # No truncation needed
            return

        # Keep system message (if present) + last N exchanges
        system_messages = []
        if self.messages and isinstance(self.messages[0], SystemMessage):
            system_messages = [self.messages[0]]
            remaining = self.messages[1:]
        else:
            remaining = self.messages

        # Keep last N exchanges (N user + N assistant messages)
        recent_messages = remaining[-(keep_last_n * 2):]

        # Rebuild message list
        self.messages = system_messages + recent_messages

        self.truncation_count += 1
        self.last_updated = datetime.utcnow()

        logger.warning(
            "conversation_truncated",
            kept_messages=len(self.messages),
            truncation_count=self.truncation_count,
        )

    def clear(self) -> None:
        """Clear all conversation memory."""
        self.messages = []
        self.last_updated = datetime.utcnow()

        logger.info("conversation_memory_cleared")

    def _get_message_role(self, message: BaseMessage) -> str:
        """
        Get role string from LangChain message object.

        Args:
            message: LangChain message object

        Returns:
            str: 'system', 'user', or 'assistant'
        """
        if isinstance(message, SystemMessage):
            return "system"
        elif isinstance(message, HumanMessage):
            return "user"
        elif isinstance(message, AIMessage):
            return "assistant"
        else:
            return "user"  # Default to user for unknown types
