from typing import List, Dict
from abc import ABC, abstractmethod

class LLMClient(ABC):
    @abstractmethod
    def get_chat_completion(self, messages: List[Dict[str, str]]) -> str:
        pass



