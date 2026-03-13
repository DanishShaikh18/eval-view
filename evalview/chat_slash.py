"""Slash command metadata and UI helpers for the chat interface."""

from __future__ import annotations

import sys
from typing import Optional

from prompt_toolkit.completion import Completer, Completion
from rich.console import Console

SLASH_COMMANDS = [
    ("/run", "Run a test case against its adapter"),
    ("/test", "Quick ad-hoc test against an adapter"),
    ("/skill", "Test Claude Code skills with real agents"),
    ("/compare", "Compare two test runs side by side"),
    ("/adapters", "List available adapters"),
    ("/trace", "Trace LLM calls in a Python script"),
    ("/traces", "List and query stored traces"),
    ("/model", "Switch to a different model"),
    ("/docs", "Open EvalView documentation"),
    ("/cli", "Show CLI commands cheatsheet"),
    ("/permissions", "Show auto-allowed commands"),
    ("/context", "Show project status"),
    ("/help", "Show help and tips"),
    ("/clear", "Clear chat history"),
    ("/exit", "Leave chat"),
]


def show_slash_menu(console: Console, selected: int = 0) -> Optional[str]:
    """Show slash command dropdown and let user select."""
    import termios
    import tty

    def get_key() -> str:
        fd = sys.stdin.fileno()
        old_settings = termios.tcgetattr(fd)
        try:
            tty.setraw(fd)
            ch = sys.stdin.read(1)
            if ch == "\x1b":
                ch2 = sys.stdin.read(1)
                ch3 = sys.stdin.read(1)
                if ch2 == "[":
                    if ch3 == "A":
                        return "up"
                    if ch3 == "B":
                        return "down"
                return "esc"
            return ch
        finally:
            termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)

    while True:
        for _ in range(len(SLASH_COMMANDS) + 1):
            console.file.write("\033[F\033[K")

        console.print("[dim]─── Slash Commands ───[/dim]")
        for idx, (cmd, desc) in enumerate(SLASH_COMMANDS):
            if idx == selected:
                console.print(f"  [#22d3ee bold]▸ {cmd:<14}[/#22d3ee bold] [dim]{desc}[/dim]")
            else:
                console.print(f"    [dim]{cmd:<14} {desc}[/dim]")

        key = get_key()
        if key == "up":
            selected = (selected - 1) % len(SLASH_COMMANDS)
        elif key == "down":
            selected = (selected + 1) % len(SLASH_COMMANDS)
        elif key in ("\r", "\n"):
            return SLASH_COMMANDS[selected][0]
        elif key in ("\x1b", "esc", "\x03", "\x7f", "\x08"):
            return None


class SlashCommandCompleter(Completer):
    """Autocomplete for slash commands."""

    def get_completions(self, document, complete_event):
        text = document.text_before_cursor
        if not text.startswith("/"):
            return

        for cmd, desc in SLASH_COMMANDS:
            if cmd.lower().startswith(text.lower()):
                yield Completion(
                    cmd,
                    start_position=-len(text),
                    display=cmd,
                    display_meta=desc,
                )
