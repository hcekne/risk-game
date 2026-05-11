import time
from dataclasses import dataclass
from typing import Any, Dict, Optional, Tuple

from openai import (
    APIConnectionError,
    APITimeoutError,
    APIStatusError,
    InternalServerError,
    OpenAI,
    RateLimitError,
)

from risk_game.llm_clients.llm_base import LLMClient


@dataclass(frozen=True)
class OpenAIModelConfig:
    supports_reasoning: bool
    supports_verbosity: bool
    reasoning_efforts: Optional[Tuple[str, ...]]


class OpenAIClient(LLMClient):
    DEFAULT_TIMEOUT_SECONDS = 1200.0
    OPEN_REASONING_EFFORTS = ("none", "minimal", "low", "medium", "high", "xhigh")
    VALID_VERBOSITY = {"low", "medium", "high"}

    MODEL_CONFIGS: Dict[str, OpenAIModelConfig] = {
        "gpt-5.5": OpenAIModelConfig(
            supports_reasoning=True,
            supports_verbosity=True,
            reasoning_efforts=("none", "low", "medium", "high", "xhigh"),
        ),
        "gpt-5.5-pro": OpenAIModelConfig(
            supports_reasoning=True,
            supports_verbosity=True,
            reasoning_efforts=("medium", "high", "xhigh"),
        ),
        "gpt-5.4": OpenAIModelConfig(
            supports_reasoning=True,
            supports_verbosity=True,
            reasoning_efforts=("none", "low", "medium", "high", "xhigh"),
        ),
        "gpt-5.4-mini": OpenAIModelConfig(
            supports_reasoning=True,
            supports_verbosity=True,
            reasoning_efforts=("none", "low", "medium", "high", "xhigh"),
        ),
        "gpt-5.4-nano": OpenAIModelConfig(
            supports_reasoning=True,
            supports_verbosity=True,
            reasoning_efforts=("none", "low", "medium", "high", "xhigh"),
        ),
        "gpt-5.4-pro": OpenAIModelConfig(
            supports_reasoning=True,
            supports_verbosity=True,
            reasoning_efforts=("medium", "high", "xhigh"),
        ),
        "gpt-5": OpenAIModelConfig(
            supports_reasoning=True,
            supports_verbosity=True,
            reasoning_efforts=("minimal", "low", "medium", "high"),
        ),
        "gpt-5-mini": OpenAIModelConfig(
            supports_reasoning=True,
            supports_verbosity=True,
            reasoning_efforts=("minimal", "low", "medium", "high"),
        ),
        "gpt-5-nano": OpenAIModelConfig(
            supports_reasoning=True,
            supports_verbosity=True,
            reasoning_efforts=("minimal", "low", "medium", "high"),
        ),
        "gpt-5-pro": OpenAIModelConfig(
            supports_reasoning=True,
            supports_verbosity=True,
            reasoning_efforts=("high",),
        ),
        "gpt-5.1": OpenAIModelConfig(
            supports_reasoning=True,
            supports_verbosity=True,
            reasoning_efforts=("none", "low", "medium", "high"),
        ),
        "gpt-5.2": OpenAIModelConfig(
            supports_reasoning=True,
            supports_verbosity=True,
            reasoning_efforts=("none", "low", "medium", "high", "xhigh"),
        ),
        "gpt-5.2-pro": OpenAIModelConfig(
            supports_reasoning=True,
            supports_verbosity=True,
            reasoning_efforts=("medium", "high", "xhigh"),
        ),
        "gpt-5-chat-latest": OpenAIModelConfig(
            supports_reasoning=False,
            supports_verbosity=False,
            reasoning_efforts=tuple(),
        ),
        # Current non-reasoning text families.
        "gpt-4.1": OpenAIModelConfig(
            supports_reasoning=False,
            supports_verbosity=False,
            reasoning_efforts=tuple(),
        ),
        "gpt-4.1-mini": OpenAIModelConfig(
            supports_reasoning=False,
            supports_verbosity=False,
            reasoning_efforts=tuple(),
        ),
        "gpt-4.1-nano": OpenAIModelConfig(
            supports_reasoning=False,
            supports_verbosity=False,
            reasoning_efforts=tuple(),
        ),
        "gpt-4o": OpenAIModelConfig(
            supports_reasoning=False,
            supports_verbosity=False,
            reasoning_efforts=tuple(),
        ),
        "gpt-4o-mini": OpenAIModelConfig(
            supports_reasoning=False,
            supports_verbosity=False,
            reasoning_efforts=tuple(),
        ),
        # o-series models are reasoning-first, but the current docs do not
        # publish a single strict reasoning.effort table across all variants.
        # We therefore accept the common effort labels locally and let the API
        # return the authoritative error if a specific model rejects one.
        "o3": OpenAIModelConfig(
            supports_reasoning=True,
            supports_verbosity=False,
            reasoning_efforts=None,
        ),
        "o3-mini": OpenAIModelConfig(
            supports_reasoning=True,
            supports_verbosity=False,
            reasoning_efforts=None,
        ),
        "o3-pro": OpenAIModelConfig(
            supports_reasoning=True,
            supports_verbosity=False,
            reasoning_efforts=None,
        ),
        "o4-mini": OpenAIModelConfig(
            supports_reasoning=True,
            supports_verbosity=False,
            reasoning_efforts=None,
        ),
    }

    LEGACY_MODEL_NUMBERS = {
        1: "gpt-5.4",
        2: "gpt-5.4-mini",
        3: "gpt-5.4-nano",
        4: "gpt-4.1",
        5: "gpt-5-chat-latest",
    }

    def __init__(
        self,
        model_number: Optional[int] = None,
        *,
        model_name: Optional[str] = None,
        use_responses_api: bool = True,
        reasoning_effort: Optional[str] = "none",
        verbosity: str = "low",
        timeout_seconds: float = DEFAULT_TIMEOUT_SECONDS,
        max_retries: int = 2,
        retry_delay: int = 10,
    ):
        resolved_model_name = self._resolve_model_name(
            model_number=model_number,
            model_name=model_name,
        )
        config = self._get_model_config(resolved_model_name)

        self.client = OpenAI(timeout=timeout_seconds)
        self.use_responses_api = use_responses_api
        self.model_type = resolved_model_name
        self.model_config = config
        self.supports_reasoning = config.supports_reasoning
        self.supports_verbosity = config.supports_verbosity
        self.reasoning_effort = self._validate_reasoning_effort(
            reasoning_effort=reasoning_effort,
            config=config,
        )
        self.verbosity = self._validate_verbosity(verbosity=verbosity)
        self.timeout_seconds = timeout_seconds

        super().__init__(
            provider_name="OpenAI",
            model_type=self.model_type,
            max_retries=max_retries,
            retry_delay=retry_delay,
        )

    @classmethod
    def supported_models(cls) -> Dict[str, Dict[str, object]]:
        return {
            model_name: {
                "supports_reasoning": config.supports_reasoning,
                "supports_verbosity": config.supports_verbosity,
                "reasoning_efforts": (
                    cls.OPEN_REASONING_EFFORTS
                    if config.reasoning_efforts is None
                    else config.reasoning_efforts
                ),
            }
            for model_name, config in cls.MODEL_CONFIGS.items()
        }

    @classmethod
    def supported_reasoning_efforts(cls, model_name: str) -> tuple[str, ...]:
        config = cls._get_model_config(model_name)
        if not config.supports_reasoning:
            return tuple()
        if config.reasoning_efforts is None:
            return cls.OPEN_REASONING_EFFORTS
        return config.reasoning_efforts

    @classmethod
    def _canonical_model_names(cls) -> list[str]:
        return sorted(cls.MODEL_CONFIGS.keys())

    @classmethod
    def _get_model_config(cls, model_name: str) -> OpenAIModelConfig:
        if model_name in cls.MODEL_CONFIGS:
            return cls.MODEL_CONFIGS[model_name]

        for prefix in sorted(cls.MODEL_CONFIGS.keys(), key=len, reverse=True):
            if model_name.startswith(f"{prefix}-"):
                return cls.MODEL_CONFIGS[prefix]

        raise ValueError(
            f"Unknown OpenAI model '{model_name}'. "
            f"Choose from {cls._canonical_model_names()}"
        )

    def _resolve_model_name(
        self,
        model_number: Optional[int],
        model_name: Optional[str],
    ) -> str:
        if model_name:
            self._get_model_config(model_name)
            return model_name

        if model_number is None:
            raise ValueError("Either model_name or model_number must be provided")

        if model_number not in self.LEGACY_MODEL_NUMBERS:
            raise ValueError(
                "Invalid OpenAI model number. "
                f"Choose from {list(self.LEGACY_MODEL_NUMBERS.keys())}"
            )

        return self.LEGACY_MODEL_NUMBERS[model_number]

    def _validate_reasoning_effort(
        self,
        reasoning_effort: Optional[str],
        config: OpenAIModelConfig,
    ) -> Optional[str]:
        if not config.supports_reasoning:
            if reasoning_effort not in (None, "none"):
                raise ValueError(
                    f"Model '{self.model_type}' does not support reasoning_effort"
                )
            return None

        if reasoning_effort is None:
            return "none"

        valid_efforts = (
            config.reasoning_efforts
            if config.reasoning_efforts is not None
            else self.OPEN_REASONING_EFFORTS
        )
        if reasoning_effort not in valid_efforts:
            raise ValueError(
                f"Invalid reasoning_effort '{reasoning_effort}' for "
                f"'{self.model_type}'. Choose from {list(valid_efforts)}"
            )
        return reasoning_effort

    def _validate_verbosity(self, verbosity: str) -> str:
        if verbosity not in self.VALID_VERBOSITY:
            raise ValueError(
                f"Invalid verbosity '{verbosity}'. "
                f"Choose from {sorted(self.VALID_VERBOSITY)}"
            )
        return verbosity

    def _resolve_reasoning_effort_override(
        self, reasoning_effort: Optional[str]
    ) -> Optional[str]:
        if reasoning_effort is None:
            return self.reasoning_effort
        return self._validate_reasoning_effort(
            reasoning_effort=reasoning_effort,
            config=self.model_config,
        )

    def _standardize_usage_from_responses_api(
        self,
        usage_payload: Optional[Dict[str, Any]],
    ) -> Optional[Dict[str, Optional[int]]]:
        if not usage_payload:
            return None
        input_details = usage_payload.get("input_tokens_details") or {}
        output_details = usage_payload.get("output_tokens_details") or {}
        return {
            "input_tokens": usage_payload.get("input_tokens"),
            "output_tokens": usage_payload.get("output_tokens"),
            "total_tokens": usage_payload.get("total_tokens"),
            "cached_input_tokens": input_details.get("cached_tokens"),
            "reasoning_tokens": output_details.get("reasoning_tokens"),
        }

    def _standardize_usage_from_chat_completions(
        self,
        usage_payload: Optional[Dict[str, Any]],
    ) -> Optional[Dict[str, Optional[int]]]:
        if not usage_payload:
            return None
        prompt_details = usage_payload.get("prompt_tokens_details") or {}
        completion_details = usage_payload.get("completion_tokens_details") or {}
        return {
            "input_tokens": usage_payload.get("prompt_tokens"),
            "output_tokens": usage_payload.get("completion_tokens"),
            "total_tokens": usage_payload.get("total_tokens"),
            "cached_input_tokens": prompt_details.get("cached_tokens"),
            "reasoning_tokens": completion_details.get("reasoning_tokens"),
        }

    def get_chat_completion(
        self,
        message_content,
        *,
        reasoning_effort: Optional[str] = None,
        timeout_seconds: Optional[float] = None,
        max_attempts_override: Optional[int] = None,
    ) -> str:
        if self.use_responses_api:
            return self._get_response_completion(
                message_content,
                reasoning_effort=reasoning_effort,
                timeout_seconds=timeout_seconds,
                max_attempts_override=max_attempts_override,
            )
        return self._get_chat_completion_legacy(
            message_content,
            timeout_seconds=timeout_seconds,
            max_attempts_override=max_attempts_override,
        )

    def _get_response_completion(
        self,
        message_content,
        *,
        reasoning_effort: Optional[str] = None,
        timeout_seconds: Optional[float] = None,
        max_attempts_override: Optional[int] = None,
    ) -> str:
        resolved_reasoning_effort = self._resolve_reasoning_effort_override(
            reasoning_effort
        )
        max_attempts = (
            self.max_retries if max_attempts_override is None else max_attempts_override
        )
        if max_attempts < 1:
            raise ValueError("max_attempts_override must be at least 1")
        client = (
            self.client
            if timeout_seconds is None
            else self.client.with_options(timeout=timeout_seconds)
        )
        last_error: Optional[Exception] = None
        for attempt in range(max_attempts):
            try:
                params = {
                    "model": self.model_type,
                    "input": message_content,
                    "instructions": self.system_prompt,
                }

                if self.supports_reasoning and resolved_reasoning_effort is not None:
                    params["reasoning"] = {"effort": resolved_reasoning_effort}
                if self.supports_verbosity:
                    params["text"] = {"verbosity": self.verbosity}

                response = client.responses.create(**params)
                raw_usage = (
                    response.usage.model_dump()
                    if getattr(response, "usage", None) is not None
                    else None
                )
                self.set_last_response_metadata(
                    {
                        "api_variant": "responses",
                        "usage": self._standardize_usage_from_responses_api(raw_usage),
                        "raw_usage": raw_usage,
                    }
                )
                return response.output_text

            except (APITimeoutError, APIConnectionError) as e:
                last_error = e
                if attempt == max_attempts - 1:
                    break
                print(
                    f"Attempt {attempt + 1} failed with transport error: {e}. "
                    f"Retrying in {self.retry_delay} seconds..."
                )
                time.sleep(self.retry_delay)
            except (InternalServerError, RateLimitError, APIStatusError) as e:
                last_error = e
                if attempt == max_attempts - 1:
                    break
                print(
                    f"Attempt {attempt + 1} failed with API error: {e}. "
                    f"Retrying in {self.retry_delay} seconds..."
                )
                time.sleep(self.retry_delay)
            except Exception as e:
                raise RuntimeError(
                    f"OpenAI response request failed unexpectedly for "
                    f"{self.model_type}: {e}"
                ) from e

        raise RuntimeError(
            f"OpenAI response request failed after {max_attempts} attempts "
            f"for {self.model_type}: {type(last_error).__name__}: {last_error}"
        )

    def _get_chat_completion_legacy(
        self,
        message_content,
        *,
        timeout_seconds: Optional[float] = None,
        max_attempts_override: Optional[int] = None,
    ) -> str:
        messages = [
            {
                "role": "system",
                "content": self.system_prompt,
            },
            {
                "role": "user",
                "content": message_content,
            },
        ]
        client = (
            self.client
            if timeout_seconds is None
            else self.client.with_options(timeout=timeout_seconds)
        )
        max_attempts = (
            self.max_retries if max_attempts_override is None else max_attempts_override
        )
        if max_attempts < 1:
            raise ValueError("max_attempts_override must be at least 1")
        last_error: Optional[Exception] = None

        for attempt in range(max_attempts):
            try:
                response = client.chat.completions.create(
                    model=self.model_type,
                    messages=messages,
                    temperature=0,
                )
                raw_usage = (
                    response.usage.model_dump()
                    if getattr(response, "usage", None) is not None
                    else None
                )
                self.set_last_response_metadata(
                    {
                        "api_variant": "chat_completions",
                        "usage": self._standardize_usage_from_chat_completions(
                            raw_usage
                        ),
                        "raw_usage": raw_usage,
                    }
                )
                return response.choices[0].message.content
            except (APITimeoutError, APIConnectionError) as e:
                last_error = e
                if attempt == max_attempts - 1:
                    break
                print(
                    f"Attempt {attempt + 1} failed with transport error: {e}. "
                    f"Retrying in {self.retry_delay} seconds..."
                )
                time.sleep(self.retry_delay)
            except (InternalServerError, RateLimitError, APIStatusError) as e:
                last_error = e
                if attempt == max_attempts - 1:
                    break
                print(
                    f"Attempt {attempt + 1} failed with API error: {e}. "
                    f"Retrying in {self.retry_delay} seconds..."
                )
                time.sleep(self.retry_delay)
            except Exception as e:
                raise RuntimeError(
                    f"OpenAI chat completion failed unexpectedly for "
                    f"{self.model_type}: {e}"
                ) from e

        raise RuntimeError(
            f"OpenAI chat completion failed after {max_attempts} attempts "
            f"for {self.model_type}: {type(last_error).__name__}: {last_error}"
        )
