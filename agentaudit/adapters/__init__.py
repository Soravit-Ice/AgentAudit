from agentaudit.adapters.base import BaseAdapter
from agentaudit.adapters.command import CommandAdapter
from agentaudit.adapters.http import HttpAdapter
from agentaudit.adapters.mock import MockAdapter
from agentaudit.exceptions import ConfigurationError
from agentaudit.models import TargetConfig


def get_adapter(config: TargetConfig) -> BaseAdapter:
    """Factory function to load the appropriate target adapter based on the configuration.

    Args:
        config: The TargetConfig Pydantic model.

    Returns:
        An instance of BaseAdapter.

    Raises:
        ConfigurationError: If the target type is unsupported.
    """
    if config.type == "mock":
        return MockAdapter(config)
    elif config.type == "http":
        return HttpAdapter(config)
    elif config.type == "command":
        return CommandAdapter(config)
    else:
        raise ConfigurationError(f"Unsupported target adapter type: {config.type}")


__all__ = [
    "BaseAdapter",
    "MockAdapter",
    "HttpAdapter",
    "CommandAdapter",
    "get_adapter",
]
