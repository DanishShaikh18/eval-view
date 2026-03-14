"""Tests for run-command onboarding guidance."""

from __future__ import annotations


def test_no_agent_guide_points_to_init_instead_of_stale_examples():
    from evalview.commands.run._cmd import _display_no_agent_guide
    from evalview.commands.run._cmd import console

    with console.capture() as capture:
        _display_no_agent_guide("http://localhost:8090/execute")

    output = capture.get()
    assert "evalview init" in output
    assert "generated-from-init" in output
    assert "demo-agent/agent.py" not in output


def test_run_loader_uses_active_test_path_when_no_path_is_given(monkeypatch, tmp_path):
    from evalview.commands.run._cmd import _load_test_cases, console
    from evalview.core.project_state import ProjectStateStore

    monkeypatch.chdir(tmp_path)
    active_dir = tmp_path / "tests" / "generated-from-init"
    active_dir.mkdir(parents=True)
    (active_dir / "sample.yaml").write_text(
        "name: sample\ninput:\n  query: hi\nexpected:\n  tools: []\nthresholds:\n  min_score: 0\n",
        encoding="utf-8",
    )
    ProjectStateStore().set_active_test_path("tests/generated-from-init")

    cases = _load_test_cases(path=None, pattern="*.yaml", verbose=False, console=console)

    assert cases is not None
    assert [case.name for case in cases] == ["sample"]


def test_run_mode_guidance_mentions_snapshot_and_check():
    from evalview.commands.run._cmd import _print_run_mode_guidance, console
    from evalview.core.types import ExpectedBehavior, TestCase, TestInput, Thresholds

    generated_case = TestCase(
        name="generated",
        input=TestInput(query="hi"),
        expected=ExpectedBehavior(),
        thresholds=Thresholds(min_score=0),
        generated=True,
    )

    with console.capture() as capture:
        _print_run_mode_guidance([generated_case], console)

    output = capture.get()
    assert "evalview run" in output
    assert "evalview snapshot" in output
    assert "evalview" in output
    assert "check" in output
