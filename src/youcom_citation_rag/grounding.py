from __future__ import annotations

import re
from dataclasses import dataclass
from typing import Iterable
from urllib.parse import urlparse


@dataclass(frozen=True)
class Source:
    id: int
    title: str
    url: str
    snippet: str
    domain: str


@dataclass(frozen=True)
class GroundedResult:
    answer: str
    sources: list[Source]
    missing_citations: list[int]


def normalize_web_results(results: Iterable[dict], max_sources: int = 5) -> list[Source]:
    sources: list[Source] = []
    overflow: list[Source] = []
    seen_domains: set[str] = set()

    for item in results:
        url = str(item.get("url", "")).strip()
        if not url:
            continue

        domain = urlparse(url).netloc.replace("www.", "")
        snippets = item.get("snippets") or item.get("snippet") or []
        if isinstance(snippets, str):
            snippet = snippets
        else:
            snippet = " ".join(str(part) for part in snippets[:2])

        candidate = Source(
            id=0,
            title=str(item.get("title", domain)).strip() or domain,
            url=url,
            snippet=collapse_whitespace(snippet),
            domain=domain,
        )
        if domain in seen_domains:
            overflow.append(candidate)
            continue

        seen_domains.add(domain)
        sources.append(candidate)
        if len(sources) >= max_sources:
            break

    if len(sources) < max_sources:
        sources.extend(overflow[: max_sources - len(sources)])

    return [
        Source(id=index, title=source.title, url=source.url, snippet=source.snippet, domain=source.domain)
        for index, source in enumerate(sources, start=1)
    ]


def build_citation_context(sources: list[Source]) -> str:
    return "\n".join(
        f"[{source.id}] {source.title}\nURL: {source.url}\nSnippet: {source.snippet}"
        for source in sources
    )


def build_extractive_answer(query: str, sources: list[Source]) -> str:
    if not sources:
        return f"I could not find enough source material to answer: {query}"

    claims = []
    for source in sources[:3]:
        sentence = first_sentence(source.snippet) or source.title
        claims.append(f"{sentence} [{source.id}]")

    return " ".join(claims)


def validate_citations(answer: str, sources: list[Source]) -> list[int]:
    valid_ids = {source.id for source in sources}
    cited_ids = {int(match) for match in re.findall(r"\[(\d+)\]", answer)}
    return sorted(cited_ids - valid_ids)


def build_grounded_result(query: str, web_results: Iterable[dict], max_sources: int = 5) -> GroundedResult:
    sources = normalize_web_results(web_results, max_sources=max_sources)
    answer = build_extractive_answer(query, sources)
    return GroundedResult(
        answer=answer,
        sources=sources,
        missing_citations=validate_citations(answer, sources),
    )


def collapse_whitespace(value: str) -> str:
    return re.sub(r"\s+", " ", value).strip()


def first_sentence(value: str) -> str:
    match = re.search(r"(.+?[.!?])(?:\s|$)", collapse_whitespace(value))
    return match.group(1) if match else collapse_whitespace(value)
