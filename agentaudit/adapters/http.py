import time
from typing import Any

import httpx

from agentaudit.adapters.base import BaseAdapter
from agentaudit.exceptions import AdapterError


class HttpAdapter(BaseAdapter):
    """An HTTP adapter to call live endpoints (e.g. Chatbots, RAG APIs, flow runners)."""

    async def execute(self, input_text: str) -> tuple[str, list[str] | None, float]:
        if not self.config.url:
            raise AdapterError("HTTP Adapter configuration requires 'url' parameter.")

        url = self.config.url
        method = self.config.method or "POST"
        headers = self.config.headers or {}
        input_key = self.config.input_key or "input"
        output_key = self.config.output_key or "output"
        sources_key = self.config.sources_key or "sources"

        start_time = time.perf_counter()

        try:
            async with httpx.AsyncClient() as client:
                if method.upper() == "GET":
                    params = {input_key: input_text}
                    response = await client.get(url, params=params, headers=headers, timeout=30.0)
                else:
                    payload = {input_key: input_text}
                    response = await client.post(url, json=payload, headers=headers, timeout=30.0)

                response.raise_for_status()
                data = response.json()
        except httpx.HTTPStatusError as e:
            raise AdapterError(f"HTTP request failed with status {e.response.status_code}: {e.response.text}") from e
        except Exception as e:
            raise AdapterError(f"HTTP request execution failed: {e}") from e

        latency_ms = (time.perf_counter() - start_time) * 1000.0

        if not isinstance(data, dict):
            raise AdapterError(f"Expected a JSON dictionary response from target, but received: {type(data)}")

        # Retrieve output and sources keys (supporting nested dicts with dot notation)
        def _get_value(d: dict[str, Any], key_path: str) -> Any:
            parts = key_path.split(".")
            val: Any = d
            for part in parts:
                if isinstance(val, dict) and part in val:
                    val = val[part]
                else:
                    return None
            return val

        output_text = _get_value(data, output_key)
        if output_text is None:
            # Fallback to direct key
            output_text = data.get(output_key)

        if output_text is None:
            raise AdapterError(f"Output key '{output_key}' not found in the response body: {data}")

        sources = _get_value(data, sources_key)
        if sources is None:
            sources = data.get(sources_key)

        if sources is not None:
            if isinstance(sources, str):
                sources = [sources]
            elif not isinstance(sources, list):
                sources = []

        return str(output_text), sources, latency_ms
