# EvalView vs LangSmith

If you are comparing **EvalView vs LangSmith**, the key distinction is simple:

- **LangSmith** is strongest for agent observability, debugging, prompt workflows, and the broader LangChain / LangGraph ecosystem.
- **EvalView** is strongest for regression testing: generate tests, snapshot agent behavior, diff tool paths, and block regressions in CI/CD.

## Choose LangSmith when

- you want trace collection and debugging dashboards
- you are already deep in LangChain or LangGraph
- you want a broader platform for prompt iteration and agent development

## Choose EvalView when

- you need **AI agent regression testing**
- you want **golden baseline testing for agents**
- you care about tool-call, sequence, output, cost, and latency diffs
- you want to generate a draft regression suite from a live agent or logs
- you need a lightweight CI gate instead of a larger platform decision

## Best fit together

Many teams can use both:
- LangSmith for observability and development traces
- EvalView for regression gating before merge or deploy

## EvalView advantage

EvalView’s strongest differentiator is:

```bash
evalview generate --agent http://localhost:8000
evalview snapshot tests/generated --approve-generated
evalview check tests/generated
```

That is a very different workflow from general trace observability. It is purpose-built for catching broken agent behavior before production.
