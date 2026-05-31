# Security Policy

## Responsible Disclosure

We take the security of **AgentAudit** and the systems it evaluates seriously. If you discover a security vulnerability in this toolkit, we appreciate a responsible disclosure.

Please do **NOT** open a public GitHub issue for security vulnerabilities. Instead, report them privately to `security@agentaudit.dev`. We will investigate and respond promptly.

---

## Safety & Secrets Disclaimer

> [!CAUTION]
> **Do not submit real secrets or private customer data in GitHub Issues, Pull Requests, or test suites.**
>
> AgentAudit is a testing utility. Since evaluation configurations and test logs are often stored in version control systems, always use mock credentials, simulated tokens, and synthetic PII inputs (e.g. visa prefix `4111`) for evaluating your applications. Never commit real API keys (e.g. `sk-...` OpenAI keys) or production databases to this repository or your own public test codebases.
