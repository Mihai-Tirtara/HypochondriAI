from typing import Optional

from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder

from app.prompts.health_anxiety_prompt_template import HEALTH_ANXIETY_BASE_PROMPT


def generate_health_anxiety_prompt(user_context: str | None = None):
    """
    Generate a health anxiety prompt for a given set of symptoms and user context.

    Args:
        symptoms: The user's symptoms.
        user_context: Additional context provided by the user.

    Returns:
        The generated health anxiety prompt.
    """
    prompt_template = ChatPromptTemplate.from_messages(
        [
            (
                "system",
                f"""
            {HEALTH_ANXIETY_BASE_PROMPT}
    - User Context: {user_context or "No additional context provided."}
    """,
            ),
            MessagesPlaceholder(variable_name="messages"),
        ]
    )

    return prompt_template
