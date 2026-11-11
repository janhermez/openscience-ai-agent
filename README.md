# OpenScience AI Agent

**A local-first Python AI agent for exploring scholarly publications and checking metadata completeness.**

> **Status:** MVP / proof of concept. This is an independent portfolio project, not an official service of the University of Warsaw, ICM UW, or Biblioteka Nauki.

## Why this project?

Scholarly metadata can contain missing or inconsistent fields. Checking records manually does not scale well, while a language model may produce plausible but incorrect details.

This prototype explores a practical separation of responsibilities:

- **Deterministic Python rules** identify selected missing metadata fields.
- **An LLM agent** uses explicit tools to search publications and request metadata-quality checks.
- **Public OpenAlex data or synthetic examples** make it possible to experiment without access to institutional infrastructure.

The goal is to test where an LLM adds value beyond conventional validation rules, not to assume that an LLM is always the better solution.

## Implemented features

| Feature | Status |
| --- | --- |
| REST API with FastAPI and interactive `/docs` | Implemented |
| `GET /api/search` — search synthetic examples or OpenAlex | Implemented |
| `POST /api/quality` — rule-based metadata completeness checks | Implemented |
| `POST /api/ask` — LLM agent with two callable tools and a call limit | Implemented (optional LLM setup) |
| Local Ollama model (`qwen3:4b`) | Supported |
| Docker-based development setup | Available |
| Offline pytest tests and GitHub Actions CI | Available |
| Systematic LLM evaluation / benchmark metrics | Not implemented yet |
| RAG, deduplication, admin UI | Not implemented |

**Core tools:** publication search and metadata-quality assessment. The agent uses function/tool calling rather than only generating an answer from a prompt.

## Tech stack

**Python 3.11+ · FastAPI · pytest · Docker · Ollama · Qwen3 · OpenAlex API · GitHub Actions**

## How it works

```text
                    Client / HTTP request
                             |
                         FastAPI
                   /api/search | /api/quality
                             |      (direct API calls)
                             |
                          /api/ask
                             |
                     LLM agent (optional)
                             |
                       tool calling
                        /       \
             publication search  quality assessment
                     |                  |
             synthetic records     Python rules
                or OpenAlex
```

The default data source is synthetic test data. OpenAlex mode is optional and uses a public external API.

## Quick start: offline API demo

**Requirements:** Docker with Docker Compose, or Python 3.11+ for a local installation.

```bash
git clone https://github.com/janhermez/openscience-ai-agent.git
cd openscience-ai-agent
cp .env.example .env
docker compose up --build -d
```

Open **http://127.0.0.1:8000/docs** to explore the API.

Search the synthetic examples:

```bash
curl 'http://127.0.0.1:8000/api/search?query=kubernetes'
```

Run a deterministic metadata check (no LLM required):

```bash
curl -s -X POST 'http://127.0.0.1:8000/api/quality' \
  -H 'Content-Type: application/json' \
  -d '{"id":"demo","title":"Sample article","publication_year":2025,"doi":null,"authors":["A. Nowak"],"abstract":null,"source":"manual"}'
```

## Run the AI agent locally with Ollama

Set the following values in your local `.env`:

```env
LLM_PROVIDER=ollama
OLLAMA_MODEL=qwen3:4b
OLLAMA_BASE_URL=http://ollama:11434/v1
```

Then start the services and download the local model:

```bash
docker compose up -d --build
docker compose exec ollama ollama pull qwen3:4b
```

Try a tool-using request:

```bash
curl -s -X POST 'http://127.0.0.1:8000/api/ask' \
  -H 'Content-Type: application/json' \
  -d '{"question":"Find publications about Kubernetes and assess their metadata completeness."}'
```

The model runs locally through Ollama; **no paid LLM API key is required** for this setup. The model must be downloaded before the agent can use it. An optional external OpenAI API provider is also supported, but may incur charges.

**Important:** Do not expose the unauthenticated agent endpoint or Ollama service to the public internet.

## Use live OpenAlex data

Set `DATA_BACKEND=openalex` in `.env` and restart the application. You may also configure `OPENALEX_API_KEY` if required by your OpenAlex account or current API limits.

The app will then query the external OpenAlex API instead of its synthetic default examples. Use only public, permitted data and respect the API's policies and limits.

- [OpenAlex API documentation](https://docs.openalex.org/)

## Run without Docker

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
cp .env.example .env
uvicorn app.main:app --reload
```

Use a supported Python version; some older Linux distributions ship an older Python by default. Local LLM inference still requires a separately configured compatible model service.

## Tests and engineering practices

```bash
pytest -q
python -m compileall -q app
```

The current tests run offline and exercise application/API and deterministic validation behavior. GitHub Actions provides CI. **These tests do not establish the accuracy or reliability of the LLM agent.**

## Known limitations

- The metadata quality score is a simplified **completeness heuristic**, not an assessment of a publication's scientific merit.
- Missing DOIs and abstracts can be legitimate for certain record types.
- LLM output may contain fabricated or malformed identifiers; publication metadata must be checked against source records before being trusted.
- No systematic evaluation dataset, precision/recall/F1 results, or latency/cost benchmark has been published yet.
- Deduplication, RAG, user authentication, rate limiting, and a production deployment are out of scope for the current MVP.
- External metadata is untrusted input, not an instruction source for the agent.

## Next steps

1. Add a small, annotated evaluation set with reproducible test questions and expected results.
2. Check DOI formatting and ensure that identifiers in answers match the retrieved source records.
3. Compare **rules-only**, **LLM-only**, and **hybrid** approaches using documented metrics and error cases.
4. Improve error handling, observability, and API tests.
5. Add more metadata checks only when supported by real use cases.

## Project independence and responsible use

This is a personal learning and portfolio project based on synthetic data and publicly accessible interfaces. It does not access employer systems or use confidential institutional data. Secrets belong in a local `.env` file and must never be committed to the repository.

A potential research study of metadata quality is a future direction, not a claim that a thesis or scientific evaluation has already been completed.
