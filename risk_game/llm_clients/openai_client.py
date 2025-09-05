import os
from openai import OpenAI, InternalServerError
from risk_game.llm_clients.llm_base import LLMClient
import time

class OpenAIClient(LLMClient):
    def __init__(self, model_number: int, use_responses_api: bool = True, 
        reasoning_effort: str = "minimal", verbosity: str = "low"):
        """Initialize OpenAI LLM client with specified model and options."""

        self.client = OpenAI()
        self.use_responses_api = use_responses_api
        self.reasoning_effort = reasoning_effort
        self.verbosity = verbosity
        
        # Model configuration with reasoning capability info
        model_configs = {
            1: {"name": "gpt-5", "supports_reasoning": True, "supports_verbosity": True},
            2: {"name": "gpt-5-mini", "supports_reasoning": True, "supports_verbosity": True},
            3: {"name": "gpt-5-nano", "supports_reasoning": True, "supports_verbosity": True},
            4: {"name": "gpt-4.1", "supports_reasoning": False, "supports_verbosity": False},
            5: {"name": "gpt-5-chat-latest", "supports_reasoning": False, "supports_verbosity": False}
        }

        if model_number not in model_configs:
            raise ValueError(f"Invalid model number. Please choose from {list(model_configs.keys())}")
        
        config = model_configs[model_number]
        self.model_type = config["name"]
        self.supports_reasoning = config["supports_reasoning"]
        self.supports_verbosity = config["supports_verbosity"]

        # Call the parent class constructor
        super().__init__(provider_name="OpenAI", model_type=self.model_type)
    
    def get_chat_completion(self, message_content) -> str:
        if self.use_responses_api:
            return self._get_response_completion(message_content)
        else:
            return self._get_chat_completion_legacy(message_content)
    
    def _get_response_completion(self, message_content) -> str:
        """Use the new Responses API for better performance and lower costs"""
        for attempt in range(self.max_retries):
            try:
                # Build request parameters
                params = {
                    "model": self.model_type,
                    "input": message_content,
                    "instructions": "You are a master strategist and Risk player with 20 years experience."
                }
                
                # Only add reasoning parameter for models that support it
                if self.supports_reasoning:
                    params["reasoning"] = {"effort": self.reasoning_effort}
                # Only add verbosity parameter for models that support it
                if self.supports_verbosity:
                    params["text"] = {"verbosity": self.verbosity}

                response = self.client.responses.create(**params)
                return response.output_text
                
            except InternalServerError as e:
                print(f"Attempt {attempt + 1} failed with API error: {e}. " +
                      f"Retrying in {self.retry_delay} seconds...")
                time.sleep(self.retry_delay)
            except Exception as e:
                print(f"Unexpected error: {e}")
                break

        raise InternalServerError("Maximum retries reached. Service is still unavailable.")
    
    def _get_chat_completion_legacy(self, message_content) -> str:
        """Legacy Chat Completions API - kept for backward compatibility"""
        messages = [
            {"role": "system", 
             "content": "You are a master strategist and Risk player with 20 years experience."},
            {
                "role": "user",
                "content": message_content
            }
        ]

        for attempt in range(self.max_retries):
            try:
                response = self.client.chat.completions.create(
                    model=self.model_type,
                    messages=messages,
                    temperature=0
                )
                return response.choices[0].message.content
            except InternalServerError as e:
                print(f"Attempt {attempt + 1} failed with API error: {e}. " +
                      f"Retrying in {self.retry_delay} seconds...")
                time.sleep(self.retry_delay)
            except Exception as e:
                print(f"Unexpected error: {e}")
                break

        raise InternalServerError("Maximum retries reached. Service is still unavailable.")


