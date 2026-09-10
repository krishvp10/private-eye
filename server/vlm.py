"""OpenAI-compatible multimodal VLM adapter with explicit mock/real modes."""

import json
import os
from typing import Any, Dict, Optional

import httpx

from server.mock_vlm import MockVLM
from server.prompts import SYSTEM_PROMPT, build_user_message
from server.validation import validate_agent_action
from shared.protocol import AgentAction, ScreenContext


class VLMAdapter:
    def __init__(
        self,
        endpoint_url: Optional[str] = None,
        model_name: Optional[str] = None,
        use_mock: Optional[bool] = None,
        api_key: Optional[str] = None,
        timeout: float = 30.0,
    ) -> None:
        mode = os.getenv("PRIVATEEYE_VLM_MODE", "mock").lower()
        self.mode = "mock" if use_mock is True else ("real" if use_mock is False else mode)
        if self.mode not in {"mock", "real"}:
            raise ValueError("PRIVATEEYE_VLM_MODE must be 'mock' or 'real'")
        self.use_mock = self.mode == "mock"
        self.endpoint_url = (endpoint_url or os.getenv(
            "PRIVATEEYE_VLM_BASE_URL", os.getenv("PE_VLLM_URL", "http://localhost:8000/v1")
        )).rstrip("/")
        self.model_name = model_name or os.getenv(
            "PRIVATEEYE_VLM_MODEL", os.getenv("PE_VLM_MODEL", "Qwen/Qwen2.5-VL-7B-Instruct")
        )
        self.api_key = api_key if api_key is not None else os.getenv("PRIVATEEYE_VLM_API_KEY", "")
        self.timeout = timeout
        self.mock_fallback = MockVLM()

    def build_request(self, context: ScreenContext) -> Dict[str, Any]:
        redaction_summary = "\n".join(
            f"- Region {r.region}: {r.category.value.upper()} masked via {r.method.value}"
            for r in context.redactions
        ) or "None (Clean screen)"
        return {
            "model": self.model_name,
            "messages": [
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": [
                    {"type": "text", "text": build_user_message(
                        task=context.task,
                        url=context.url,
                        screen_graph_json=context.screen_graph.model_dump_json(),
                        redaction_summary=redaction_summary,
                    )},
                    {"type": "image_url", "image_url": {
                        "url": f"data:image/jpeg;base64,{context.image_b64}"
                    }},
                ]},
            ],
            "temperature": 0.0,
            "response_format": {"type": "json_object"},
        }

    @staticmethod
    def parse_response(data: Dict[str, Any]) -> AgentAction:
        try:
            content = data["choices"][0]["message"]["content"]
            if isinstance(content, list):
                content = next(part["text"] for part in content if part.get("type") == "text")
            if not isinstance(content, str) or not content.strip():
                raise ValueError("Model returned an empty response")
            return validate_agent_action(json.loads(content))
        except Exception as exc:
            raise ValueError(f"Malformed VLM response: {exc}") from exc

    async def analyze(self, context: ScreenContext) -> AgentAction:
        if self.use_mock:
            return self.mock_fallback.analyze(context)
        headers = {"Authorization": f"Bearer {self.api_key}"} if self.api_key else {}
        async with httpx.AsyncClient(timeout=self.timeout) as client:
            response = await client.post(
                f"{self.endpoint_url}/chat/completions",
                json=self.build_request(context),
                headers=headers,
            )
            response.raise_for_status()
            return self.parse_response(response.json())
