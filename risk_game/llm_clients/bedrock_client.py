import boto3
from risk_game.llm_clients.llm_base import LLMClient 
import time
import json

class BedrockClient(LLMClient):
    def __init__(self, model_number: int):
        self.client = boto3.client('bedrock-runtime', region_name='us-west-2')
        if model_number == 1:
            self.model_type = "meta.llama3-1-405b-instruct-v1:0"
        else:
            raise ValueError("Invalid model number. Please choose a number " +
                             "between 1 and 1.")
    
    def get_chat_completion(self, message_content: str) -> str:
        max_retries = 3  # Maximum number of retry attempts
        retry_delay = 5   # Delay in seconds between retries

        full_prompt = {
            "prompt": message_content,
            "max_gen_len": 2000,
            "temperature": 0,
            "top_p": 1
        }

        for attempt in range(max_retries):
            try:
                response = self.client.invoke_model(
                    contentType="application/json", 
                    body=json.dumps(full_prompt),
                    modelId=self.model_type
                )
                response_body = response["body"].read().decode("utf-8")
                generated_text = json.loads(response_body).get('generation', '')
                cleaned_text = generated_text.replace('\n', ' ')
                return cleaned_text
            except Exception as e:
                print(f"Attempt {attempt + 1} failed with error: {e}." +
                f"Retrying in {retry_delay} seconds...")
                time.sleep(retry_delay)

        raise Exception("Maximum retries reached. Service is still unavailable.")