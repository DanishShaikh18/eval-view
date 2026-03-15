"""Expand command — generate test variations using LLM."""
from __future__ import annotations

import asyncio
import re
from pathlib import Path
from typing import Any, List, Optional

import click

from evalview.commands.shared import console
from evalview.telemetry.decorators import track_command


@click.command("expand")
@click.argument("test_path", type=click.Path(exists=True))
@click.option(
    "--count",
    "-n",
    default=10,
    type=int,
    help="Number of variations to generate per test (default: 10)",
)
@click.option(
    "--output-dir",
    "-o",
    type=click.Path(),
    help="Output directory for generated tests (default: same as input)",
)
@click.option(
    "--edge-cases/--no-edge-cases",
    default=True,
    help="Include edge case variations (default: True)",
)
@click.option(
    "--edge-only",
    is_flag=True,
    help="Only generate edge cases (adversarial, boundary, missing input)",
)
@click.option(
    "--style",
    "-s",
    type=click.Choice(["adversarial", "boundary", "missing-input", "format", "mixed"], case_sensitive=False),
    default=None,
    help="Style of edge cases to generate",
)
@click.option(
    "--test",
    "-t",
    "test_filter",
    default=None,
    help="Expand only this specific test (by name)",
)
@click.option(
    "--focus",
    "-f",
    help="Focus variations on specific aspect (e.g., 'different stock tickers')",
)
@click.option(
    "--dry-run",
    is_flag=True,
    help="Preview generated tests without saving",
)
@track_command("expand", lambda **kw: {"count": kw.get("count"), "edge_cases": kw.get("edge_cases")})
def expand(
    test_path: str,
    count: int,
    output_dir: str,
    edge_cases: bool,
    edge_only: bool,
    style: Optional[str],
    test_filter: Optional[str],
    focus: str,
    dry_run: bool,
) -> None:
    """Expand test cases into variations using LLM.

    Accepts a single YAML file or a directory of test cases. When given a
    directory, expands every test (or use --test to pick one).

    \b
    Examples:
        evalview expand tests/stock-basic.yaml --count 20
        evalview expand tests/                              # batch: all tests
        evalview expand tests/ --test "weather-lookup"      # one test in dir
        evalview expand tests/ --edge-only --style adversarial
    """
    asyncio.run(_expand_async(
        test_path, count, output_dir, edge_cases, edge_only, style, test_filter, focus, dry_run
    ))


