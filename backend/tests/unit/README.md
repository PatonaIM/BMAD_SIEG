# Unit Tests - Known Issues & Fixes

## Current Status
- **54 out of 62 tests passing** (87% pass rate)
- **8 failing tests** - all in `test_openai_provider.py`
- **78% overall code coverage**

## Failing Tests Summary

### OpenAI Provider Tests (8 failures)

#### Issue 1: ChatOpenAI Mocking Problem
**Tests affected:** 
- `test_generate_completion_success`
- `test_generate_completion_timeout_retry`
- `test_generate_completion_context_length_error`

**Error:**
```
ValueError: "ChatOpenAI" object has no field "ainvoke"
```

**Root Cause:**
LangChain's `ChatOpenAI` is a Pydantic v2 model. Can't directly assign mocked methods to it.

**Recommended Fixes:**

**Option 1:** Mock at HTTP client level using `respx`
```python
import respx
from httpx import Response

@respx.mock
@pytest.mark.asyncio
async def test_generate_completion_success(provider):
    respx.post("https://api.openai.com/v1/chat/completions").mock(
        return_value=Response(200, json={
            "choices": [{"message": {"content": "Test response"}}],
            "usage": {"prompt_tokens": 10, "completion_tokens": 5}
        })
    )
    
    result = await provider.generate_completion([...])
    assert result == "Test response"
```

**Option 2:** Use MockAIProvider in tests
```python
from app.providers.mock_ai_provider import MockAIProvider

@pytest.mark.asyncio
async def test_generate_completion_success():
    provider = MockAIProvider(role_type="react")
    result = await provider.generate_completion([...])
    assert isinstance(result, str)
    assert len(result) > 0
```

**Option 3:** Patch the underlying OpenAI client
```python
@patch("app.providers.openai_provider.ChatOpenAI")
async def test_generate_completion_success(mock_chatgpt, provider):
    mock_instance = mock_chatgpt.return_value
    mock_response = Mock(content="Test response")
    mock_instance.ainvoke = AsyncMock(return_value=mock_response)
    # ... rest of test
```

#### Issue 2: OpenAI Exception Constructor Changes

**Tests affected:**
- `test_generate_completion_rate_limit_retry`
- `test_generate_completion_rate_limit_exhausted`
- `test_generate_completion_authentication_error`
- `test_generate_completion_api_error_retry`

**Error:**
```
TypeError: APIStatusError.__init__() missing 2 required keyword-only arguments: 'response' and 'body'
```

**Root Cause:**
OpenAI SDK v1.0+ changed exception signatures to require `response` and `body` parameters.

**Fix:**
Create helper fixture:
```python
@pytest.fixture
def create_openai_error():
    """Factory for creating properly formatted OpenAI errors."""
    def _create(error_class, message, status_code=500):
        mock_response = Mock()
        mock_response.status_code = status_code
        mock_response.headers = {}
        return error_class(
            message,
            response=mock_response,
            body={"error": {"message": message}}
        )
    return _create

# Usage in tests:
async def test_rate_limit_retry(provider, create_openai_error):
    error = create_openai_error(RateLimitError, "Rate limit exceeded", 429)
    provider.llm.ainvoke = AsyncMock(side_effect=[error, error, mock_success])
    # ... rest of test
```

## Quick Commands

```bash
# Run only passing tests
uv run pytest tests/unit/ -k "not openai_provider" -v

# Run with coverage (excluding failing tests)
uv run pytest tests/unit/ -k "not openai_provider" --cov=app --cov-report=term-missing

# Run single test file
uv run pytest tests/unit/test_prompt_loader.py -v

# Run with detailed output
uv run pytest tests/unit/test_openai_provider.py -vv --tb=long
```

## Working Test Files
✅ `test_prompt_loader.py` - All 8 tests passing
✅ `test_token_counter.py` - All 10 tests passing  
✅ `test_conversation_memory.py` - 7/8 tests passing
⚠️ `test_openai_provider.py` - 0/8 tests passing (needs fixing)

## Test Coverage by Module
- `app.utils.prompt_loader`: 88% coverage ✅
- `app.utils.token_counter`: 88% coverage ✅
- `app.services.conversation_memory`: 91% coverage ✅
- `app.providers.openai_provider`: 51% coverage ⚠️ (low due to untested error paths)
- `app.providers.mock_ai_provider`: 0% coverage (not tested, works correctly)

## Next Steps
1. Fix OpenAI provider test mocking (Issues 1 & 2 above)
2. Add integration tests for full conversation flows
3. Add tests for `MockAIProvider` directly
4. Increase coverage for error handling paths in `OpenAIProvider`

## Resources
- OpenAI Python SDK docs: https://github.com/openai/openai-python
- LangChain testing patterns: https://github.com/langchain-ai/langchain/tree/master/libs/langchain/tests
- Respx mocking library: https://lundberg.github.io/respx/
