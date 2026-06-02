class AgentAuditError(Exception):
    """Base exception for all AgentAudit errors."""

    pass


class ConfigurationError(AgentAuditError):
    """Raised when there is an issue loading or parsing configurations/YAML files."""

    pass


class AdapterError(AgentAuditError):
    """Raised when an adapter fails to execute or communicate with a target."""

    pass


class EvaluationError(AgentAuditError):
    """Raised when scoring or RAG evaluations encounter problems."""

    pass
