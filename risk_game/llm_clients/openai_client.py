import os
from openai import OpenAI, InternalServerError
from risk_game.llm_clients.llm_base import LLMClient
import time

class OpenAIClient(LLMClient):
    def __init__(self, model_number: int):
        # os.environ.get("OPENAI_API_KEY")
        self.client = OpenAI()
        
        if model_number == 1:
            self.model_type = "gpt-4o"
        elif model_number == 2:
            self.model_type = "gpt-3.5-turbo-0125"
        else:
            raise ValueError("Invalid model number. Please choose a number " +
                             "between 1 and 2.")
    
    def get_chat_completion(self, message_content) -> str:
        max_retries = 3  # Maximum number of retry attempts
        retry_delay = 5   # Delay in seconds between retries
        messages = [
        {"role": "system", 
         "content": "You are a master strategist and Risk player with 20 years experience."},
        {
            "role": "user",
            "content": message_content
        }
    ]

        for attempt in range(max_retries):
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
                      f"Retrying in {retry_delay} seconds...")
                time.sleep(retry_delay)
            except Exception as e:
                print(f"Unexpected error: {e}")
                break

        raise InternalServerError("Maximum retries reached. Service is still unavailable.")


