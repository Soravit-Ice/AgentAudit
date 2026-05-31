# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.1.0] - 2026-05-31

### Added
- **Core Models**: Pydantic schemas validating test suites, targets, cases, assertions, and reporting aggregates.
- **CLI Commands**: `init` scaffolding tool, `run` executor, `report` generator, and `version` printer.
- **Pluggable Adapters**:
  - `MockAdapter` simulating target answers, sources, and latencies.
  - `HttpAdapter` asynchronously requesting external API webhooks.
  - `CommandAdapter` securely launching local subprocess commands via async streams and stdin.
- **Deterministic Scorers**: Checks for exact match, contains, exclusions, regex patterns, latencies, and RAG document citations.
- **Thai & English Refusal Heuristics**: Deterministic refusal checks to verify defensive prompt injections without API key dependencies.
- **Safety Packing**: Predefined prompt exfiltration tests in English and Thai.
- **Rich Multi-Format Reports**: Beautiful terminal panels, JSON schemas, Markdown, and custom interactive Glassmorphism HTML dashboards.
- **Developer Workflows**: Multi-stage `Makefile` and GitHub Actions CI pipelines.
