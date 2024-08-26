import os
from openai import OpenAI, InternalServerError
from risk_game.llm_clients.llm_base import LLMClient
import time

class OpenAIClient(LLMClient):
    def __init__(self, model_number: int):
        # os.environ.get("OPENAI_API_KEY")
        self.client = OpenAI()
        
        if model_number == 1:
            model_type = "gpt-4o"
        elif model_number == 2:
            model_type = "gpt-4o-mini"
        elif model_number == 3:
            model_type = "gpt-3.5-turbo-0125"
        
        else:
            raise ValueError("Invalid model number. Please choose a number " +
                             "between 1 and 2.")
        # Call the parent class constructor to set provider and model_type
        super().__init__(provider_name="OpenAI", model_type=model_type)
    
    def get_chat_completion(self, message_content) -> str:
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
                    max_tokens=1000,
                    temperature=0,
                )
                return response.choices[0].message.content
            except InternalServerError as e:
                print(f"Attempt {attempt + 1} failed with API error: {e}." +
                      f"Retrying in {self.retry_delay} seconds...")
                time.sleep(self.retry_delay)
            except Exception as e:
                print(f"Unexpected error: {e}")
                break

        raise InternalServerError("Maximum retries reached. Service is still unavailable.")


