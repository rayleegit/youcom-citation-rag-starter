# You.com Citation RAG Starter

A compact starter project for building grounded AI answers with the You.com Search API.

I built this as a small DevRel-style starter: fetch live web results, turn them into numbered source context, draft a short answer, and check that every citation points back to something the app actually retrieved.

## Why this exists

Most RAG demos stop right when things get interesting. This one keeps going into the parts I usually want when I am deciding whether an example is shippable:

- Live web retrieval through You.com Search
- Source IDs that map cleanly to URLs
- Domain variety when it is available
- Offline fixtures for demos, tests, and workshops
- A citation check after the answer is generated

## Quickstart

```bash
python -m venv .venv
source .venv/bin/activate
python -m pip install -e .
```

Run with the included fixture:

```bash
you-rag "What does You.com provide for grounded AI apps?" --fixture examples/sample_results.json
```

Run against the live You.com Search API:

```bash
export YDC_API_KEY="your-api-key"
you-rag "latest research on agentic search UX" --count 5
```

## Environment

Copy `.env.example` if you want a local env file:

```bash
cp .env.example .env
```

Required for live search:

```text
YDC_API_KEY=...
```

## Project Layout

```text
src/youcom_citation_rag/search_client.py  You.com Search API client
src/youcom_citation_rag/grounding.py      Citation context and validation logic
src/youcom_citation_rag/cli.py            Demo CLI
examples/sample_results.json              Offline sample response
tests/test_grounding.py                   Unit tests
```

## What This Shows

This is intentionally small enough to read in a few minutes. The point is to show the shape of a useful technical asset, not bury the idea under framework code:

- Clear onboarding path
- Working code with offline demo mode
- API usage tied to a real product surface
- Practical defaults instead of a giant abstraction
- Testable citation behavior

## License

MIT
