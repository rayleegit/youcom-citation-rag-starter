import unittest

from youcom_citation_rag.grounding import build_grounded_result, normalize_web_results, validate_citations


class GroundingTests(unittest.TestCase):
    def test_normalizes_and_deduplicates_domains(self):
        results = [
            {"title": "A", "url": "https://example.com/a", "snippets": ["Alpha."]},
            {"title": "B", "url": "https://www.example.com/b", "snippets": ["Beta."]},
            {"title": "C", "url": "https://docs.you.com/c", "snippets": ["Gamma."]},
        ]

        sources = normalize_web_results(results, max_sources=2)

        self.assertEqual([source.domain for source in sources], ["example.com", "docs.you.com"])

    def test_fills_from_same_domain_when_needed(self):
        results = [
            {"title": "A", "url": "https://example.com/a", "snippets": ["Alpha."]},
            {"title": "B", "url": "https://www.example.com/b", "snippets": ["Beta."]},
        ]

        sources = normalize_web_results(results, max_sources=2)

        self.assertEqual([source.title for source in sources], ["A", "B"])

    def test_validates_missing_citations(self):
        missing = validate_citations("Answer [1] [4]", normalize_web_results([
            {"title": "A", "url": "https://example.com/a", "snippets": ["Alpha."]},
        ]))

        self.assertEqual(missing, [4])

    def test_builds_grounded_result(self):
        result = build_grounded_result("What is You.com?", [
            {"title": "You.com Docs", "url": "https://you.com/docs", "snippets": ["You.com supports grounded AI apps."]}
        ])

        self.assertIn("[1]", result.answer)
        self.assertEqual(result.missing_citations, [])


if __name__ == "__main__":
    unittest.main()
