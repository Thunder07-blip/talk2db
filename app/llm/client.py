"""Groq LLM client for Talk2DB SQL generation."""

from groq import Groq
from app.config import GROQ_API_KEY, GROQ_MODEL, GROQ_MAX_TOKENS, GROQ_TEMPERATURE


def _get_client() -> Groq:
    """Create a Groq client using the configured API key."""
    if not GROQ_API_KEY:
        raise RuntimeError(
            "GROQ_API_KEY is not set. Add groq_api_1=<key> to your .env file."
        )
    return Groq(api_key=GROQ_API_KEY)


def generate_sql(system_prompt: str, user_prompt: str) -> str:
    """Send a chat completion request to Groq and return the raw response text.

    Args:
        system_prompt: The system message defining the LLM's role.
        user_prompt: The user message with schema context and question.

    Returns:
        The LLM's response text (expected to be a SQL query).

    Raises:
        RuntimeError: If the API key is missing.
        groq.APIError: On API-level failures.
    """
    client = _get_client()

    response = client.chat.completions.create(
        model=GROQ_MODEL,
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ],
        max_tokens=GROQ_MAX_TOKENS,
        temperature=GROQ_TEMPERATURE,
    )

    return response.choices[0].message.content.strip()
