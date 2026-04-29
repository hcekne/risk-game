import os
import time
from typing import Dict, Optional

from openai import (
    APIConnectionError,
    APITimeoutError,
    APIStatusError,
    InternalServerError,
    OpenAI,
    RateLimitError,
)

from risk_game.llm_clients.llm_base import LLMClient


class MoonshotClient(LLMClient):
    DEFAULT_TIMEOUT_SECONDS = 1200.0
    BASE_URL = "https://api.moonshot.ai/v1"

    LEGACY_MODEL_NUMBERS = {
        1: "kimi-k2.6",
        2: "kimi-k2.5",
        3: "moonshot-v1-auto",
        4: "moonshot-v1-8k",
        5: "moonshot-v1-32k",
        6: "moonshot-v1-128k",
    }

    CORE_MODELS: Dict[str, Dict[str, object]] = {
        "kimi-k2.6": {"family": "kimi"},
        "kimi-k2.5": {"family": "kimi"},
        "moonshot-v1-auto": {"family": "moonshot-v1"},
        "moonshot-v1-8k": {"family": "moonshot-v1"},
        "moonshot-v1-32k": {"family": "moonshot-v1"},
        "moonshot-v1-128k": {"family": "moonshot-v1"},
    }

    def __init__(
        self,
        model_number: Optional[int] = None,
        *,
        model_name: Optional[str] = None,
        enable_thinking: bool = False,
        timeout_seconds: float = DEFAULT_TIMEOUT_SECONDS,
        max_retries: int = 2,
        retry_delay: int = 10,
    ) -> None:
        resolved_model_name = self._resolve_model_name(
            model_number=model_number,
            model_name=model_name,
        )
        api_key = os.environ.get("MOONSHOT_API_KEY")
        if not api_key:
            raise ValueError(
                "MoonshotClient requires MOONSHOT_API_KEY in the environment."
            )

        self.client = OpenAI(
            api_key=api_key,
            base_url=self.BASE_URL,
            timeout=timeout_seconds,
        )
        self.model_type = resolved_model_name
        self.enable_thinking = enable_thinking
        self.timeout_seconds = timeout_seconds

        super().__init__(
            provider_name="Moonshot",
            model_type=self.model_type,
            max_retries=max_retries,
            retry_delay=retry_delay,
        )

    @classmethod
    def supported_models(cls) -> Dict[str, Dict[str, object]]:
        return cls.CORE_MODELS.copy()

    def _resolve_model_name(
        self,
        model_number: Optional[int],
        model_name: Optional[str],
    ) -> str:
        if model_name:
            if not (
                model_name.startswith("kimi-") or model_name.startswith("moonshot-")
            ):
                raise ValueError(
                    "Moonshot model names must start with 'kimi-' or 'moonshot-'. "
                    f"Received '{model_name}'."
                )
            return model_name

        if model_number is None:
            raise ValueError("Either model_name or model_number must be provided")

        if model_number not in self.LEGACY_MODEL_NUMBERS:
            raise ValueError(
                "Invalid Moonshot model number. "
                f"Choose from {list(self.LEGACY_MODEL_NUMBERS.keys())}"
            )

        return self.LEGACY_MODEL_NUMBERS[model_number]

    def get_chat_completion(
        self,
        message_content,
        *,
        reasoning_effort: Optional[str] = None,
        timeout_seconds: Optional[float] = None,
        max_attempts_override: Optional[int] = None,
    ) -> str:
        del reasoning_effort
        max_attempts = (
            self.max_retries if max_attempts_override is None else max_attempts_override
        )
        if max_attempts < 1:
            raise ValueError("max_attempts_override must be at least 1")

        request_timeout = (
            self.timeout_seconds if timeout_seconds is None else timeout_seconds
        )
        active_client = (
            self.client
            if request_timeout == self.timeout_seconds
            else self.client.with_options(timeout=request_timeout)
        )

        last_error: Optional[Exception] = None
        for attempt in range(max_attempts):
            try:
                response = active_client.chat.completions.create(
                    model=self.model_type,
                    messages=[
                        {
                            "role": "system",
                            "content": self.system_prompt,
                        },
                        {"role": "user", "content": message_content},
                    ],
                    extra_body={
                        "thinking": {
                            "type": "enabled" if self.enable_thinking else "disabled"
                        }
                    },
                )
                content = response.choices[0].message.content
                if not content:
                    raise RuntimeError(
                        f"Moonshot response for {self.model_type} contained no text."
                    )
                return content
            except (
                APIConnectionError,
                APITimeoutError,
                InternalServerError,
                RateLimitError,
            ) as exc:
                last_error = exc
                if attempt == max_attempts - 1:
                    break
                print(
                    f"Attempt {attempt + 1} failed with transport/server error: {exc}. "
                    f"Retrying in {self.retry_delay} seconds..."
                )
                time.sleep(self.retry_delay)
            except APIStatusError as exc:
                last_error = exc
                if attempt == max_attempts - 1:
                    break
                print(
                    f"Attempt {attempt + 1} failed with API status error: {exc}. "
                    f"Retrying in {self.retry_delay} seconds..."
                )
                time.sleep(self.retry_delay)
            except Exception as exc:
                raise RuntimeError(
                    f"Moonshot request failed unexpectedly for {self.model_type}: {exc}"
                ) from exc

        error_body = ""
        if isinstance(last_error, APIStatusError):
            response = getattr(last_error, "response", None)
            if response is not None:
                error_body = str(getattr(response, "text", ""))[:1200]

        raise RuntimeError(
            f"Moonshot request failed after {max_attempts} attempts for "
            f"{self.model_type}: {type(last_error).__name__}: {last_error}"
            f"{' | body=' + error_body if error_body else ''}"
        )
