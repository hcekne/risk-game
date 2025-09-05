from .groq_client import GroqClient
from .anthropic_client import AnthropicClient
from .openai_client import OpenAIClient
from .bedrock_client import BedrockClient

# Factory Method
def create_llm_client(provider: str, model_number: int, 
                     use_responses_api: bool = True, 
                     reasoning_effort: str = "minimal",
                     enable_thinking: bool = False,
                     thinking_budget: int = 2000) -> 'LLMClient':
    """Factory method to create LLM client instances based on provider and model number"""
    if provider == "Groq":
        return GroqClient(model_number)
    elif provider == "Anthropic":
        return AnthropicClient(model_number, enable_thinking=enable_thinking, 
                             thinking_budget=thinking_budget)
    elif provider == "OpenAI":
        return OpenAIClient(model_number, use_responses_api=use_responses_api, 
                          reasoning_effort=reasoning_effort)
    elif provider == "Bedrock":
        return BedrockClient(model_number)
    else:
        raise ValueError(f"Unknown LLM provider: {provider}")
