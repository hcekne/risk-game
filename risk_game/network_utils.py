from typing import List, Dict
import os
from groq import Groq


class GroqClient:
    def __init__(self, model_number:int):
        self.client = Groq(
            api_key=os.environ.get("GROQ_API_KEY"),
        )
        self.model_number = model_number

    def get_chat_completion(self,messages:List[Dict[str, str]]) -> str:
        if  self.model_number == 1:
            model_type="llama-3.1-70b-versatile"
        elif self.model_number == 2:
            model_type="llama3-70b-8192"
        elif self.model_number == 3:
            model_type="llama-3.1-8b-instant"
        elif self.model_number == 4:
            model_type="mixtral-8x7b-32768"
        
        
        return self.client.chat.completions.create(
            messages=messages,
            model=model_type,
        )
