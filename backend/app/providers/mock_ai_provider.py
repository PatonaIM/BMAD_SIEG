"""Mock AI provider for development and testing."""

import asyncio
import random

import structlog

from app.providers.base_ai_provider import AIProvider

logger = structlog.get_logger()


class MockAIProvider(AIProvider):
    """
    Mock implementation of AIProvider for development and testing.

    Features:
    - No actual API calls (zero cost)
    - Simulates realistic response delays
    - Role-specific pre-defined responses
    - Useful for development, testing, and demos

    Usage:
        provider = MockAIProvider()
        response = await provider.generate_completion(
            messages=[
                {"role": "system", "content": "You are an interviewer"},
                {"role": "user", "content": "Tell me about React"}
            ]
        )
        # Returns: Pre-defined mock response with simulated delay
    """

    # Mock responses for different role types
    MOCK_RESPONSES = {
        "react": [
            "Great! Let's start with React fundamentals. Can you explain the difference between state and props in React?",
            "That's a good explanation. Now, tell me about your experience with React hooks. Which hooks have you used most frequently?",
            "Interesting. Can you describe a situation where you had to optimize React component performance? What approach did you take?",
            "Good insight. How do you typically handle state management in larger React applications? Have you used Redux, Context API, or other solutions?",
            "Excellent. Let's dive deeper into component patterns. Can you explain when you'd use a controlled vs uncontrolled component?",
            "That makes sense. How do you approach testing React components? What testing libraries and strategies do you prefer?",
            "Thank you for sharing that. Based on your responses, you demonstrate a solid understanding of React fundamentals and best practices.",
        ],
        "python": [
            "Excellent! Let's begin with Python basics. Can you explain the difference between a list and a tuple in Python?",
            "Good explanation. Now, tell me about your experience with Python decorators. Have you created any custom decorators?",
            "Interesting approach. How do you handle exception handling in Python? Can you walk me through your typical error handling strategy?",
            "That's a solid approach. Have you worked with asynchronous programming in Python? What's your experience with async/await?",
            "Great. Can you describe a situation where you had to optimize Python code for performance? What techniques did you use?",
            "Excellent insights. How do you approach testing in Python? What frameworks and methodologies do you prefer?",
            "Thank you. Based on your responses, you show strong Python fundamentals and practical development experience.",
        ],
        "javascript": [
            "Perfect! Let's start with JavaScript fundamentals. Can you explain how closures work in JavaScript?",
            "Good explanation. Now, tell me about your experience with asynchronous JavaScript. How do you handle Promises vs async/await?",
            "Interesting. Can you describe the event loop in JavaScript and how it affects asynchronous operations?",
            "That's a solid understanding. How do you approach error handling in asynchronous JavaScript code?",
            "Great. Have you worked with modern JavaScript (ES6+)? What features do you find most useful?",
            "Excellent. How do you ensure code quality in JavaScript projects? What tools and practices do you use?",
            "Thank you for the detailed responses. You demonstrate strong JavaScript fundamentals and modern development practices.",
        ],
        "fullstack": [
            "Excellent! Let's discuss your full-stack experience. Can you walk me through how you'd architect a typical web application?",
            "Good approach. How do you handle communication between frontend and backend? What API design patterns do you prefer?",
            "Interesting. Tell me about your experience with databases. How do you handle data modeling and optimization?",
            "That's solid. How do you approach authentication and authorization in full-stack applications?",
            "Great insights. Can you describe your deployment and DevOps experience? What tools and platforms have you used?",
            "Excellent. How do you ensure application security across the full stack? What are your key considerations?",
            "Thank you. Based on your responses, you show well-rounded full-stack development capabilities.",
        ],
    }

    def __init__(self, role_type: str = "javascript"):
        """
        Initialize mock AI provider.

        Args:
            role_type: Role type for response selection
        """
        self.role_type = role_type
        self.response_index = 0
        self.call_count = 0

        logger.info(
            "mock_ai_provider_initialized",
            role_type=role_type,
        )

    async def generate_completion(
        self,
        messages: list[dict[str, str]],
        **kwargs
    ) -> str:
        """
        Generate mock AI completion with simulated delay.

        Args:
            messages: List of message dicts (not actually used for mocking)
            **kwargs: Ignored for mock provider

        Returns:
            str: Pre-defined mock response
        """
        # Simulate realistic API delay (0.5-1.5 seconds)
        delay = random.uniform(0.5, 1.5)
        await asyncio.sleep(delay)

        # Get response set for role type
        responses = self.MOCK_RESPONSES.get(
            self.role_type,
            self.MOCK_RESPONSES["javascript"]
        )

        # Cycle through responses
        response = responses[self.response_index % len(responses)]
        self.response_index += 1
        self.call_count += 1

        logger.info(
            "mock_completion_generated",
            role_type=self.role_type,
            response_index=self.response_index,
            call_count=self.call_count,
            delay=delay,
            message_count=len(messages),
        )

        return response

    async def count_tokens(self, text: str) -> int:
        """
        Mock token counting (estimates ~4 chars per token).

        Args:
            text: Text to count tokens for

        Returns:
            int: Estimated token count
        """
        # Simple estimation: ~4 characters per token
        estimated_tokens = len(text) // 4

        logger.debug(
            "mock_tokens_counted",
            text_length=len(text),
            estimated_tokens=estimated_tokens,
        )

        return estimated_tokens


def get_ai_provider(role_type: str = "javascript") -> AIProvider:
    """
    Factory function to get appropriate AI provider based on configuration.

    Returns MockAIProvider if USE_MOCK_AI=true, otherwise OpenAIProvider.

    Args:
        role_type: Role type for interview

    Returns:
        AIProvider: Either MockAIProvider or OpenAIProvider

    Usage:
        provider = get_ai_provider(role_type="react")
        response = await provider.generate_completion(messages)
    """
    from app.core.config import settings

    if settings.use_mock_ai:
        logger.info(
            "using_mock_ai_provider",
            role_type=role_type,
        )
        return MockAIProvider(role_type=role_type)
    else:
        from app.providers.openai_provider import OpenAIProvider
        logger.info(
            "using_openai_provider",
            model=settings.openai_model,
        )
        return OpenAIProvider()
