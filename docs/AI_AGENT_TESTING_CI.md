# AI Agent Testing in CI/CD

If you are looking for **AI agent testing in CI/CD**, the practical problem is not just “does the output look okay?” It is “did my agent behavior change in a way that should block this merge?”

EvalView is built for that workflow.

## What EvalView tests in CI

- tool calls
- tool sequence
- output drift
- cost changes
- latency changes
- safety contracts like `forbidden_tools`

## Recommended workflow

### 1. Generate or capture a suite

Cold start:

```bash
evalview generate --agent http://localhost:8000
evalview snapshot tests/generated --approve-generated
```

Real traffic:

```bash
evalview capture --agent http://localhost:8000/invoke
evalview snapshot
```

### 2. Run regression checks in CI

```bash
evalview check --json --fail-on REGRESSION
```

### 3. Post review comments to the PR

```bash
evalview ci comment --results tests/generated/generated.report.json
```

## Why this matters

Traditional software tests catch code regressions.
EvalView catches **agent behavior regressions**:
- wrong tool
- extra tool
- reordered tool path
- degraded final output
- unsafe capability drift

That is the part most AI teams still do manually.

## Works especially well for

- LangGraph agents
- MCP servers and MCP-based agents
- generic HTTP agents
- tool-calling assistants
- teams shipping agent changes through GitHub Actions

## Related docs

- [CI/CD Integration](CI_CD.md)
- [Golden Traces](GOLDEN_TRACES.md)
- [Test Generation](TEST_GENERATION.md)
