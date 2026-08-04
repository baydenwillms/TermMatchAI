"""
Terminal UI helpers for TermMatchAI.

Same approach as FAIReSheets / edna2obis: pyfiglet for the banner, rich for
colored prompts and progress. Keeps HuggingFace / torch noise out of the way
so matching steps read as short status lines instead of a wall of text.
"""

from __future__ import annotations

import logging
import os
import warnings
from pathlib import Path
from typing import List, Optional

import pyfiglet
from rich.console import Console
from rich.panel import Panel
from rich.prompt import IntPrompt
from rich.table import Table

from data_loading.data_loading import INPUTS_DIR

console = Console()


def quiet_third_party_logs() -> None:
    """Mute transformers / HF / torch chatter that floods the terminal."""
    os.environ.setdefault("TOKENIZERS_PARALLELISM", "false")
    os.environ.setdefault("HF_HUB_DISABLE_PROGRESS_BARS", "1")
    os.environ.setdefault("HF_HUB_DISABLE_SYMLINKS_WARNING", "1")
    os.environ.setdefault("TRANSFORMERS_VERBOSITY", "error")

    for name in (
        "transformers",
        "sentence_transformers",
        "huggingface_hub",
        "torch",
        "filelock",
        "urllib3",
    ):
        logging.getLogger(name).setLevel(logging.ERROR)

    try:
        from transformers.utils import logging as hf_logging
        hf_logging.set_verbosity_error()
    except Exception:
        pass

    warnings.filterwarnings("ignore", message=".*UntypedStorage.*")
    warnings.filterwarnings("ignore", message=".*symlinks.*")
    warnings.filterwarnings("ignore", category=FutureWarning, module="transformers.*")
    warnings.filterwarnings("ignore", category=UserWarning, module="torch.*")
    warnings.filterwarnings(
        "ignore", category=UserWarning, module="huggingface_hub.*"
    )


def print_banner() -> None:
    """ASCII title banner (same stack / default font as FAIReSheets)."""
    banner = pyfiglet.figlet_format("TermMatchAI")
    console.print()
    console.print(banner.rstrip("\n"), style="bold cyan")
    console.print(
        "Map YOUR data standard onto the FAIR eDNA data standard.\n",
        style="bold",
    )


def list_input_jsons(inputs_dir: Optional[str] = None) -> List[Path]:
    """Sorted list of *.json files in the inputs directory."""
    root = Path(inputs_dir or INPUTS_DIR)
    if not root.is_dir():
        return []
    return sorted(root.glob("*.json"), key=lambda p: p.name.lower())


def print_input_json_menu(files: List[Path]) -> None:
    """Numbered list of standards in inputs/ (shown once before both picks)."""
    table = Table(show_header=True, header_style="bold", box=None, pad_edge=False)
    table.add_column("#", style="bold cyan", justify="right", width=4)
    table.add_column("File", style="white")
    for i, path in enumerate(files, start=1):
        table.add_row(str(i), path.name)

    console.print(
        Panel(
            table,
            title="[bold]Available standards[/bold]",
            subtitle="[dim]Pick by number in the steps below[/dim]",
            border_style="bright_black",
            padding=(0, 1),
        )
    )
    console.print()


def prompt_choose_input_json(
    step: str,
    headline: str,
    detail: str,
    files: List[Path],
    default_index: Optional[int] = None,
) -> Path:
    """
    Ask for a numbered choice from files (menu should already be on screen).
    default_index is 1-based (same numbers shown in the menu).
    """
    if not files:
        raise FileNotFoundError(
            f"No .json files found in {INPUTS_DIR}. "
            "Add a standard JSON there, then re-run."
        )

    default = default_index if default_index is not None else 1
    if not (1 <= default <= len(files)):
        default = 1

    console.print(f"[bold cyan]{step}[/bold cyan]  [bold]{headline}[/bold]")
    console.print(f"  [dim]{detail}[/dim]")
    while True:
        choice = IntPrompt.ask(
            "  Number",
            default=default,
            console=console,
        )
        if 1 <= choice <= len(files):
            chosen = files[choice - 1]
            console.print(f"  [green]✓[/green] [green]{chosen.name}[/green]")
            console.print()
            return chosen
        console.print(
            f"  [yellow]Enter a number between 1 and {len(files)}.[/yellow]"
        )


def prompt_num_matches(default: int = 3) -> int:
    """How many FAIR eDNA candidates to show per user term."""
    while True:
        n = IntPrompt.ask(
            "Matches to show per term (1-5)",
            default=default,
            console=console,
        )
        if 1 <= n <= 5:
            return n
        console.print("[yellow]Please enter a number between 1 and 5.[/yellow]")


def step(message: str) -> None:
    """One-line progress marker so long runs don't look frozen."""
    console.print(f"  [cyan]•[/cyan] {message}")


def step_done(message: str) -> None:
    console.print(f"  [green]✓[/green] {message}")


def default_index_for(files: List[Path], preferred_name: str) -> int:
    """1-based index of preferred_name in files, or 1 if not found."""
    preferred = preferred_name.lower()
    for i, path in enumerate(files, start=1):
        if path.name.lower() == preferred:
            return i
    return 1
