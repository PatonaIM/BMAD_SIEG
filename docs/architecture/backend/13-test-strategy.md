# Test Strategy

## Testing Pyramid

```
           /\
          /E2E\        10% - End-to-end tests (full workflows)
         /______\
        /        \
       /Integration\ 30% - Integration tests (service + DB)
      /____________\
     /              \
    /      Unit      \ 60% - Unit tests (pure logic)
   /__________________\
```

## Unit Tests (60% of tests)

```python
# tests/unit/test_auth_service.py

@pytest.mark.asyncio
async def test_register_candidate_success():
    # Arrange
    mock_repo = Mock(spec=CandidateRepository)
    mock_repo.get_by_email.return_value = None  # Email available
    auth_service = AuthService(candidate_repo=mock_repo)
    
    # Act
    candidate = await auth_service.register_candidate(
        email="test@example.com",
        password="SecurePass123!",
        full_name="Test User"
    )
    
    # Assert
    assert candidate.email == "test@example.com"
    assert candidate.password_hash != "SecurePass123!"  # Hashed
    mock_repo.create.assert_called_once()
```

## Integration Tests (30% of tests)

```python
# tests/integration/test_interview_flow.py

@pytest.mark.asyncio
async def test_complete_interview_flow(test_db, test_candidate):
    # Uses real database (test instance)
    interview_service = InterviewService(db=test_db)
    
    # Start interview
    interview = await interview_service.start_interview(
        candidate_id=test_candidate.id,
        role_type="react"
    )
    
    # Simulate Q&A
    await interview_service.process_response(interview.id, "I have 3 years React experience")
    
    # Complete interview
    result = await interview_service.complete_interview(interview.id)
    
    assert result.status == "completed"
    assert result.assessment is not None
```

## E2E Tests (10% of tests)

```python
# tests/e2e/test_complete_interview.py

@pytest.mark.e2e
async def test_candidate_completes_interview_via_api(test_client):
    # Uses FastAPI TestClient
    # 1. Register
    response = await test_client.post("/api/v1/auth/register", json={
        "email": "e2e@example.com",
        "password": "Pass123!",
        "full_name": "E2E Test"
    })
    assert response.status_code == 201
    token = response.json()["token"]
    
    # 2. Start interview
    response = await test_client.post(
        "/api/v1/interviews",
        headers={"Authorization": f"Bearer {token}"},
        json={"role_type": "react"}
    )
    interview_id = response.json()["id"]
    
    # 3. Submit answers (mocked audio)
    # ...
    
    # 4. Complete and verify results
    response = await test_client.post(f"/api/v1/interviews/{interview_id}/complete")
    assert response.status_code == 200
```

## Test Fixtures

```python
# tests/conftest.py

@pytest.fixture
async def test_db():
    """Create test database"""
    engine = create_async_engine("postgresql+asyncpg://test:test@localhost/test_db")
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield engine
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)

@pytest.fixture
def mock_openai_provider():
    """Mock OpenAI API calls"""
    provider = Mock(spec=OpenAIProvider)
    provider.generate_question.return_value = "What is React?"
    provider.transcribe_audio.return_value = TranscriptionResult(text="My answer")
    return provider
```

---
