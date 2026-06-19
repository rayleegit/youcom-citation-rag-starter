from __future__ import annotations

import argparse
import sys

from .grounding import build_citation_context, build_grounded_result
from .search_client import YouSearchClient, YouSearchError, load_fixture


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Build a grounded answer with You.com Search API citations.")
    parser.add_argument("query", help="Question or search query to answer.")
    parser.add_argument("--count", type=int, default=5, help="Number of search results to request.")
    parser.add_argument("--fixture", help="Path to an offline You.com-style search fixture.")
    parser.add_argument("--show-context", action="store_true", help="Print the citation context before the answer.")
    args = parser.parse_args(argv)

    try:
        web_results = load_fixture(args.fixture) if args.fixture else YouSearchClient.from_env().search(args.query, args.count)
    except (OSError, ValueError, YouSearchError) as exc:
        print(f"Error: {exc}", file=sys.stderr)
        return 1

    result = build_grounded_result(args.query, web_results, max_sources=args.count)

    if args.show_context:
        print("Citation Context")
        print("================")
        print(build_citation_context(result.sources))
        print()

    print("Answer")
    print("======")
    print(result.answer)
    print()
    print("Sources")
    print("=======")
    for source in result.sources:
        print(f"[{source.id}] {source.title} - {source.url}")

    if result.missing_citations:
        print(f"\nWarning: answer referenced missing citations: {result.missing_citations}", file=sys.stderr)
        return 2
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
