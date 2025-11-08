"""Integration tests for profile management API endpoints."""
from decimal import Decimal

import pytest
from httpx import AsyncClient

from app.core.security import create_access_token


@pytest.mark.asyncio
async def test_get_profile_authenticated(test_client: AsyncClient, test_candidate):
    """Test GET /api/v1/profile with valid JWT."""
    # Arrange
    token = create_access_token(test_candidate.id)
    headers = {"Authorization": f"Bearer {token}"}

    # Act
    response = await test_client.get("/api/v1/profile", headers=headers)

    # Assert
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == str(test_candidate.id)
    assert data["email"] == test_candidate.email
    assert data["full_name"] == test_candidate.full_name
    assert "profile_completeness_score" in data


@pytest.mark.asyncio
async def test_get_profile_unauthorized(test_client: AsyncClient):
    """Test GET /api/v1/profile without JWT returns 401."""
    # Act
    response = await test_client.get("/api/v1/profile")

    # Assert
    assert response.status_code == 401


@pytest.mark.asyncio
async def test_get_profile_invalid_token(test_client: AsyncClient):
    """Test GET /api/v1/profile with invalid JWT returns 401."""
    # Arrange
    headers = {"Authorization": "Bearer invalid_token"}

    # Act
    response = await test_client.get("/api/v1/profile", headers=headers)

    # Assert
    assert response.status_code == 401


@pytest.mark.asyncio
async def test_update_skills_success(test_client: AsyncClient, test_candidate):
    """Test PUT /api/v1/profile/skills with valid data."""
    # Arrange
    token = create_access_token(test_candidate.id)
    headers = {"Authorization": f"Bearer {token}"}
    payload = {
        "skills": ["React", "Python", "TypeScript", "Node.js"]
    }

    # Act
    response = await test_client.put(
        "/api/v1/profile/skills",
        headers=headers,
        json=payload
    )

    # Assert
    assert response.status_code == 200
    data = response.json()
    assert data["skills"] == ["node.js", "python", "react", "typescript"]
    assert data["profile_completeness_score"] is not None
    # Should have higher completeness with 4+ skills
    assert Decimal(str(data["profile_completeness_score"])) >= Decimal("30.00")


@pytest.mark.asyncio
async def test_update_skills_normalization(test_client: AsyncClient, test_candidate):
    """Test skills normalization (lowercase, dedupe, sort)."""
    # Arrange
    token = create_access_token(test_candidate.id)
    headers = {"Authorization": f"Bearer {token}"}
    payload = {
        "skills": ["React", "  TypeScript ", "react", "Node.js", ""]
    }

    # Act
    response = await test_client.put(
        "/api/v1/profile/skills",
        headers=headers,
        json=payload
    )

    # Assert
    assert response.status_code == 200
    data = response.json()
    # Should normalize to lowercase, dedupe, sort, and remove empty strings
    assert data["skills"] == ["node.js", "react", "typescript"]


@pytest.mark.asyncio
async def test_update_skills_unauthorized(test_client: AsyncClient):
    """Test PUT /api/v1/profile/skills without JWT returns 401."""
    # Act
    response = await test_client.put(
        "/api/v1/profile/skills",
        json={"skills": ["python"]}
    )

    # Assert
    assert response.status_code == 401


@pytest.mark.asyncio
async def test_update_skills_invalid_data(test_client: AsyncClient, test_candidate):
    """Test PUT /api/v1/profile/skills with invalid data returns 422."""
    # Arrange
    token = create_access_token(test_candidate.id)
    headers = {"Authorization": f"Bearer {token}"}
    payload = {
        "skills": "not_a_list"  # Should be a list
    }

    # Act
    response = await test_client.put(
        "/api/v1/profile/skills",
        headers=headers,
        json=payload
    )

    # Assert
    assert response.status_code == 422


@pytest.mark.asyncio
async def test_update_basic_info_success(test_client: AsyncClient, test_candidate):
    """Test PUT /api/v1/profile/basic-info with valid data."""
    # Arrange
    token = create_access_token(test_candidate.id)
    headers = {"Authorization": f"Bearer {token}"}
    payload = {
        "full_name": "Jane Smith",
        "phone": "+1234567890"
    }

    # Act
    response = await test_client.put(
        "/api/v1/profile/basic-info",
        headers=headers,
        json=payload
    )

    # Assert
    assert response.status_code == 200
    data = response.json()
    assert data["full_name"] == "Jane Smith"
    assert data["phone"] == "+1234567890"
    assert data["profile_completeness_score"] is not None


