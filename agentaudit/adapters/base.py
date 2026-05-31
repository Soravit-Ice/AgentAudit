import abc

from agentaudit.models import TargetConfig


class BaseAdapter(abc.ABC):
    """Abstract base class for all AgentAudit target adapters."""

    def __init__(self, config: TargetConfig):
        self.config = config

    @abc.abstractmethod
    async def execute(self, input_text: str) -> tuple[str, list[str] | None, float]:
        """Executes the test case input against the target.

        Args:
            input_text: The user prompt or message input.

        Returns:
            A tuple of (output_text, list_of_sources, latency_ms)
        """
        pass