async def _expand_async(
    test_path_str: str,
    count: int,
    output_dir: Optional[str],
    edge_cases: bool,
    edge_only: bool,
    style: Optional[str],
    test_filter: Optional[str],
    focus: Optional[str],
    dry_run: bool,
) -> None:
    """Async implementation of expand command."""
    from evalview.expander import TestExpander
    from evalview.core.loader import TestCaseLoader
    from rich.table import Table

    test_path = Path(test_path_str)

    # Load test(s) — single file or directory
    base_tests: List[Any] = []
    if test_path.is_dir():
        loader = TestCaseLoader()
        all_tests = loader.load_from_directory(test_path)
        if test_filter:
            base_tests = [tc for tc in all_tests if tc.name == test_filter]
            if not base_tests:
                console.print(f"[red]No test found with name: {test_filter}[/red]")
                return
        else:
            base_tests = all_tests
    else:
        loaded = TestCaseLoader.load_from_file(test_path)
        if not loaded:
            console.print(f"[red]No test cases found in {test_path_str}[/red]")
            return
        base_tests = [loaded]

    console.print(f"[blue]🔄 Expanding {len(base_tests)} test(s)...[/blue]\n")

    # Build the focus/style hint
    effective_focus = focus or ""
    if edge_only or style:
        style_label = style or "mixed"
        style_hints = {
            "adversarial": "adversarial inputs: prompt injection, conflicting instructions, malicious payloads",
            "boundary": "boundary conditions: max/min values, empty strings, very long inputs, special characters",
            "missing-input": "missing or incomplete inputs: no required fields, partial data, null values",
            "format": "format edge cases: wrong data types, unexpected encodings, mixed languages",
            "mixed": "edge cases: adversarial, boundary, missing-input, and format variations",
        }
        edge_hint = style_hints.get(style_label, style_hints["mixed"])
        effective_focus = f"{effective_focus}. Focus on {edge_hint}".strip(". ")

    if edge_only:
        edge_cases = True

    # Initialize expander
    try:
        expander = TestExpander()
    except ValueError as e:
        console.print(f"[red]{e}[/red]")
        return

    if expander.message:
        console.print(f"[yellow]{expander.message}[/yellow]")
    console.print(f"[dim]Using {expander.provider.capitalize()} for test generation[/dim]\n")

    all_variations: List[Any] = []
    all_test_cases: List[Any] = []

    for base_test in base_tests:
        console.print(f"[cyan]🤖 {base_test.name}[/cyan] — generating {count} variations...")

        try:
            variations = await expander.expand(
                base_test,
                count=count,
                include_edge_cases=edge_cases,
                variation_focus=effective_focus or None,
            )
        except Exception as e:
            console.print(f"  [red]Failed: {e}[/red]")
            continue

        if not variations:
            console.print("  [yellow]No variations generated[/yellow]")
            continue

        # If edge_only, filter to edge cases
        if edge_only:
            variations = [v for v in variations if v.get("is_edge_case", True)]

        test_cases = [
            expander.convert_to_test_case(v, base_test, i)
            for i, v in enumerate(variations, 1)
        ]

        console.print(f"  [green]✓[/green] {len(variations)} variations")
        all_variations.extend(zip(variations, [base_test] * len(variations)))
        all_test_cases.extend(test_cases)

    if not all_test_cases:
        console.print("\n[yellow]No variations generated[/yellow]")
        return

    console.print(f"\n[green]✓[/green] {len(all_test_cases)} total variations\n")

    # Show preview table
    table = Table(title="Generated Test Variations", show_header=True, header_style="bold cyan")
    table.add_column("#", style="dim", width=3)
    table.add_column("Name", style="white", no_wrap=False)
    table.add_column("Query", style="dim", no_wrap=False)
    table.add_column("Edge?", style="yellow", justify="center", width=5)

    for i, tc in enumerate(all_test_cases, 1):
        variation_dict = all_variations[i - 1][0]
        is_edge = "⚠️" if variation_dict.get("is_edge_case") else ""
        query_preview = tc.input.query[:50] + "..." if len(tc.input.query) > 50 else tc.input.query
        table.add_row(str(i), tc.name, query_preview, is_edge)
        if i >= 30:
            table.add_row("...", f"... and {len(all_test_cases) - 30} more", "", "")
            break

    console.print(table)
    console.print()

    if dry_run:
        console.print("[yellow]Dry run — no files saved[/yellow]")
        return

    if not click.confirm("Save these test variations?", default=True):
        console.print("[yellow]Cancelled[/yellow]")
        return

    # Determine output directory
    if output_dir:
        out_path = Path(output_dir)
    else:
        out_path = test_path if test_path.is_dir() else test_path.parent

    # Generate prefix
    if len(base_tests) == 1:
        prefix = re.sub(r'[^a-z0-9]+', '-', base_tests[0].name.lower()).strip('-')[:20]
        prefix = f"{prefix}-var"
    else:
        prefix = "expanded"

    # Save variations
    console.print(f"\n[cyan]💾 Saving to {out_path}/...[/cyan]")
    saved_paths = expander.save_variations(all_test_cases, out_path, prefix=prefix)

    console.print(f"\n[green]✅ Saved {len(saved_paths)} test variations:[/green]")
    for path in saved_paths[:5]:
        console.print(f"   • {path.name}")
    if len(saved_paths) > 5:
        console.print(f"   • ... and {len(saved_paths) - 5} more")

    console.print(f"\n[blue]Run with:[/blue] evalview run {out_path} --pattern '{prefix}*.yaml'")
