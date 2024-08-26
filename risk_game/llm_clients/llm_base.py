from typing import List, Dict
from abc import ABC, abstractmethod

class LLMClient(ABC):
    def __init__(self, provider_name: str, model_type: str, max_retries: int=4,
                 retry_delay: int=10) -> None:
        self.provider_name = provider_name
        self.model_type = model_type
        self.retry_delay = retry_delay
        self.max_retries = max_retries


    @abstractmethod
    def get_chat_completion(self, messages: List[Dict[str, str]]) -> str:
        pass

    def __repr__(self) -> str:
        return (f"<LLMClient(provider='{self.provider_name}', " +
                f"model='{self.model_type}')>")


