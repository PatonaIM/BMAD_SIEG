# AI Provider System - Quick Start Guide

**Last Updated:** 2025-10-29 (Story 1.4)  
**Status:** Production Ready - All Tests Passing (62/62, 84% Coverage)

---

## Overview
This system provides a flexible abstraction for AI providers, currently supporting OpenAI with LangChain integration and a mock provider for testing.

## Basic Usage

### 1. Using the Provider Factory (Recommended)

\`\`\`python
from app.providers.mock_ai_provider import get_ai_provider

# Automatically uses MockAIProvider if USE_MOCK_AI=true, otherwise OpenAIProvider
provider = get_ai_provider(role_type="react")

# Generate a completion
messages = [
    {"role": "system", "content": "You are an interviewer"},
    {"role": "user", "content": "Tell me about React hooks"}
]

response = await provider.generate_completion(messages)
print(response)

# Count tokens
token_count = await provider.count_tokens("Hello, how are you?")
print(f"Token count: {token_count}")
\`\`\`

### 2. Direct Provider Usage

\`\`\`python
from app.providers.openai_provider import OpenAIProvider
from app.providers.mock_ai_provider import MockAIProvider

# Use OpenAI (requires valid API key)
openai_provider = OpenAIProvider()
response = await openai_provider.generate_completion(messages)

# Use Mock (no API calls, zero cost)
mock_provider = MockAIProvider(role_type="python")
response = await mock_provider.generate_completion(messages)
\`\`\`

### 3. With Conversation Memory

\`\`\`python
from app.services.conversation_memory import ConversationMemoryManager
from app.providers.mock_ai_provider import get_ai_provider

# Initialize
memory = ConversationMemoryManager()
provider = get_ai_provider(role_type="javascript")

# Conversation loop
while True:
    user_input = input("You: ")
    if user_input.lower() == "quit":
        break
    
    # Get all messages for context
    messages = memory.get_messages()
    messages.append({"role": "user", "content": user_input})
    
    # Get AI response
    ai_response = await provider.generate_completion(messages)
    print(f"AI: {ai_response}")
    
    # Save to memory
    memory.save_context(
        inputs={"user": user_input},
        outputs={"assistant": ai_response}
    )

# Save to database (JSON format)
json_data = memory.serialize_to_json()
# Store json_data in InterviewSession.conversation_memory field
\`\`\`

### 4. With Prompt Templates

\`\`\`python
from app.utils.prompt_loader import PromptTemplateManager
from app.providers.mock_ai_provider import get_ai_provider

# Load interview prompt for specific role
prompt_manager = PromptTemplateManager()
system_prompt = prompt_manager.get_interview_prompt(role_type="react")

# Use in conversation
provider = get_ai_provider(role_type="react")
messages = [
    {"role": "system", "content": system_prompt},
    {"role": "user", "content": "Let's start the interview"}
]

response = await provider.generate_completion(messages)
\`\`\`

### 5. Token Counting and Cost Tracking

\`\`\`python
from app.utils.token_counter import (
    count_tokens_for_messages,
    estimate_cost,
    estimate_interview_cost
)

# Count tokens for messages
messages = [
    {"role": "system", "content": "You are helpful"},
    {"role": "user", "content": "Hello"}
]
token_count = count_tokens_for_messages(messages, model="gpt-4o-mini")
print(f"Total tokens: {token_count}")

# Estimate cost
cost = estimate_cost(
    input_tokens=1000,
    output_tokens=500,
    model="gpt-4o-mini"
)
print(f"Cost: ${cost}")

# Estimate full interview cost
interview_cost = estimate_interview_cost(
    avg_message_length=150,
    message_count=25,
    model="gpt-4o-mini"
)
print(f"Estimated interview cost: ${interview_cost}")
\`\`\`

## Configuration

### Environment Variables

\`\`\`bash
# OpenAI API Configuration
OPENAI_API_KEY=sk-proj-your-key-here
OPENAI_MODEL=gpt-4o-mini
OPENAI_MAX_TOKENS=1000
OPENAI_TEMPERATURE=0.7

# Development Mode (use mock provider)
USE_MOCK_AI=true
\`\`\`

### Switching Between Providers

**Development/Testing (Free):**
\`\`\`bash
export USE_MOCK_AI=true
\`\`\`

**Production (Costs Money):**
\`\`\`bash
export USE_MOCK_AI=false
export OPENAI_API_KEY=sk-your-real-key
\`\`\`

## Error Handling

The OpenAI provider automatically handles:
- **Rate limits (429)**: Exponential backoff with 3 retries
- **Timeouts**: 3 retries with 5s delay
- **Server errors (500)**: 3 retries with 5s delay
- **Context length errors**: Raises `ContextLengthExceededError` (truncate history manually)
- **Authentication errors (401)**: No retry, raises immediately

\`\`\`python
from app.core.exceptions import (
    RateLimitExceededError,
    ContextLengthExceededError,
    OpenAIProviderError
)

try:
    response = await provider.generate_completion(messages)
except RateLimitExceededError:
    # Handle rate limit after all retries exhausted
    print("Rate limit exceeded, try again later")
except ContextLengthExceededError:
    # Truncate conversation history
    memory.truncate_history(keep_last_n=5)
    messages = memory.get_messages()
    response = await provider.generate_completion(messages)
except OpenAIProviderError as e:
    # Handle other provider errors
    print(f"Provider error: {e}")
\`\`\`

## Best Practices

### 1. Use Mock Provider in Tests
\`\`\`python
# In tests, always use mock to avoid API costs
provider = MockAIProvider(role_type="react")
\`\`\`

### 2. Truncate History for Long Conversations
\`\`\`python
# Keep only system prompt + last 5 exchanges
if len(memory.get_messages()) > 15:
    memory.truncate_history(keep_last_n=5)
\`\`\`

### 3. Track Costs
\`\`\`python
# Log token usage for monitoring
from app.utils.token_counter import count_tokens_for_messages

tokens_used = count_tokens_for_messages(messages)
cost = estimate_cost(tokens_used, tokens_used // 2, "gpt-4o-mini")

logger.info(
    "interview_api_call",
    tokens_used=tokens_used,
    cost_usd=float(cost),
    model="gpt-4o-mini"
)
\`\`\`

### 4. Version Control Prompts
\`\`\`python
# Prompts are in files - version control them!
# Modify prompts without code changes
# backend/app/prompts/interview_system.txt
# backend/app/prompts/react_interview.txt
\`\`\`

## Architecture

\`\`\`
AIProvider (Abstract)
├── OpenAIProvider (Production)
│   ├── Uses LangChain's ChatOpenAI
│   ├── Automatic retry logic
│   ├── Token counting with tiktoken
│   └── Error handling
└── MockAIProvider (Testing)
    ├── Pre-defined responses
    ├── Simulated delays
    └── Zero cost

get_ai_provider() factory
├── Checks USE_MOCK_AI setting
└── Returns appropriate provider
\`\`\`

## Common Patterns

### Pattern 1: Complete Interview Session
\`\`\`python
# Setup
memory = ConversationMemoryManager()
provider = get_ai_provider(role_type="react")
prompt_manager = PromptTemplateManager()

# Load interview prompt
system_prompt = prompt_manager.get_interview_prompt("react")
messages = [{"role": "system", "content": system_prompt}]

# Interview loop
for question_num in range(5):
    # Get AI question
    ai_question = await provider.generate_completion(messages)
    messages.append({"role": "assistant", "content": ai_question})
    
    # Get candidate answer
    candidate_answer = get_candidate_input()  # Your input method
    messages.append({"role": "user", "content": candidate_answer})
    
    # Save to memory
    memory.save_context(
        inputs={"user": candidate_answer},
        outputs={"assistant": ai_question}
    )

# Save to database
conversation_data = memory.serialize_to_json()
\`\`\`

### Pattern 2: Load Existing Conversation
\`\`\`python
# Load from database
json_data = get_from_database()  # Your DB retrieval

# Deserialize
memory = ConversationMemoryManager.deserialize_from_json(json_data)

# Continue conversation
messages = memory.get_messages()
messages.append({"role": "user", "content": "New question"})
response = await provider.generate_completion(messages)
\`\`\`

## Troubleshooting

**Problem:** `ModuleNotFoundError: No module named 'langchain.memory'`
**Solution:** Use langchain_core messages directly (already implemented)

**Problem:** `OpenAI API key not found`
**Solution:** Set `OPENAI_API_KEY` env var or use `USE_MOCK_AI=true`

**Problem:** `Context length exceeded`
**Solution:** Truncate conversation history: `memory.truncate_history(keep_last_n=5)`

**Problem:** Rate limits
**Solution:** Use GPT-4o-mini (cheaper, higher limits) or implement request throttling
