# EvalView as a Regression Gate for OpenClaw Agents

**The problem:** Your claw modifies agent code autonomously — tweaking prompts, refactoring tools, changing system instructions. Each change looks fine in isolation. But after 20 iterations, the agent silently stopped asking clarifying questions, skipped a safety check, and the output quality drifted. **Nobody was watching.**

EvalView is the automated quality gate. After every change, it checks whether the agent still behaves correctly — tool calls, output quality, safety constraints — and reverts anything that regresses.

## How It Works

```
┌─────────────┐     ┌──────────┐     ┌──────────┐
│  OpenClaw   │────→│ Make     │────→│ EvalView │
│  Claw       │     │ Change   │     │ gate()   │
└─────────────┘     └──────────┘     └────┬─────┘
       ↑                                  │
       │            ┌──────────┐          │
       └────────────│ Revert   │←─── REGRESSION?
                    │ or Keep  │     YES → revert, try again
                    └──────────┘     NO  → continue
```

The claw makes changes. EvalView checks them. Regressions get reverted automatically. Good changes keep going.

## Setup (2 minutes)

### 1. Install the skill

```bash
evalview openclaw install
```

This copies `evalview-gate.md` into your `skills/` directory. Any claw working in this directory will automatically use EvalView after code changes.

### 2. Create baselines

```bash
evalview snapshot
```

Run this once against your working agent. EvalView captures the full execution trace — tool calls, parameters, outputs, cost — as a golden baseline.

### 3. That's it

The claw now has the skill. After every code change, it runs `evalview check`, reads the result, and decides: continue, revert, or accept.

## Three Ways to Integrate

### Option 1: Skill file (zero code)

The installed `evalview-gate.md` skill tells the claw exactly how to use EvalView. The claw calls `evalview check --json`, parses the output, and follows the decision rules:

- `all_passed` → continue
- `has_regressions` → revert with `git checkout -- .`
- `has_tools_changed` → review, accept if intentional
- `has_output_changed` → usually safe, continue

No Python code needed — works with any claw that has bash access.

### Option 2: `gate_or_revert()` (simplest Python)

One function call. Pass or revert. Nothing else.

```python
from evalview.openclaw import gate_or_revert

# After making a code change:
make_code_change()

if not gate_or_revert("tests/", quick=True):
    # Change was reverted — try a different approach
    try_alternative()
```

`gate_or_revert()` runs the full check, and if any regression is found, runs `git checkout -- .` to revert. Returns `True` if safe, `False` if reverted.

Use `quick=True` for sub-second checks with no LLM judge ($0). Perfect for tight loops.

### Option 3: `check_and_decide()` (full control)

Four possible decisions with context:

```python
from evalview.openclaw import check_and_decide, accept_change

decision = check_and_decide("tests/")

if decision.action == "continue":
    # All tests passed — keep going
    pass

elif decision.action == "revert":
    # Regression detected — already reverted
    print(f"Reverted: {decision.reason}")
    try_different_approach()

elif decision.action == "accept":
    # Tools changed but scores improved — intentional improvement
    accept_change(decision)  # Snapshots new baselines
    print(f"Accepted improvement: {decision.reason}")

elif decision.action == "review":
    # Scores declined slightly — not a regression but worth checking
    print(f"Review needed: {decision.reason}")
    # Decide based on context whether to accept or revert
```

## Autonomous Loop Example

A complete prompt optimization loop that uses EvalView as the fitness function:

```python
"""Autonomous prompt optimizer using EvalView as the quality gate."""
from evalview.openclaw import gate_or_revert
from evalview import gate

PROMPT_VARIANTS = [
    "You are a helpful support agent. Always verify with tools before answering.",
    "You are a precise support agent. Use tools for every question. Never guess.",
    "You are a friendly support agent. Check your tools first, then explain clearly.",
]

def update_system_prompt(new_prompt: str) -> None:
    """Write the new system prompt to the agent config."""
    with open("agent_config.yaml", "r") as f:
        config = f.read()
    config = config.replace(
        config.split("system_prompt:")[1].split("\n")[0],
        f' "{new_prompt}"'
    )
    with open("agent_config.yaml", "w") as f:
        f.write(config)

# Try each variant, keep the best one
best_score = 0
best_prompt = None

for prompt in PROMPT_VARIANTS:
    update_system_prompt(prompt)

    if gate_or_revert("tests/", quick=True):
        # Passed — check the score
        result = gate(test_dir="tests/", quick=True)
        avg_score = sum(d.score_delta for d in result.diffs) / len(result.diffs) if result.diffs else 0

        if avg_score > best_score:
            best_score = avg_score
            best_prompt = prompt
            print(f"New best: {prompt[:50]}... (score: {avg_score:+.1f})")
    else:
        print(f"Reverted: {prompt[:50]}... (regression)")

if best_prompt:
    update_system_prompt(best_prompt)
    print(f"\nWinner: {best_prompt}")
```

## CLI Equivalent

Don't want to write Python? Use the CLI:

```bash
# Standard gate check (auto-reverts on regression)
evalview openclaw check

# Strict mode — fail on ANY change
evalview openclaw check --strict

# Don't auto-revert, just report
evalview openclaw check --no-revert

# Check specific test directory
evalview openclaw check --path tests/
```

## Watch Mode for Manual Iteration

When you're iterating on prompts by hand (not in an autonomous loop):

```bash
evalview watch --quick
```

Every file save triggers a check. Sub-second feedback, $0 cost.

## What the Skill File Contains

The `evalview-gate.md` skill (installed to `skills/`) gives the claw:

- **Decision rules**: When to revert, continue, accept, or review
- **Command reference**: All `evalview check` and `evalview snapshot` commands
- **JSON output format**: How to parse the machine-readable results
- **Python API**: Alternative to CLI for tighter integration
- **Guidelines**: Always check after changes, revert fast, snapshot improvements

## Safety Notes

- `gate_or_revert()` defaults to `git checkout -- .` which **discards all uncommitted changes**. Always commit or stash before entering an autonomous loop.
- Use `revert_cmd="git stash"` for a safer alternative: `gate_or_revert("tests/", revert_cmd="git stash")`
- `check_and_decide(auto_revert=False)` disables auto-revert — the claw decides what to do.

## Links

- [EvalView Python API](../../README.md#python-api)
- [EvalView OpenClaw section](../../README.md#openclaw-integration)
- [OpenClaw](https://github.com/openclaw)
- [`evalview/openclaw.py` source](../../evalview/openclaw.py)
