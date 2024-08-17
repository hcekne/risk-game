import os
import time
from groq import Groq, InternalServerError
from risk_game.llm_clients.llm_base import LLMClient 


class GroqClient(LLMClient):

    def __init__(self, model_number: int):
        self.client = Groq(api_key=os.environ.get("GROQ_API_KEY"))
        if  model_number == 1:
            self.model_type="llama-3.1-70b-versatile"
        elif model_number == 2:
            self.model_type="llama3-70b-8192"
        elif model_number == 3:
            self.model_type="llama-3.1-8b-instant"
        elif model_number == 4:
            self.model_type="mixtral-8x7b-32768"
        else:
            raise ValueError("Invalid model number. Please choose a number " +
                             "between 1 and 4.")

    def get_chat_completion(self, message_content: str) -> str:
        full_prompt = [
        {"role": "system", 
        "content": "You are a master strategist and Risk player with 20 years experience."},
        {
            "role": "user",
            "content": message_content
        }]
        max_retries = 3  # Maximum number of retry attempts
        retry_delay = 5   # Delay in seconds between retries

        for attempt in range(max_retries):
            try:
                response = self.client.chat.completions.create(
                    model=self.model_type,
                    messages=full_prompt,
                    max_tokens=2000,
                    temperature=1.2)
                return response.choices[0].message.content
            except InternalServerError as e:
                print(f"Attempt {attempt + 1} failed with error: {e}." +
                f"Retrying in {retry_delay} seconds...")
                time.sleep(retry_delay)
            except Exception as e:
                print(f"Unexpected error: {e}")
                break

        raise InternalServerError("Maximum retries reached. Service is still unavailable.")