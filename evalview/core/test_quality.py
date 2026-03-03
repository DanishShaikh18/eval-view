"""Test quality scoring — gates test execution on test case quality.

A test result is only meaningful if the test itself is well-written.
This module scores test cases before they run and filters out low-quality
ones so users see clean agent performance scores, not noise from bad tests.
"""

from typing import List, Tuple, TYPE_CHECKING

if TYPE_CHECKING:
    from evalview.core.types import TestCase

# Quality threshold: tests below this score are skipped and not run
QUALITY_THRESHOLD = 50

# Fragment endings that indicate a truncated, incomplete query
_FRAGMENT_ENDINGS = (
    " for", " the", " a", " an", " of", " in", " on",
    " to", " with", " and", " or",
)


def score_test_quality(tc: "TestCase") -> Tuple[int, List[str]]:
    """Score a test case for quality (0-100). Return (score, issues).

    Scoring breakdown:
      Query quality        — 60 pts  (length, word count, completeness)
      Expectation quality  — 40 pts  (has real expectations, no empty strings)

    Tests below QUALITY_THRESHOLD should not be run — their results
    reflect test problems, not agent problems.
    """
    score = 0
    issues: List[str] = []

    query = (tc.input.query or "").strip()

    # ── Query quality (60 pts) ──────────────────────────────────────────────

    # Length: meaningful queries need substance
    if len(query) >= 15:
        score += 20
    else:
        issues.append(
            f'Query is too short ({len(query)} chars) — '
            'add a specific intent or object '
            '(e.g. "Show me LangSmith pain points" not "Search for")'
        )

    # Word count: at least 3 words
    words = query.split()
    if len(words) >= 3:
        score += 20
    else:
        issues.append(
            f'Query has only {len(words)} word(s) — '
            'a good test query has at least 3 words'
        )

    # Completeness: doesn't end mid-phrase
    if query.lower().endswith(_FRAGMENT_ENDINGS):
        last_word = words[-1] if words else ""
        issues.append(
            f'Query looks truncated — ends with "{last_word}", '
            'which suggests a missing search term or object. '
            f'Edit the query in your test YAML to complete it.'
        )
    else:
        score += 20

    # ── Expectation quality (40 pts) ───────────────────────────────────────

    expected = tc.expected
    has_tools = bool(expected.tools or expected.tool_sequence or expected.tool_categories)
    contains_strings: List[str] = []
    if expected.output and hasattr(expected.output, "contains") and expected.output.contains:
        contains_strings = [s for s in expected.output.contains if s is not None]

    has_real_contains = any(s.strip() for s in contains_strings)
    has_empty_contains = any(s.strip() == "" for s in contains_strings)

    # Has at least one real expectation
    if has_tools or has_real_contains:
        score += 20
    else:
        issues.append(
            'No real expectations defined — add expected.tools or '
            'expected.output.contains with a phrase your agent always outputs'
        )

    # No empty strings in contains (always pass, hide real failures)
    if has_empty_contains:
        issues.append(
            'expected.output.contains has an empty string ("") — '
            'it always passes and hides real failures. '
            'Replace it with an actual phrase from your agent\'s response.'
        )
    else:
        score += 20

    return score, issues
