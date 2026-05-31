from unittest.mock import AsyncMock, patch

import pytest

from agentaudit.adapters.http import HttpAdapter
from agentaudit.exceptions import AdapterError
from agentaudit.models import TargetConfig


@pytest.mark.asyncio
async def test_http_adapter_success() -> None:
    config = TargetConfig(
        type="http",
        url="http://mockservice/chat",
        output_key="answer",
        sources_key="docs",
    )

    mock_response = AsyncMock()
    mock_response.status_code = 200
    mock_response.json = lambda: {
        "answer": "Standard shipping takes 3-5 business days.",
        "docs": ["shipping_policy.md"],
    }
    mock_response.raise_for_status = AsyncMock()

    adapter = HttpAdapter(config)

    with patch("httpx.AsyncClient.post", return_value=mock_response) as mock_post:
        output, sources, latency = await adapter.execute("Shipping duration?")

        assert output == "Standard shipping takes 3-5 business days."
        assert sources == ["shipping_policy.md"]
        assert latency >= 0.0

        # Verify AsyncClient called post with correct parameters
        mock_post.assert_called_once()
        call_kwargs = mock_post.call_args[1]
        assert call_kwargs["json"] == {"input": "Shipping duration?"}


@pytest.mark.asyncio
async def test_http_adapter_error_handling() -> None:
    config = TargetConfig(type="http", url="http://mockservice/chat")

    adapter = HttpAdapter(config)

    # Simulate network connection failure
    with patch("httpx.AsyncClient.post", side_effect=Exception("Connection refused")):
        with pytest.raises(AdapterError) as exc_info:
            await adapter.execute("Prompt")
        assert "execution failed" in str(exc_info.value)
