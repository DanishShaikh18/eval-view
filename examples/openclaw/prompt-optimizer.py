"""Autonomous prompt optimizer using EvalView as the quality gate.

Demonstrates the auto-research pattern: try N prompt variants,
use EvalView to evaluate each one, keep the best.

Usage:
    1. Set up your agent with EvalView tests:
       evalview init && evalview snapshot

    2. Run this script:
       python prompt-optimizer.py

    3. The script tries each prompt variant, reverts regressions,
       and keeps the best-performing prompt.
"""
from __future__ import annotations

import sys
from pathlib import Path

from evalview.openclaw import gate_or_revert
from evalview import gate

# ── Configure your variants here ──────────────────────────────────────────────

AGENT_CONFIG = "agent_config.yaml"  # Path to your agent's config file
TEST_DIR = "tests"

PROMPT_VARIANTS = [
    "You are a helpful support agent. Always verify with tools before answering.",
    "You are a precise support agent. Use tools for every question. Never guess.",
    "You are a friendly support agent. Check your tools first, then explain clearly.",
    "You are an efficient support agent. Use the minimum tools needed, answer concisely.",
    "You are a thorough support agent. Cross-check with multiple tools when possible.",
]


# ── Helper ────────────────────────────────────────────────────────────────────

def update_system_prompt(config_path: str, new_prompt: str) -> None:
    """Update the system_prompt field in a YAML config file."""
    path = Path(config_path)
    if not path.exists():
        print(f"Config file not found: {config_path}")
        sys.exit(1)

    content = path.read_text()
    # Simple replacement — works for flat YAML configs
    import re
    updated = re.sub(
        r'(system_prompt:\s*)(["\']).*?\2',
        f'\\1"{new_prompt}"',
        content,
    )
    if updated == content:
        # Try unquoted format
        updated = re.sub(
            r'(system_prompt:\s*).*',
            f'\\1"{new_prompt}"',
            content,
        )
    path.write_text(updated)


# ── Main loop ─────────────────────────────────────────────────────────────────

def main() -> None:
    print(f"Testing {len(PROMPT_VARIANTS)} prompt variants against {TEST_DIR}/\n")

    # Read current prompt as baseline
    results = []

    for i, prompt in enumerate(PROMPT_VARIANTS, 1):
        short = prompt[:60] + "..." if len(prompt) > 60 else prompt
        print(f"[{i}/{len(PROMPT_VARIANTS)}] Trying: {short}")

        update_system_prompt(AGENT_CONFIG, prompt)

        if gate_or_revert(TEST_DIR, quick=True):
            # Passed — measure quality
            result = gate(test_dir=TEST_DIR, quick=True)
            total_score = sum(
                d.score_delta for d in result.diffs
            ) if result.diffs else 0
            passed = result.summary.unchanged
            total = result.summary.total

            results.append((prompt, total_score, passed, total))
            print(f"  PASS  {passed}/{total} tests, score delta: {total_score:+.1f}\n")
        else:
            results.append((prompt, float("-inf"), 0, 0))
            print(f"  REVERTED — regression detected\n")

    # Pick the winner
    print("=" * 60)
    results.sort(key=lambda r: r[1], reverse=True)

    winner = results[0]
    print(f"\nBest prompt (score delta: {winner[1]:+.1f}):")
    print(f"  {winner[0]}\n")

    # Apply the winner
    update_system_prompt(AGENT_CONFIG, winner[0])
    print(f"Applied to {AGENT_CONFIG}")


if __name__ == "__main__":
    main()
