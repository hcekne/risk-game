from copy import deepcopy
from typing import Any, Dict, List, Optional
from abc import ABC, abstractmethod
from risk_game.llm_clients.system_prompts import (
    DEFAULT_SYSTEM_PROMPT_PROFILE,
    resolve_system_prompt,
)

class LLMClient(ABC):
    def __init__(self, provider_name: str, model_type: str, max_retries: int=4,
                 retry_delay: int=10,
                 system_prompt_profile: str = DEFAULT_SYSTEM_PROMPT_PROFILE,
                 system_prompt_override: Optional[str] = None) -> None:
        self.provider_name = provider_name
        self.model_type = model_type
        self.retry_delay = retry_delay
        self.max_retries = max_retries
        self.system_prompt_profile = system_prompt_profile
        self.system_prompt = resolve_system_prompt(
            profile=system_prompt_profile,
            override=system_prompt_override,
        )
        self.last_response_metadata: Optional[Dict[str, Any]] = None


    @abstractmethod
    def get_chat_completion(self, messages: List[Dict[str, str]]) -> str:
        pass

    def clear_last_response_metadata(self) -> None:
        self.last_response_metadata = None

    def set_last_response_metadata(
        self,
        metadata: Optional[Dict[str, Any]],
    ) -> None:
        self.last_response_metadata = (
            deepcopy(metadata) if metadata is not None else None
        )

    def get_last_response_metadata(self) -> Optional[Dict[str, Any]]:
        return deepcopy(self.last_response_metadata)

    def set_system_prompt_profile(self, profile: str) -> None:
        self.system_prompt_profile = profile
        self.system_prompt = resolve_system_prompt(profile=profile)

    def set_system_prompt(self, prompt: str) -> None:
        self.system_prompt_profile = "custom"
        self.system_prompt = resolve_system_prompt(
            profile=DEFAULT_SYSTEM_PROMPT_PROFILE,
            override=prompt,
        )

    def __repr__(self) -> str:
        return (f"<LLMClient(provider='{self.provider_name}', " +
                f"model='{self.model_type}')>")