@pytest.mark.asyncio
async def test_update_basic_info_phone_only(test_client: AsyncClient, test_candidate):
    """Test PUT /api/v1/profile/basic-info updating only phone."""
    # Arrange
    token = create_access_token(test_candidate.id)
    headers = {"Authorization": f"Bearer {token}"}
    original_name = test_candidate.full_name
    payload = {"phone": "+9876543210"}

    # Act
    response = await test_client.put(
        "/api/v1/profile/basic-info",
        headers=headers,
        json=payload
    )

    # Assert
    assert response.status_code == 200
    data = response.json()
    assert data["full_name"] == original_name  # Name unchanged
    assert data["phone"] == "+9876543210"


@pytest.mark.asyncio
async def test_update_basic_info_unauthorized(test_client: AsyncClient):
    """Test PUT /api/v1/profile/basic-info without auth returns 401."""
    # Arrange
    payload = {"full_name": "Test", "phone": "123"}

    # Act
    response = await test_client.put(
        "/api/v1/profile/basic-info",
        json=payload
    )

    # Assert
    assert response.status_code == 401


@pytest.mark.asyncio
async def test_update_experience_success(test_client: AsyncClient, test_candidate):
    """Test PUT /api/v1/profile/experience with valid years."""
    # Arrange
    token = create_access_token(test_candidate.id)
    headers = {"Authorization": f"Bearer {token}"}
    payload = {"experience_years": 5}

    # Act
    response = await test_client.put(
        "/api/v1/profile/experience",
        headers=headers,
        json=payload
    )

    # Assert
    assert response.status_code == 200
    data = response.json()
    assert data["experience_years"] == 5
    assert data["profile_completeness_score"] is not None
    # Should have higher completeness with experience
    assert Decimal(str(data["profile_completeness_score"])) >= Decimal("20.00")


@pytest.mark.asyncio
async def test_update_experience_invalid_range(test_client: AsyncClient, test_candidate):
    """Test PUT /api/v1/profile/experience with years > 50 returns 422."""
    # Arrange
    token = create_access_token(test_candidate.id)
    headers = {"Authorization": f"Bearer {token}"}
    payload = {"experience_years": 51}  # Exceeds max

    # Act
    response = await test_client.put(
        "/api/v1/profile/experience",
        headers=headers,
        json=payload
    )

    # Assert
    assert response.status_code == 422


@pytest.mark.asyncio
async def test_update_experience_negative_value(test_client: AsyncClient, test_candidate):
    """Test PUT /api/v1/profile/experience with negative years returns 422."""
    # Arrange
    token = create_access_token(test_candidate.id)
    headers = {"Authorization": f"Bearer {token}"}
    payload = {"experience_years": -1}

    # Act
    response = await test_client.put(
        "/api/v1/profile/experience",
        headers=headers,
        json=payload
    )

    # Assert
    assert response.status_code == 422


@pytest.mark.asyncio
async def test_update_preferences_success(test_client: AsyncClient, test_candidate):
    """Test PUT /api/v1/profile/preferences with valid JSON."""
    # Arrange
    token = create_access_token(test_candidate.id)
    headers = {"Authorization": f"Bearer {token}"}
    payload = {
        "job_preferences": {
            "locations": ["Remote Australia", "Sydney"],
            "employment_types": ["permanent", "contract"],
            "work_setups": ["remote", "hybrid"],
            "salary_min": 120000,
            "salary_max": 150000,
            "role_categories": ["engineering", "quality_assurance"]
        }
    }

    # Act
    response = await test_client.put(
        "/api/v1/profile/preferences",
        headers=headers,
        json=payload
    )

    # Assert
    assert response.status_code == 200
    data = response.json()
    assert data["job_preferences"] is not None
    assert data["job_preferences"]["locations"] == ["Remote Australia", "Sydney"]
    assert data["job_preferences"]["salary_min"] == 120000
    assert data["job_preferences"]["salary_max"] == 150000
    assert data["profile_completeness_score"] is not None


