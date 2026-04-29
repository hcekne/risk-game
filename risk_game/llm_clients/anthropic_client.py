import os
import time
from dataclasses import dataclass
from typing import Dict, Optional, Tuple

from anthropic import (
    APIConnectionError,
    APIStatusError,
    APITimeoutError,
    Anthropic,
    AnthropicError,
    InternalServerError,
    RateLimitError,
)

from risk_game.llm_clients.llm_base import LLMClient


@dataclass(frozen=True)
class AnthropicModelConfig:
    supports_thinking: bool
    thinking_types: Tuple[str, ...]
    supports_effort: bool
    supports_effort_max: bool = False
    supports_temperature: bool = True


class AnthropicClient(LLMClient):
    DEFAULT_TIMEOUT_SECONDS = 1200.0

    MODEL_CONFIGS: Dict[str, AnthropicModelConfig] = {
        "claude-opus-4-7": AnthropicModelConfig(
            supports_thinking=True,
            thinking_types=("adaptive",),
            supports_effort=False,
            supports_temperature=False,
        ),
        "claude-sonnet-4-6": AnthropicModelConfig(
            supports_thinking=True,
            thinking_types=("enabled", "adaptive"),
            supports_effort=True,
            supports_effort_max=True,
        ),
        "claude-opus-4-6": AnthropicModelConfig(
            supports_thinking=True,
            thinking_types=("enabled", "adaptive"),
            supports_effort=True,
            supports_effort_max=True,
        ),
        "claude-opus-4-5-20251101": AnthropicModelConfig(
            supports_thinking=True,
            thinking_types=("enabled",),
            supports_effort=True,
        ),
        "claude-haiku-4-5-20251001": AnthropicModelConfig(
            supports_thinking=True,
            thinking_types=("enabled",),
            supports_effort=False,
        ),
        "claude-sonnet-4-5-20250929": AnthropicModelConfig(
            supports_thinking=True,
            thinking_types=("enabled",),
            supports_effort=False,
        ),
        "claude-opus-4-1-20250805": AnthropicModelConfig(
            supports_thinking=True,
            thinking_types=("enabled",),
            supports_effort=False,
        ),
        "claude-opus-4-20250514": AnthropicModelConfig(
            supports_thinking=True,
            thinking_types=("enabled",),
            supports_effort=False,
        ),
        "claude-sonnet-4-20250514": AnthropicModelConfig(
            supports_thinking=True,
            thinking_types=("enabled",),
            supports_effort=False,
        ),
    }

    LEGACY_MODEL_ALIASES = {
        "claude-opus-4-1": "claude-opus-4-1-20250805",
        "claude-opus-4-0": "claude-opus-4-20250514",
        "claude-sonnet-4-0": "claude-sonnet-4-20250514",
        "claude-3-7-sonnet-latest": "claude-sonnet-4-6",
        "claude-3-5-sonnet-latest": "claude-sonnet-4-5-20250929",
    }

    LEGACY_MODEL_NUMBERS = {
        1: "claude-opus-4-7",
        2: "claude-sonnet-4-6",
        3: "claude-opus-4-6",
        4: "claude-haiku-4-5-20251001",
        5: "claude-sonnet-4-5-20250929",
        6: "claude-opus-4-1-20250805",
        7: "claude-opus-4-20250514",
        8: "claude-sonnet-4-20250514",
    }

    THINKING_BUDGET_BY_REASONING = {
        "low": 1024,
        "medium": 4096,
        "high": 12000,
        "xhigh": 24000,
    }
    ADAPTIVE_EFFORT_BY_REASONING = {
        "low": "low",
        "medium": "medium",
        "high": "high",
        "xhigh": "max",
    }

    def __init__(
        self,
        model_number: Optional[int] = None,
        *,
        model_name: Optional[str] = None,
        enable_thinking: bool = False,
        thinking_budget: int = 2000,
        thinking_effort: Optional[str] = None,
        timeout_seconds: float = DEFAULT_TIMEOUT_SECONDS,
        max_retries: int = 2,
        retry_delay: int = 10,
    ):
        resolved_model_name = self._resolve_model_name(
            model_number=model_number,
            model_name=model_name,
        )
        config = self.MODEL_CONFIGS[resolved_model_name]

        self.client = Anthropic(
            api_key=os.environ.get("ANTHROPIC_API_KEY"),
            timeout=timeout_seconds,
            max_retries=0,
        )
        self.model_type = resolved_model_name
        self.model_config = config
        self.enable_thinking = enable_thinking
        self.thinking_budget = thinking_budget
        self.thinking_effort = thinking_effort
        self.supports_thinking = config.supports_thinking
        self.timeout_seconds = timeout_seconds

        super().__init__(
            provider_name="Anthropic",
            model_type=self.model_type,
            max_retries=max_retries,
            retry_delay=retry_delay,
        )

    @classmethod
    def supported_models(cls) -> Dict[str, Dict[str, object]]:
        return {
            model_name: {
                "supports_thinking": config.supports_thinking,
                "thinking_types": config.thinking_types,
                "supports_effort": config.supports_effort,
                "supports_effort_max": config.supports_effort_max,
            }
            for model_name, config in cls.MODEL_CONFIGS.items()
        }

    def _resolve_model_name(
        self,
        model_number: Optional[int],
        model_name: Optional[str],
    ) -> str:
        if model_name:
            resolved_alias = self.LEGACY_MODEL_ALIASES.get(model_name, model_name)
            if resolved_alias not in self.MODEL_CONFIGS:
                raise ValueError(
                    f"Unknown Anthropic model '{model_name}'. "
                    f"Choose from {sorted(self.MODEL_CONFIGS.keys())}"
                )
            return resolved_alias

        if model_number is None:
            raise ValueError("Either model_name or model_number must be provided")

        if model_number not in self.LEGACY_MODEL_NUMBERS:
            raise ValueError(
                "Invalid Anthropic model number. "
                f"Choose from {list(self.LEGACY_MODEL_NUMBERS.keys())}"
            )

        return self.LEGACY_MODEL_NUMBERS[model_number]

    def _resolve_per_call_thinking(
        self,
        reasoning_effort: Optional[str],
    ) -> Optional[Dict[str, object]]:
        if not self.supports_thinking or not self.enable_thinking:
            return None
        resolved_reasoning_effort = reasoning_effort or self.thinking_effort

        if "adaptive" in self.model_config.thinking_types:
            thinking_config = {
                "type": "adaptive",
                "display": "omitted",
            }
            if self.model_config.supports_effort:
                if resolved_reasoning_effort in (None, "none"):
                    adaptive_effort = "medium"
                else:
                    adaptive_effort = self.ADAPTIVE_EFFORT_BY_REASONING.get(
                        resolved_reasoning_effort
                    )
                    if adaptive_effort is None:
                        raise ValueError(
                            f"Unsupported Anthropic reasoning_effort "
                            f"'{resolved_reasoning_effort}' for adaptive thinking."
                        )
                    if (
                        adaptive_effort == "max"
                        and not self.model_config.supports_effort_max
                    ):
                        adaptive_effort = "high"
                thinking_config["effort"] = adaptive_effort

            return thinking_config

        if resolved_reasoning_effort in (None, "none"):
            budget_tokens = self.thinking_budget
        else:
            budget_tokens = self.THINKING_BUDGET_BY_REASONING.get(
                resolved_reasoning_effort
            )
            if budget_tokens is None:
                raise ValueError(
                    f"Unsupported Anthropic reasoning_effort "
                    f"'{resolved_reasoning_effort}' for manual thinking."
                )

        return {
            "type": "enabled",
            "budget_tokens": budget_tokens,
            "display": "omitted",
        }

    def get_chat_completion(
        self,
        message_content,
        *,
        reasoning_effort: Optional[str] = None,
        timeout_seconds: Optional[float] = None,
        max_attempts_override: Optional[int] = None,
    ) -> str:
        full_prompt = [{"role": "user", "content": message_content}]
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
                    "system": self.system_prompt,
                    "max_tokens": 4000,
                    "messages": full_prompt,
                }
                if self.model_config.supports_temperature:
                    params["temperature"] = 0

                thinking_config = self._resolve_per_call_thinking(reasoning_effort)
                if thinking_config is not None:
                    params["thinking"] = thinking_config
                    if self.model_config.supports_temperature:
                        params["temperature"] = 1

                message = client.messages.create(**params)

                response_text = ""
                for block in message.content:
                    if block.type == "text":
                        response_text += block.text
                return response_text

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
                    f"Anthropic request failed unexpectedly for "
                    f"{self.model_type}: {e}"
                ) from e

        raise AnthropicError(
            f"Anthropic request failed after {max_attempts} attempts for "
            f"{self.model_type}: {type(last_error).__name__}: {last_error}"
        )
