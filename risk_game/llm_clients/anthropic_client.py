import os
from anthropic import Client, AnthropicError
from risk_game.llm_clients.llm_base import LLMClient 
import time


class AnthropicClient(LLMClient):
    def __init__(self, model_number: int, enable_thinking: bool = False, thinking_budget: int = 2000):
        self.client = Client(api_key=os.environ.get("ANTHROPIC_API_KEY"))
        self.enable_thinking = enable_thinking
        self.thinking_budget = thinking_budget
        
        # Model configuration with thinking capability info
        model_configs = {
            1: {"name": "claude-opus-4-1", "supports_thinking": True},
            2: {"name": "claude-sonnet-4-0", "supports_thinking": True}, 
            3: {"name": "claude-3-7-sonnet-latest", "supports_thinking": True},
            4: {"name": "claude-3-5-sonnet-latest", "supports_thinking": False}
        }
        
        if model_number not in model_configs:
            raise ValueError(f"Invalid model number. Please choose from {list(model_configs.keys())}")
        
        config = model_configs[model_number]
        self.model_type = config["name"]
        self.supports_thinking = config["supports_thinking"]

        # Call the parent class constructor to set provider and model_type
        super().__init__(provider_name="Anthropic", model_type=self.model_type)

    def get_chat_completion(self, message_content) -> str:
        full_prompt = [
            {
                "role": "user",
                "content": message_content
            }
        ]

        for attempt in range(self.max_retries):
            try:
                # Build request parameters
                params = {
                    "model": self.model_type,
                    "system": "You are a master strategist and Risk player with 20 years experience.",
                    "max_tokens": 4000,
                    "messages": full_prompt
                }
                
                # Only add thinking parameter for models that support it
                if self.enable_thinking and self.supports_thinking:
                    params["thinking"] = {
                        "type": "enabled",
                        "budget_tokens": self.thinking_budget
                    }

                    params["temperature"] = 1  # Required when thinking is enabled
                else:
                    params["temperature"] = 0  # Default for non-thinking mode    

                message = self.client.messages.create(**params)
                
                # Extract response text, handling both thinking and non-thinking responses
                response_text = ""
                for block in message.content:
                    if block.type == "text":
                        response_text += block.text
                    elif block.type == "thinking" and self.enable_thinking:
                        # Optionally include thinking summary in response for debugging
                        # Uncomment the next line if you want to see thinking in responses
                        # response_text += f"\n[Thinking: {block.thinking}]\n"
                        pass
                
                return response_text
                
            except AnthropicError as e:
                print(f"Attempt {attempt + 1} failed with error: {e}. " +
                      f"Retrying in {self.retry_delay} seconds...")
                time.sleep(self.retry_delay)
            except Exception as e:
                print(f"Unexpected error: {e}")
                break

        raise AnthropicError("Maximum retries reached. Service is still unavailable.")