@pytest.mark.asyncio
async def test_update_preferences_invalid_salary_range(test_client: AsyncClient, test_candidate):
    """Test PUT /api/v1/profile/preferences with salary_max < salary_min returns 422."""
    # Arrange
    token = create_access_token(test_candidate.id)
    headers = {"Authorization": f"Bearer {token}"}
    payload = {
        "job_preferences": {
            "locations": ["Remote"],
            "salary_min": 150000,
            "salary_max": 120000  # Max < Min
        }
    }

    # Act
    response = await test_client.put(
        "/api/v1/profile/preferences",
        headers=headers,
        json=payload
    )

    # Assert
    assert response.status_code == 422


@pytest.mark.asyncio
async def test_profile_completeness_updates(test_client: AsyncClient, test_candidate):
    """Test that profile completeness score updates after each change."""
    # Arrange
    token = create_access_token(test_candidate.id)
    headers = {"Authorization": f"Bearer {token}"}

    # Act 1: Get initial profile
    response1 = await test_client.get("/api/v1/profile", headers=headers)
    initial_score = Decimal(str(response1.json()["profile_completeness_score"] or "0"))

    # Act 2: Add skills
    await test_client.put(
        "/api/v1/profile/skills",
        headers=headers,
        json={"skills": ["python", "react", "typescript", "node.js"]}
    )
    response2 = await test_client.get("/api/v1/profile", headers=headers)
    score_after_skills = Decimal(str(response2.json()["profile_completeness_score"]))

    # Act 3: Add experience
    await test_client.put(
        "/api/v1/profile/experience",
        headers=headers,
        json={"experience_years": 5}
    )
    response3 = await test_client.get("/api/v1/profile", headers=headers)
    score_after_experience = Decimal(str(response3.json()["profile_completeness_score"]))

    # Assert: Score should increase with each addition
    assert score_after_skills > initial_score
    assert score_after_experience > score_after_skills


@pytest.mark.asyncio
async def test_auth_me_endpoint_still_works(test_client: AsyncClient, test_candidate):
    """Test that existing /api/v1/auth/me endpoint continues to work (no regression)."""
    # Arrange
    token = create_access_token(test_candidate.id)
    headers = {"Authorization": f"Bearer {token}"}

    # Act
    response = await test_client.get("/api/v1/auth/me", headers=headers)

    # Assert
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == str(test_candidate.id)
    assert data["email"] == test_candidate.email


@pytest.mark.asyncio
async def test_update_skills_then_get_profile(test_client: AsyncClient, test_candidate):
    """Test that updated skills are persisted and returned in GET profile."""
    # Arrange
    token = create_access_token(test_candidate.id)
    headers = {"Authorization": f"Bearer {token}"}
    skills = ["python", "react", "typescript", "aws"]

    # Act: Update skills
    update_response = await test_client.put(
        "/api/v1/profile/skills",
        headers=headers,
        json={"skills": skills}
    )

    # Get profile
    get_response = await test_client.get("/api/v1/profile", headers=headers)

    # Assert
    assert update_response.status_code == 200
    assert get_response.status_code == 200
    assert get_response.json()["skills"] == ["aws", "python", "react", "typescript"]


@pytest.mark.asyncio
async def test_empty_skills_list(test_client: AsyncClient, test_candidate):
    """Test updating skills with empty list."""
    # Arrange
    token = create_access_token(test_candidate.id)
    headers = {"Authorization": f"Bearer {token}"}

    # Act
    response = await test_client.put(
        "/api/v1/profile/skills",
        headers=headers,
        json={"skills": []}
    )

    # Assert
    assert response.status_code == 200
    data = response.json()
    assert data["skills"] == []


@pytest.mark.asyncio
async def test_partial_preferences_update(test_client: AsyncClient, test_candidate):
    """Test updating only some preference fields."""
    # Arrange
    token = create_access_token(test_candidate.id)
    headers = {"Authorization": f"Bearer {token}"}
    payload = {
        "job_preferences": {
            "locations": ["Remote"],
            "employment_types": ["permanent"]
            # Intentionally omit other fields
        }
    }

    # Act
    response = await test_client.put(
        "/api/v1/profile/preferences",
        headers=headers,
        json=payload
    )

    # Assert
    assert response.status_code == 200
    data = response.json()
    assert data["job_preferences"]["locations"] == ["Remote"]
    assert data["job_preferences"]["employment_types"] == ["permanent"]
    # Should have some completeness points for partial preferences
    assert Decimal(str(data["profile_completeness_score"])) > Decimal("20.00")
