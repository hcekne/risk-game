from typing import Optional, Union

from .anthropic_client import AnthropicClient
from .bedrock_client import BedrockClient
from .gemini_client import GeminiClient
from .groq_client import GroqClient
from .moonshot_client import MoonshotClient
from .openai_client import OpenAIClient


def create_llm_client(
    provider: str,
    model_number: Optional[Union[int, str]] = None,
    *,
    model_name: Optional[str] = None,
    use_responses_api: bool = True,
    reasoning_effort: Optional[str] = "none",
    verbosity: str = "low",
    enable_thinking: bool = False,
    thinking_budget: int = 2000,
    thinking_effort: Optional[str] = None,
) -> "LLMClient":
    """Factory method to create LLM client instances."""
    if provider == "Groq":
        return GroqClient(model_number)
    if provider == "Anthropic":
        resolved_model_name = model_name
        resolved_model_number = model_number

        if isinstance(model_number, str) and model_name is None:
            resolved_model_name = model_number
            resolved_model_number = None

        return AnthropicClient(
            resolved_model_number,
            model_name=resolved_model_name,
            enable_thinking=enable_thinking,
            thinking_budget=thinking_budget,
            thinking_effort=thinking_effort,
        )
    if provider == "OpenAI":
        resolved_model_name = model_name
        resolved_model_number = model_number

        if isinstance(model_number, str) and model_name is None:
            resolved_model_name = model_number
            resolved_model_number = None

        return OpenAIClient(
            model_number=resolved_model_number,
            model_name=resolved_model_name,
            use_responses_api=use_responses_api,
            reasoning_effort=reasoning_effort,
            verbosity=verbosity,
        )
    if provider == "Gemini":
        resolved_model_name = model_name
        resolved_model_number = model_number

        if isinstance(model_number, str) and model_name is None:
            resolved_model_name = model_number
            resolved_model_number = None

        return GeminiClient(
            model_number=resolved_model_number,
            model_name=resolved_model_name,
            reasoning_effort=reasoning_effort,
            thinking_budget=thinking_budget,
            include_thoughts=enable_thinking,
        )
    if provider in ("Moonshot", "Kimi"):
        resolved_model_name = model_name
        resolved_model_number = model_number

        if isinstance(model_number, str) and model_name is None:
            resolved_model_name = model_number
            resolved_model_number = None

        return MoonshotClient(
            model_number=resolved_model_number,
            model_name=resolved_model_name,
            enable_thinking=enable_thinking,
        )
    if provider == "Bedrock":
        return BedrockClient(model_number)

    raise ValueError(f"Unknown LLM provider: {provider}")
