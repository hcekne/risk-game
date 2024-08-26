import os
import time
from groq import Groq, InternalServerError, APIStatusError
from risk_game.llm_clients.llm_base import LLMClient
import json  # Import json to handle response decoding

class GroqClient(LLMClient):

    def __init__(self, model_number: int):
        self.client = Groq(api_key=os.environ.get("GROQ_API_KEY"))
        if model_number == 1:
            model_type = "llama-3.1-70b-versatile"
        elif model_number == 2:
            model_type = "llama3-70b-8192"
        elif model_number == 3:
            model_type = "llama-3.1-8b-instant"
        elif model_number == 4:
            model_type = "mixtral-8x7b-32768"
        else:
            raise ValueError("Invalid model number. Please choose a number " +
                             "between 1 and 4.")

        # Call the parent class constructor to set provider and model_type
        super().__init__(provider_name="Groq", model_type=model_type)

    def get_chat_completion(self, message_content: str) -> str:
        full_prompt = [
            {"role": "system", 
            "content": "You are a master strategist and Risk player with 20 years experience."},
            {
                "role": "user",
                "content": message_content
            }]

        for attempt in range(self.max_retries):
            try:
                response = self.client.chat.completions.create(
                    model=self.model_type,
                    messages=full_prompt,
                    max_tokens=2000,
                    temperature=1)
                return response.choices[0].message.content

            except APIStatusError as e:
                # Handle API status error, particularly rate limit errors (429)
                if e.status_code == 429:  # Too Many Requests error
                    try:
                        # Convert the response to JSON
                        error_data = e.response.json()
                        
                        # Extract the error details
                        error_message = error_data['error']['message']
                        error_type = error_data['error']['type']
                        print(f"Rate Limit Error: {error_message} (Type: {error_type})")
                        
                        # Extract Retry-After or fallback to retry_delay
                        retry_after = error_data.get('retry_after', 
                                                     self.retry_delay)
                    except json.JSONDecodeError:
                        # Fallback to the default delay if JSON decoding fails
                        retry_after = self.retry_delay
                        print("Failed to decode JSON response, using default retry delay.")
                    
                    print(f"Rate limit reached, retrying in {retry_after} seconds...")
                    time.sleep(float(retry_after))

                else:
                    print(f"Attempt {attempt + 1} failed with error: {e}. " +
                          f"Retrying in {self.retry_delay} seconds...")
                    time.sleep(self.retry_delay)

            except InternalServerError as e:
                # Handle InternalServerError generically
                print(f"Internal Server Error (503): {e}. Retrying in {self.retry_delay} seconds...")
                time.sleep(self.retry_delay)

            except Exception as e:
                # Generic exception handling for other errors
                print(f"Unexpected error: {e}")
                break

        # If we exhausted all retries, raise an error
        raise InternalServerError(("Maximum retries reached. Service is " +
                                   "still unavailable."), response=None, body=None)
