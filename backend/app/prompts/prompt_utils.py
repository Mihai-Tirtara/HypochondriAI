from typing import Optional
from prompts.health_anxiety_prompt_template import HEALTH_ANXIETY_BASE_PROMPT
def generate_health_anxiety_prompt(symptoms: str, user_context: Optional[str] = None) -> str:
    """
    Generate a health anxiety prompt for a given set of symptoms and user context.

    Args:
        symptoms: The user's symptoms.
        user_context: Additional context provided by the user.

    Returns:
        The generated health anxiety prompt.
    """
    return f"""
    {HEALTH_ANXIETY_BASE_PROMPT}

    ## User Information
    - Symptoms: {symptoms}
    - User Context: {user_context or "No additional context provided."}
    """
