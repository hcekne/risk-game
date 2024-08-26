import boto3
from risk_game.llm_clients.llm_base import LLMClient 
import time
import json

class BedrockClient(LLMClient):
    def __init__(self, model_number: int):
        self.client = boto3.client('bedrock-runtime', region_name='us-west-2')
        if model_number == 1:
            model_type = "meta.llama3-1-405b-instruct-v1:0"
        if model_number == 2:
            model_type = "meta.llama3-1-70b-instruct-v1:0"
        else:
            raise ValueError("Invalid model number. Please choose a number " +
                             "between 1 and 2.")
        
        # Call the parent class constructor to set provider and model_type
        super().__init__(provider_name="AWS_Bedrock", model_type=model_type)
    
    def get_chat_completion(self, message_content: str) -> str:

        full_prompt = {
            "prompt": message_content,
            "max_gen_len": 2000,
            "temperature": 1,
            "top_p": 1
        }

        for attempt in range(self.max_retries):
            try:
                response = self.client.invoke_model(
                    contentType="application/json", 
                    body=json.dumps(full_prompt),
                    modelId=self.model_type
                )
                # print(response)
                response_body = response["body"].read().decode("utf-8")
                # print(response_body)
                generated_text = json.loads(response_body).get('generation', '')
                cleaned_text = generated_text.replace('\n', ' ')
                return cleaned_text
            except Exception as e:
                print(f"Attempt {attempt + 1} failed with error: {e}." +
                f"Retrying in {self.retry_delay} seconds...")
                time.sleep(self.retry_delay)

        raise Exception("Maximum retries reached. Service is still unavailable.")