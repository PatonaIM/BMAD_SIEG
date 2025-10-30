"""Unit tests for prompt template loader."""


import pytest

from app.utils.prompt_loader import PromptTemplateManager


def test_init_prompt_manager():
    """Test initializing prompt template manager."""
    manager = PromptTemplateManager()
    assert manager.prompts_dir.exists()


def test_load_template_success():
    """Test loading existing template."""
    manager = PromptTemplateManager()

    content = manager.load_template("interview_system")

    assert isinstance(content, str)
    assert len(content) > 0
    assert "interviewer" in content.lower() or "interview" in content.lower()


def test_load_template_not_found():
    """Test loading non-existent template."""
    manager = PromptTemplateManager()

    with pytest.raises(FileNotFoundError):
        manager.load_template("nonexistent_template")


def test_get_interview_prompt_react():
    """Test getting React interview prompt."""
    manager = PromptTemplateManager()

    prompt = manager.get_interview_prompt("react")

    assert isinstance(prompt, str)
    assert len(prompt) > 0
    # Should contain both system and role-specific content
    assert "interview" in prompt.lower()
    assert "react" in prompt.lower()


def test_get_interview_prompt_python():
    """Test getting Python interview prompt."""
    manager = PromptTemplateManager()

    prompt = manager.get_interview_prompt("python")

    assert isinstance(prompt, str)
    assert "python" in prompt.lower()


def test_get_interview_prompt_javascript():
    """Test getting JavaScript interview prompt."""
    manager = PromptTemplateManager()

    prompt = manager.get_interview_prompt("javascript")

    assert isinstance(prompt, str)
    assert "javascript" in prompt.lower()


def test_get_interview_prompt_fullstack():
    """Test getting fullstack interview prompt (defaults to JavaScript)."""
    manager = PromptTemplateManager()

    prompt = manager.get_interview_prompt("fullstack")

    assert isinstance(prompt, str)
    assert len(prompt) > 0


def test_get_interview_prompt_unsupported():
    """Test unsupported role type."""
    manager = PromptTemplateManager()

    with pytest.raises(ValueError):
        manager.get_interview_prompt("unsupported_role")


def test_list_available_templates():
    """Test listing available templates."""
    manager = PromptTemplateManager()

    templates = manager.list_available_templates()

    assert isinstance(templates, list)
    assert len(templates) > 0
    assert "interview_system" in templates
    assert "react_interview" in templates
    assert "python_interview" in templates
    assert "javascript_interview" in templates
