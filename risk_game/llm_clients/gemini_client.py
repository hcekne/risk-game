import os
import time
from typing import Dict, Optional

import requests

from risk_game.llm_clients.llm_base import LLMClient


class GeminiClient(LLMClient):
    DEFAULT_TIMEOUT_SECONDS = 1200.0
    BASE_URL = "https://generativelanguage.googleapis.com/v1beta/models"

    LEGACY_MODEL_NUMBERS = {
        1: "gemini-2.5-pro",
        2: "gemini-2.5-flash",
        3: "gemini-2.5-flash-lite",
        4: "gemini-3.1-pro-preview",
        5: "gemini-3.1-flash-lite-preview",
    }

    CORE_MODELS: Dict[str, Dict[str, object]] = {
        "gemini-2.5-pro": {"family": "gemini-2.5"},
        "gemini-2.5-flash": {"family": "gemini-2.5"},
        "gemini-2.5-flash-lite": {"family": "gemini-2.5"},
        "gemini-3-pro-preview": {"family": "gemini-3"},
        "gemini-3-flash-preview": {"family": "gemini-3"},
        "gemini-3.1-pro-preview": {"family": "gemini-3"},
        "gemini-3.1-flash-lite-preview": {"family": "gemini-3"},
    }

    THINKING_BUDGET_BY_REASONING = {
        "none": 0,
        "low": 512,
        "medium": 4096,
        "high": 12288,
        "xhigh": 24576,
    }
    GEMINI3_LEVEL_BY_REASONING = {
        "none": "minimal",
        "low": "low",
        "medium": "medium",
        "high": "high",
        "xhigh": "high",
    }

    def __init__(
        self,
        model_number: Optional[int] = None,
        *,
        model_name: Optional[str] = None,
        reasoning_effort: Optional[str] = "medium",
        thinking_budget: Optional[int] = None,
        include_thoughts: bool = False,
        timeout_seconds: float = DEFAULT_TIMEOUT_SECONDS,
        max_retries: int = 2,
        retry_delay: int = 10,
    ):
        resolved_model_name = self._resolve_model_name(
            model_number=model_number,
            model_name=model_name,
        )
        self.api_key = os.environ.get("GEMINI_API_KEY") or os.environ.get(
            "GOOGLE_API_KEY"
        )
        if not self.api_key:
            raise ValueError(
                "GeminiClient requires GEMINI_API_KEY or GOOGLE_API_KEY in the environment."
            )

        self.model_type = resolved_model_name
        self.reasoning_effort = reasoning_effort
        self.thinking_budget = thinking_budget
        self.include_thoughts = include_thoughts
        self.timeout_seconds = timeout_seconds

        super().__init__(
            provider_name="Gemini",
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
            if model_name.startswith("models/"):
                model_name = model_name.split("/", 1)[1]
            if not model_name.startswith("gemini-"):
                raise ValueError(
                    "Gemini model names must start with 'gemini-'. "
                    f"Received '{model_name}'."
                )
            return model_name

        if model_number is None:
            raise ValueError("Either model_name or model_number must be provided")

        if model_number not in self.LEGACY_MODEL_NUMBERS:
            raise ValueError(
                "Invalid Gemini model number. "
                f"Choose from {list(self.LEGACY_MODEL_NUMBERS.keys())}"
            )
        return self.LEGACY_MODEL_NUMBERS[model_number]

    def _model_family(self) -> str:
        if self.model_type.startswith("gemini-3"):
            return "gemini-3"
        if self.model_type.startswith("gemini-2.5"):
            return "gemini-2.5"
        return "unknown"

    def _build_generation_config(
        self,
        reasoning_effort: Optional[str],
    ) -> Dict[str, object]:
        resolved_reasoning = self.reasoning_effort if reasoning_effort is None else reasoning_effort
        family = self._model_family()

        thinking_config: Dict[str, object] = {}

        if family == "gemini-3":
            level = self.GEMINI3_LEVEL_BY_REASONING.get(resolved_reasoning or "medium")
            if level is None:
                raise ValueError(
                    f"Unsupported Gemini reasoning_effort '{resolved_reasoning}' "
                    f"for {self.model_type}."
                )
            if self.model_type.startswith("gemini-3.1-") and level == "minimal":
                # The Gemini 3.1 Pro preview rejects MINIMAL. Use LOW as the
                # cheapest supported live setting instead of surfacing a
                # predictable 400 to the caller.
                level = "low"
            thinking_config["thinkingLevel"] = level
            if self.include_thoughts:
                thinking_config["includeThoughts"] = True
        elif family == "gemini-2.5":
            if self.thinking_budget is not None and reasoning_effort is None:
                budget = self.thinking_budget
            else:
                budget = self.THINKING_BUDGET_BY_REASONING.get(
                    resolved_reasoning or "medium"
                )
                if budget is None:
                    raise ValueError(
                        f"Unsupported Gemini reasoning_effort '{resolved_reasoning}' "
                        f"for {self.model_type}."
                    )
            if "pro" in self.model_type and budget == 0:
                # Gemini 2.5 Pro does not allow full thinking-off. Use the
                # minimum practical budget instead of generating an avoidable 400.
                budget = 128
            thinking_config["thinkingBudget"] = budget
            if self.include_thoughts:
                thinking_config["includeThoughts"] = True
        elif self.include_thoughts:
            thinking_config["includeThoughts"] = True

        if not thinking_config:
            return {}
        return {"thinkingConfig": thinking_config}

    def _extract_text(self, payload: Dict[str, object]) -> str:
        candidates = payload.get("candidates") or []
        if not candidates:
            raise RuntimeError(f"Gemini response contained no candidates: {payload}")

        parts = (
            candidates[0]
            .get("content", {})
            .get("parts", [])
        )

        text_parts = []
        for part in parts:
            text = part.get("text")
            if text:
                text_parts.append(text)

        if not text_parts:
            raise RuntimeError(f"Gemini response contained no text parts: {payload}")
        return "".join(text_parts)

    def _standardize_usage(
        self,
        usage_metadata: Optional[Dict[str, object]],
    ) -> Optional[Dict[str, Optional[int]]]:
        if not usage_metadata:
            return None
        input_tokens = usage_metadata.get("promptTokenCount")
        output_tokens = usage_metadata.get("candidatesTokenCount")
        thoughts_tokens = usage_metadata.get("thoughtsTokenCount")
        total_tokens = usage_metadata.get("totalTokenCount")
        if (
            total_tokens is None
            and input_tokens is not None
            and output_tokens is not None
        ):
            total_tokens = int(input_tokens) + int(output_tokens)
        return {
            "input_tokens": input_tokens,
            "output_tokens": output_tokens,
            "total_tokens": total_tokens,
            "cached_input_tokens": usage_metadata.get("cachedContentTokenCount"),
            "reasoning_tokens": thoughts_tokens,
        }

    def get_chat_completion(
        self,
        message_content,
        *,
        reasoning_effort: Optional[str] = None,
        timeout_seconds: Optional[float] = None,
        max_attempts_override: Optional[int] = None,
    ) -> str:
        max_attempts = (
            self.max_retries if max_attempts_override is None else max_attempts_override
        )
        if max_attempts < 1:
            raise ValueError("max_attempts_override must be at least 1")

        request_timeout = (
            self.timeout_seconds if timeout_seconds is None else timeout_seconds
        )
        generation_config = self._build_generation_config(reasoning_effort)
        payload: Dict[str, object] = {
            "systemInstruction": {
                "parts": [
                    {"text": self.system_prompt}
                ]
            },
            "contents": [
                {
                    "role": "user",
                    "parts": [{"text": message_content}],
                }
            ],
        }
        if generation_config:
            payload["generationConfig"] = generation_config

        headers = {
            "Content-Type": "application/json",
            "x-goog-api-key": self.api_key,
        }
        endpoint = f"{self.BASE_URL}/{self.model_type}:generateContent"

        last_error: Optional[Exception] = None
        for attempt in range(max_attempts):
            try:
                response = requests.post(
                    endpoint,
                    headers=headers,
                    json=payload,
                    timeout=request_timeout,
                )
                response.raise_for_status()
                response_payload = response.json()
                self.set_last_response_metadata(
                    {
                        "api_variant": "generate_content",
                        "usage": self._standardize_usage(
                            response_payload.get("usageMetadata")
                        ),
                        "raw_usage": response_payload.get("usageMetadata"),
                    }
                )
                return self._extract_text(response_payload)
            except (requests.Timeout, requests.ConnectionError) as exc:
                last_error = exc
                if attempt == max_attempts - 1:
                    break
                print(
                    f"Attempt {attempt + 1} failed with transport error: {exc}. "
                    f"Retrying in {self.retry_delay} seconds..."
                )
                time.sleep(self.retry_delay)
            except requests.HTTPError as exc:
                last_error = exc
                if attempt == max_attempts - 1:
                    break
                print(
                    f"Attempt {attempt + 1} failed with API error: {exc}. "
                    f"Retrying in {self.retry_delay} seconds..."
                )
                time.sleep(self.retry_delay)
            except Exception as exc:
                raise RuntimeError(
                    f"Gemini request failed unexpectedly for {self.model_type}: {exc}"
                ) from exc

        error_body = ""
        if isinstance(last_error, requests.HTTPError) and last_error.response is not None:
            error_body = last_error.response.text[:1200]

        raise RuntimeError(
            f"Gemini request failed after {max_attempts} attempts for "
            f"{self.model_type}: {type(last_error).__name__}: {last_error}"
            f"{' | body=' + error_body if error_body else ''}"
        )
