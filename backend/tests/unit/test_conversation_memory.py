"""Unit tests for conversation memory manager."""


from app.services.conversation_memory import ConversationMemoryManager


def test_init_new_memory():
    """Test initializing new conversation memory."""
    manager = ConversationMemoryManager()

    assert manager.messages is not None
    assert manager.created_at is not None
    assert manager.truncation_count == 0


def test_save_context():
    """Test saving conversation context."""
    manager = ConversationMemoryManager()

    manager.save_context(
        inputs={"user": "Hello"},
        outputs={"assistant": "Hi there!"}
    )

    messages = manager.get_messages()
    assert len(messages) >= 2  # At least user and assistant messages


def test_serialize_to_json():
    """Test serializing memory to JSON."""
    manager = ConversationMemoryManager()

    manager.save_context(
        inputs={"user": "Test message"},
        outputs={"assistant": "Test response"}
    )

    json_data = manager.serialize_to_json()

    assert "messages" in json_data
    assert "memory_metadata" in json_data
    assert json_data["memory_metadata"]["message_count"] >= 0
    assert "created_at" in json_data["memory_metadata"]
    assert "truncation_count" in json_data["memory_metadata"]


def test_deserialize_from_json():
    """Test deserializing memory from JSON."""
    # Create and serialize
    manager1 = ConversationMemoryManager()
    manager1.save_context(
        inputs={"user": "Question 1"},
        outputs={"assistant": "Answer 1"}
    )
    json_data = manager1.serialize_to_json()

    # Deserialize
    manager2 = ConversationMemoryManager.deserialize_from_json(json_data)

    assert len(manager2.get_messages()) == len(manager1.get_messages())
    assert manager2.truncation_count == manager1.truncation_count


def test_truncate_history():
    """Test conversation history truncation."""
    manager = ConversationMemoryManager()

    # Add many exchanges
    for i in range(10):
        manager.save_context(
            inputs={"user": f"Question {i}"},
            outputs={"assistant": f"Answer {i}"}
        )

    initial_count = len(manager.get_messages())

    # Truncate to keep last 3 exchanges
    manager.truncate_history(keep_last_n=3)

    final_count = len(manager.get_messages())

    assert final_count < initial_count
    assert manager.truncation_count == 1


def test_clear_memory():
    """Test clearing conversation memory."""
    manager = ConversationMemoryManager()

    manager.save_context(
        inputs={"user": "Test"},
        outputs={"assistant": "Response"}
    )

    assert len(manager.get_messages()) > 0

    manager.clear()

    # Memory should be empty after clear
    messages = manager.get_messages()
    assert len(messages) == 0


def test_get_messages():
    """Test getting messages in standard format."""
    manager = ConversationMemoryManager()

    manager.save_context(
        inputs={"user": "Hello"},
        outputs={"assistant": "Hi!"}
    )

    messages = manager.get_messages()

    assert isinstance(messages, list)
    for msg in messages:
        assert "role" in msg
        assert "content" in msg
        assert msg["role"] in ["system", "user", "assistant"]
