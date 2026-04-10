"""
LLM client for QUGEN. Paper uses Llama-3-70b-instruct; we support OpenAI-compatible API.
"""

from __future__ import annotations

import os
from abc import ABC, abstractmethod
from typing import Any

# Optional: use OPENAI_API_BASE for local/vendor Llama endpoints
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")
OPENAI_API_BASE = os.getenv("OPENAI_API_BASE", None)  # e.g. "https://.../v1"
# Default: gpt-5.4-nano khi dùng Responses API; hoặc gpt-4o-mini cho Chat Completions
USE_RESPONSES_API = os.getenv("OPENAI_USE_RESPONSES_API", "1").strip().lower() in ("1", "true", "yes")
MODEL_NAME = os.getenv("QUGEN_LLM_MODEL", "gpt-5.4-mini" if USE_RESPONSES_API else "gpt-4o-mini")


class BaseLLMClient(ABC):
    @abstractmethod
    def complete(
        self,
        prompt: str,
        *,
        temperature: float = 1.0,
        max_tokens: int = 2048,
        stop: list[str] | None = None,
    ) -> str:
        """Return single completion text."""
        pass

    def complete_multi(
        self,
        prompt: str,
        num_samples: int = 1,
        temperature: float = 1.0,
        max_tokens: int = 2048,
        stop: list[str] | None = None,
    ) -> list[str]:
        """Return multiple independent samples (for s samples per iteration)."""
        return [
            self.complete(prompt, temperature=temperature, max_tokens=max_tokens, stop=stop)
            for _ in range(num_samples)
        ]


class OpenAICompatibleClient(BaseLLMClient):
    """OpenAI API: Responses API (responses.create + output_text) hoặc Chat Completions."""

    def __init__(
        self,
        model: str | None = None,
        api_key: str | None = None,
        base_url: str | None = None,
        use_responses_api: bool | None = None,
    ):
        self.model = model or MODEL_NAME
        self._api_key = api_key or OPENAI_API_KEY
        self._base_url = base_url or OPENAI_API_BASE
        self._use_responses_api = use_responses_api if use_responses_api is not None else USE_RESPONSES_API

    def _get_client(self):
        try:
            from openai import OpenAI
        except ImportError:
            raise ImportError("Install openai: pip install openai")
        client_kw: dict[str, Any] = {}
        if self._api_key:
            client_kw["api_key"] = self._api_key
        if self._base_url:
            client_kw["base_url"] = self._base_url
        return OpenAI(**client_kw)

    def complete(
        self,
        prompt: str,
        *,
        temperature: float = 1.0,
        max_tokens: int = 2048,
        stop: list[str] | None = None,
    ) -> str:
        client = self._get_client()

        if self._use_responses_api and hasattr(client, "responses"):
            # OpenAI Responses API: client.responses.create(model=..., input=..., store=...)
            # Một số model (vd gpt-5-nano) không hỗ trợ temperature → không gửi nếu không cần
            kwargs: dict[str, Any] = {
                "model": self.model,
                "input": prompt,
                "store": False,
            }
            # Model reasoning tốn token → cần đủ token cho cả reasoning + output (tối thiểu 8192)
            kwargs["max_output_tokens"] = max(max_tokens or 2048, 8192)
            resp = client.responses.create(**kwargs)
            text = getattr(resp, "output_text", None) or ""
            if not (text and text.strip()) and getattr(resp, "output", None):
                # Fallback: gom text từ output (message items với content type output_text)
                parts = []
                for item in (resp.output or []):
                    if getattr(item, "type", None) == "message" and getattr(item, "content", None):
                        for c in (item.content or []):
                            if getattr(c, "type", None) == "output_text" and getattr(c, "text", None):
                                parts.append(c.text)
                text = "\n".join(parts)
            return (text or "").strip()
        else:
            # Chat Completions API (fallback)
            kwargs = {
                "model": self.model,
                "messages": [{"role": "user", "content": prompt}],
                "temperature": temperature,
                "max_tokens": max_tokens,
            }
            if stop:
                kwargs["stop"] = stop
            resp = client.chat.completions.create(**kwargs)
            return (resp.choices[0].message.content or "").strip()


class MockLLMClient(BaseLLMClient):
    """Mock LLM for dry-run: returns fixed Insight Cards (no API key needed)."""

    # Sample output for transactions-like schema (Vietnamese)
    SAMPLE_INSIGHT_RESPONSE = """
[INSIGHT]
REASON: Phân tích xu hướng doanh thu theo thời gian giúp đánh giá hiệu quả kinh doanh.
QUESTION: Doanh thu thay đổi như thế nào theo từng tháng trong năm?
BREAKDOWN: Tháng
MEASURE: SUM(Thành Tiền)
[/INSIGHT]

[INSIGHT]
REASON: So sánh doanh thu theo khu vực để xác định thị trường trọng điểm.
QUESTION: Khu vực (quận/huyện) nào có tổng doanh thu cao nhất?
BREAKDOWN: Khu Vực (Quận/Huyện)
MEASURE: SUM(Thành Tiền)
[/INSIGHT]

[INSIGHT]
REASON: Phân khúc khách hàng ảnh hưởng đến doanh thu và biên lợi nhuận.
QUESTION: Doanh thu trung bình và biên lợi nhuận khác nhau thế nào giữa các phân khúc sản phẩm?
BREAKDOWN: Phân khúc sản phẩm
MEASURE: MEAN(Thành Tiền)
[/INSIGHT]

[INSIGHT]
REASON: Tỷ lệ giao hàng trễ và khiếu nại phản ánh chất lượng dịch vụ.
QUESTION: Tỷ lệ giao dịch có giao hàng trễ hoặc khiếu nại theo từng tỉnh/thành phố?
BREAKDOWN: Tỉnh / Thành Phố_x
MEASURE: COUNT(*)
[/INSIGHT]
"""

    def complete(
        self,
        prompt: str,
        *,
        temperature: float = 1.0,
        max_tokens: int = 2048,
        stop: list[str] | None = None,
    ) -> str:
        if "[STAT]" in prompt or "statistical" in prompt.lower():
            return "[STAT] Số lượng giao dịch trong bảng? [/STAT]\n[STAT] Các tỉnh/thành có giao dịch? [/STAT]"
        return self.SAMPLE_INSIGHT_RESPONSE.strip()


def get_default_llm_client(use_mock: bool = False) -> BaseLLMClient:
    """Return default LLM client. use_mock=True for dry-run without API key."""
    if use_mock:
        return MockLLMClient()
    return OpenAICompatibleClient()
