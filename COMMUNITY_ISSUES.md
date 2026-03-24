# Community Issues

Ready-to-create GitHub issues. Create with labels noted on each.

---

## Good First Issues

These are scoped, well-defined tasks ideal for first-time contributors.

### 1. Add CrewAI example — Trip Planner crew
**Labels:** `good first issue`, `help wanted`, `crewai`, `documentation`

Write `examples/crewai/trip-planner.yaml` for the CrewAI Trip Planner example (`crewAI-examples/crews/trip_planner`). 3 agents, search + scraping tools. Test it against the running crew and add to the examples README.

### 2. Add Pydantic AI example — customer support agent
**Labels:** `good first issue`, `help wanted`, `pydantic-ai`, `documentation`

Write an end-to-end example in `examples/pydantic-ai/` showing EvalView testing a Pydantic AI agent with tool calls and structured output. Include test YAML, a minimal agent script, and a README.

### 3. Write "EvalView vs crewai test" comparison doc
**Labels:** `good first issue`, `help wanted`, `crewai`, `documentation`

Run both `crewai test` and `evalview check` on the same crew. Show side-by-side output. Highlight what EvalView catches that `crewai test` doesn't: tool diffs, parameter changes, output similarity, CI integration. Add to `docs/COMPARISONS.md`.

### 4. Write "EvalView vs pydantic_evals" comparison doc
**Labels:** `good first issue`, `help wanted`, `pydantic-ai`, `documentation`

Show how pydantic_evals and EvalView complement each other. pydantic_evals scores, EvalView catches regressions. Side-by-side examples. Add to `docs/COMPARISONS.md`.

### 5. Add Ollama example — local agent with no API keys
**Labels:** `good first issue`, `help wanted`, `documentation`

Write an example showing EvalView testing a fully local agent using Ollama. Zero cloud API keys needed. Demonstrate `--no-judge` mode for free offline regression detection.

### 6. Improve error messages for common adapter failures
**Labels:** `good first issue`, `help wanted`, `dx`

When an adapter fails to connect, the error can be cryptic. Add friendly error messages with fix suggestions for: connection refused, timeout, invalid JSON response, missing API key. Look at `evalview/adapters/http_adapter.py` for the pattern.

### 7. Add `evalview doctor` command
**Labels:** `good first issue`, `help wanted`, `dx`

A diagnostic command that checks: Python version, installed extras (watchdog, etc.), API key availability, golden baselines exist, agent endpoint reachable. Prints a health report. Helps users debug setup issues.

### 8. Add test templates to `evalview init`
**Labels:** `good first issue`, `help wanted`, `dx`

When running `evalview init`, offer template test suites for common agent types: customer support, RAG pipeline, code assistant, search agent. User picks one, gets pre-written YAML tests they can customize.

---

## Help Wanted

Larger tasks that need more context but are well-scoped.

### 9. CrewAI adapter — capture per-agent reasoning steps
**Labels:** `help wanted`, `crewai`, `enhancement`

Parse CrewAI's verbose output to capture agent reasoning (thoughts, plans, tool selection rationale) as trace metadata. Add `verbose: true` option in test YAML. Include reasoning in HTML trace report.

**Files:** `evalview/adapters/crewai_adapter.py`, `evalview/visualization/generators.py`

### 10. CrewAI adapter — support hierarchical process type
**Labels:** `help wanted`, `crewai`, `enhancement`

CrewAI supports `process: hierarchical` where a manager agent delegates to workers. Detect process type from response, capture parent-child task relationships, show delegation tree in diff output.

**Files:** `evalview/adapters/crewai_adapter.py` — `_parse_tasks()`

### 11. Pydantic AI adapter — structured output validation
**Labels:** `help wanted`, `pydantic-ai`, `enhancement`

Pydantic AI agents return typed structured outputs. Add support for validating the output schema matches expectations (not just string contains). Use Pydantic model validation in the test YAML.

### 12. MCP contract drift — auto-detect schema changes
**Labels:** `help wanted`, `mcp`, `enhancement`

