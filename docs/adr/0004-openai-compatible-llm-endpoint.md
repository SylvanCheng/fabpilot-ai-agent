# ADR-0004: LLM behind an OpenAI-compatible endpoint

- Status: Accepted
- Date: 2026-11-02

## Context
Data must stay self-hosted. Models run on rented cloud GPUs: Ollama for quick development, vLLM
for throughput. Model choice (Qwen family today) will change.

## Decision
The backend talks to any OpenAI-compatible `/v1` endpoint. Provider, URL, model and key are
`LLM_*` env vars. Code depends on the `ChatModel` port in `modules/llm`, never on a vendor SDK
directly.

## Consequences
Dev → prod and model upgrades are config changes. Vendor-specific features (e.g. guided decoding
options) must be exposed through the port deliberately.
