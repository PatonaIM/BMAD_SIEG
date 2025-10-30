"""Prompt template loading and management."""

from pathlib import Path

import structlog

logger = structlog.get_logger()

# Path to prompts directory
PROMPTS_DIR = Path(__file__).parent.parent / "prompts"


class PromptTemplateManager:
    """
    Manages loading and combining prompt templates for AI interviews.

    Prompt files are stored in backend/app/prompts/ as .txt files:
    - interview_system.txt: Base system prompt for all interviews
    - react_interview.txt: React-specific context
    - python_interview.txt: Python-specific context
    - javascript_interview.txt: JavaScript-specific context

    Templates are version-controlled and can be updated without code changes.
    Each template file includes a version header for tracking.

    Usage:
        manager = PromptTemplateManager()

        # Load full interview prompt for React role
        prompt = manager.get_interview_prompt(role_type="react")

        # Load specific template
        system_prompt = manager.load_template("interview_system")
    """

    def __init__(self, prompts_dir: Path | None = None):
        """
        Initialize prompt template manager.

        Args:
            prompts_dir: Optional custom path to prompts directory
        """
        self.prompts_dir = prompts_dir or PROMPTS_DIR

        if not self.prompts_dir.exists():
            logger.error(
                "prompts_directory_not_found",
                path=str(self.prompts_dir),
            )
            raise FileNotFoundError(f"Prompts directory not found: {self.prompts_dir}")

        logger.info(
            "prompt_manager_initialized",
            prompts_dir=str(self.prompts_dir),
        )

    def load_template(self, template_name: str) -> str:
        """
        Load a prompt template by name.

        Args:
            template_name: Name of template file without .txt extension
                          (e.g., "interview_system", "react_interview")

        Returns:
            str: Template content

        Raises:
            FileNotFoundError: If template file doesn't exist
        """
        template_path = self.prompts_dir / f"{template_name}.txt"

        if not template_path.exists():
            logger.error(
                "template_not_found",
                template_name=template_name,
                path=str(template_path),
            )
            raise FileNotFoundError(
                f"Template '{template_name}' not found at {template_path}"
            )

        try:
            with open(template_path, encoding="utf-8") as f:
                content = f.read()

            logger.debug(
                "template_loaded",
                template_name=template_name,
                content_length=len(content),
            )

            return content

        except Exception as e:
            logger.error(
                "template_load_failed",
                template_name=template_name,
                error=str(e),
            )
            raise

    def get_interview_prompt(self, role_type: str) -> str:
        """
        Get complete interview prompt combining system and role-specific prompts.

        Combines:
        1. Base system prompt (interview_system.txt)
        2. Role-specific prompt (e.g., react_interview.txt)

        Args:
            role_type: Role type identifier ("react", "python", "javascript", "fullstack")

        Returns:
            str: Combined prompt ready for AI model

        Raises:
            FileNotFoundError: If required templates don't exist
            ValueError: If role_type is not supported
        """
        # Validate role type
        supported_roles = ["react", "python", "javascript", "fullstack"]
        if role_type not in supported_roles:
            logger.error(
                "unsupported_role_type",
                role_type=role_type,
                supported_roles=supported_roles,
            )
            raise ValueError(
                f"Unsupported role type: {role_type}. "
                f"Supported: {', '.join(supported_roles)}"
            )

        # Load system prompt
        system_prompt = self.load_template("interview_system")

        # For fullstack, default to JavaScript for now
        # (could be enhanced to combine multiple role prompts)
        if role_type == "fullstack":
            role_type = "javascript"

        # Load role-specific prompt
        role_prompt = self.load_template(f"{role_type}_interview")

        # Combine prompts with clear separator
        combined_prompt = f"{system_prompt}\n\n---\n\n{role_prompt}"

        logger.info(
            "interview_prompt_generated",
            role_type=role_type,
            total_length=len(combined_prompt),
        )

        return combined_prompt

    def list_available_templates(self) -> list[str]:
        """
        List all available template names.

        Returns:
            List of template names (without .txt extension)
        """
        templates = []
        for file_path in self.prompts_dir.glob("*.txt"):
            templates.append(file_path.stem)

        logger.debug(
            "templates_listed",
            count=len(templates),
            templates=templates,
        )

        return sorted(templates)
