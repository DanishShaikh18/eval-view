"""Tests for check command edge cases."""

from __future__ import annotations

from click.testing import CliRunner


def test_check_dry_run_handles_golden_metadata_objects(monkeypatch, tmp_path):
    """Dry-run should count baselines by name without hashing metadata models."""
    from evalview.commands.check_cmd import check
    from evalview.core.golden import GoldenMetadata

    project = tmp_path
    monkeypatch.chdir(project)

    tests_dir = project / "tests"
    tests_dir.mkdir()
    (tests_dir / "sample.yaml").write_text(
        "name: sample\ninput:\n  query: hi\nexpected:\n  tools: []\nthresholds:\n  min_score: 0\n",
        encoding="utf-8",
    )

    evalview_dir = project / ".evalview"
    evalview_dir.mkdir()
    (evalview_dir / "config.yaml").write_text(
        "adapter: http\nendpoint: http://example.com\n",
        encoding="utf-8",
    )

    runner = CliRunner()

    monkeypatch.setattr(
        "evalview.commands.check_cmd._cloud_pull",
        lambda store: None,
    )
    monkeypatch.setattr(
        "evalview.commands.check_cmd._load_config_if_exists",
        lambda: None,
    )
    monkeypatch.setattr(
        "evalview.core.golden.GoldenStore.list_golden",
        lambda self: [
            GoldenMetadata(
                test_name="sample",
                blessed_at="2026-03-13T00:00:00Z",
                score=95.0,
            )
        ],
    )

    result = runner.invoke(check, ["tests", "--dry-run"])

    assert result.exit_code == 0
    assert "With baselines: 1" in result.output