When an MCP server updates its tool schemas (parameters added/removed/renamed), detect this as CONTRACT_DRIFT before running tests. Compare current tool schemas against saved schemas from last snapshot.

**Files:** `evalview/adapters/mcp_adapter.py`, `evalview/core/diff.py`

### 13. OpenClaw — auto-research loop example
**Labels:** `help wanted`, `openclaw`, `documentation`

Write an end-to-end example showing an OpenClaw claw that: modifies agent prompts, calls `gate()` to evaluate, reverts on regression, keeps improvements. Demonstrate the autonomous improvement loop.

### 14. CrewAI adapter — streaming support
**Labels:** `help wanted`, `crewai`, `enhancement`

Add SSE/streaming support for CrewAI endpoints so users see agent progress in real time during `evalview run`.

### 15. CrewAI — track cost per agent
**Labels:** `help wanted`, `crewai`, `enhancement`

Parse per-task token counts if CrewAI exposes them (newer versions may). Fall back to proportional distribution. Show per-agent cost in check output.

**Files:** `evalview/adapters/crewai_adapter.py` — `_distribute_metrics_to_steps()`

### 16. Add `evalview export --format openai-evals`
**Labels:** `help wanted`, `enhancement`

Export EvalView test cases to OpenAI Evals format. Enables users to run the same tests in both EvalView and OpenAI's platform. First step toward the agent test format spec.

### 17. Add `evalview import --from pydantic-evals`
**Labels:** `help wanted`, `pydantic-ai`, `enhancement`

Import pydantic_evals datasets as EvalView test cases. Convert cases, expected outputs, and evaluator configs to YAML format.

### 18. Badge — add GitHub Actions step to auto-commit badge
**Labels:** `help wanted`, `ci`, `enhancement`

Create a reusable workflow snippet that auto-commits the updated `.evalview/badge.json` after a check runs in CI. Handle: branch protection, merge conflicts, and avoiding infinite loops.

### 19. Watch mode — Textual TUI upgrade
**Labels:** `help wanted`, `enhancement`

Upgrade `evalview watch` from print-and-scroll to a Textual-based live terminal UI. Show: test list with live status, sparkline trends, scrollable diff viewer. Keep the current simple mode as fallback.

### 20. Interactive HTML report — add filtering and search
**Labels:** `help wanted`, `enhancement`

Add JavaScript interactivity to the HTML report: filterable test table, sortable columns, search/grep across test names and outputs. Currently the report is static HTML.

### 21. Community test registry — seed templates
**Labels:** `help wanted`, `documentation`

Create a `registry/` directory with reusable test suite templates for common agent types: customer support, RAG pipeline, code assistant, search agent, travel planner. Each template includes: YAML tests, expected tool patterns, judge criteria, README.

### 22. Add Vercel AI SDK integration guide
**Labels:** `help wanted`, `documentation`

Write an integration guide for testing Vercel AI SDK agents via EvalView's HTTP adapter. Show how to test tool-calling agents built with AI SDK 6's Agent abstraction. Address the TypeScript → HTTP bridge.

### 23. Add AutoGen/AG2 integration guide
**Labels:** `help wanted`, `documentation`

Write an integration guide for testing AutoGen/AG2 multi-agent conversations with EvalView. Include example YAML tests for group chat agents.

---

## Feature Requests (larger scope)

### 24. Agent Test Format spec
**Labels:** `feature`, `spec`

Publish a formal spec for the YAML test case format and golden baseline JSON format. JSON Schema for validation. Goal: make it an interchange standard other tools can import/export.

### 25. `evalview sweep` — batch evaluation
**Labels:** `feature`, `enhancement`

Evaluate N agent configs against the same test suite, return ranked results. The auto-research primitive: "try 20 prompt variants, tell me which is best."

### 26. Test coverage report
**Labels:** `feature`, `enhancement`

Show which tools, tool combinations, and conversation paths are covered by the test suite vs. which are untested. Help users identify gaps in their regression coverage.
