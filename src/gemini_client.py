"""Gemini client with Google Search grounding for live research."""

from typing import Type, TypeVar
from google import genai
from google.genai import types
from pydantic import BaseModel
from src.config import GOOGLE_API_KEY, GEMINI_MODEL

T = TypeVar("T", bound=BaseModel)


def get_client():
    """Get configured Gemini client."""
    return genai.Client(api_key=GOOGLE_API_KEY)


def generate_with_grounding(prompt: str, use_search: bool = True) -> str:
    """
    Generate content using Gemini with optional Google Search grounding.

    Args:
        prompt: The prompt to send to Gemini
        use_search: Whether to enable Google Search grounding for live info

    Returns:
        Generated text response
    """
    client = get_client()

    # Add instruction to output content directly without preamble
    enhanced_prompt = f"""{prompt}

IMPORTANT: Output ONLY the requested content. Do not include any preamble,
acknowledgment, or meta-commentary like "I will write..." or "Here is...".
Start directly with the content itself."""

    if use_search:
        # Enable Google Search grounding for live web results
        response = client.models.generate_content(
            model=GEMINI_MODEL,
            contents=enhanced_prompt,
            config=types.GenerateContentConfig(
                tools=[types.Tool(google_search=types.GoogleSearch())],
                temperature=0.7,
            )
        )
    else:
        # Standard generation without search
        response = client.models.generate_content(
            model=GEMINI_MODEL,
            contents=enhanced_prompt,
            config=types.GenerateContentConfig(
                temperature=0.7,
            )
        )

    return response.text


def generate_structured_output(
    prompt: str,
    response_schema: Type[T],
    use_search: bool = False,
    temperature: float = 0.7,
) -> T:
    """
    Generate content with structured output using a Pydantic model.

    Args:
        prompt: The prompt to send
        response_schema: Pydantic model class defining the output structure
        use_search: Whether to enable Google Search grounding
        temperature: Creativity level (0-1)

    Returns:
        Parsed Pydantic model instance
    """
    client = get_client()

    tools = []
    if use_search:
        tools.append(types.Tool(google_search=types.GoogleSearch()))

    response = client.models.generate_content(
        model=GEMINI_MODEL,
        contents=prompt,
        config=types.GenerateContentConfig(
            temperature=temperature,
            response_mime_type="application/json",
            response_schema=response_schema,
            tools=tools if tools else None,
        )
    )

    # Parse the JSON response into the Pydantic model
    import json
    data = json.loads(response.text)
    return response_schema.model_validate(data)


def generate_structured(prompt: str, temperature: float = 0.7) -> str:
    """
    Generate content without search grounding (for style guide, stitching, etc.)

    Args:
        prompt: The prompt to send
        temperature: Creativity level (0-1)

    Returns:
        Generated text response
    """
    client = get_client()

    # Add instruction to output content directly without preamble
    enhanced_prompt = f"""{prompt}

IMPORTANT: Output ONLY the requested content. Do not include any preamble,
acknowledgment, or meta-commentary like "I will write..." or "Here is...".
Start directly with the content itself."""

    response = client.models.generate_content(
        model=GEMINI_MODEL,
        contents=enhanced_prompt,
        config=types.GenerateContentConfig(
            temperature=temperature,
        )
    )

    return response.text
