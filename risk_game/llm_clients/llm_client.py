from .groq_client import GroqClient
from .anthropic_client import AnthropicClient
from .openai_client import OpenAIClient
from .bedrock_client import BedrockClient



# Factory Method
def create_llm_client(provider: str, model_number: int) -> 'LLMClient':
    if provider == "Groq":
        return GroqClient(model_number)
    elif provider == "Anthropic":
        return AnthropicClient(model_number)
    elif provider == "OpenAI":
        return OpenAIClient(model_number)
    elif provider == "Bedrock":
        return BedrockClient(model_number)
    else:
        raise ValueError(f"Unknown LLM provider: {provider}")
