import os
from anthropic import Client, AnthropicError
from risk_game.llm_clients.llm_base import LLMClient 
import time


class AnthropicClient(LLMClient):
    def __init__(self, model_number: int):
        self.client = Client(api_key=os.environ.get("ANTHROPIC_API_KEY"))
        if model_number == 1:
            model_type = "claude-3-5-sonnet-20240620"
        elif model_number == 2:
            model_type = "claude-3-sonnet-20240229"
        elif model_number == 3:
            model_type = "claude-3-haiku-20240307"
        else:
            raise ValueError("Invalid model number. Please choose a number " +
                             "between 1 and 3.")

        # Call the parent class constructor to set provider and model_type
        super().__init__(provider_name="Anthropic", model_type=model_type)


    def get_chat_completion(self, message_content) -> str:
        full_prompt = [
        {
            "role": "user",
            "content": message_content
        }]

        for attempt in range(self.max_retries):
            try:
                message= self.client.messages.create(
                    model=self.model_type,
                    system=(f"You are a master strategist and Risk player " +
                    f"with 20 years experience."),
                    max_tokens=2000,
                    temperature=0,
                    messages=full_prompt
                    )
                return message.content[0].text
            except (AnthropicError) as e:
                print(f"Attempt {attempt + 1} failed with error: {e}." +
                f"Retrying in {self.retry_delay} seconds...")
                time.sleep(self.retry_delay)
            except Exception as e:
                print(f"Unexpected error: {e}")
                break

        raise AnthropicError("Maximum retries reached. Service is still unavailable.")