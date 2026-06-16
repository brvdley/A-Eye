# SPDX-License-Identifier: Apache-2.0
# Copyright 2026 A-Eye contributors
"""A-Eye command-line interface."""
from __future__ import annotations

import typer
from rich import print as rprint

from . import __version__
from .ingest import ingest as ingest_video

app = typer.Typer(
    help="A-Eye — watch any video with an AI that actually sees it.",
    no_args_is_help=True,
    add_completion=False,
)


@app.command()
def version() -> None:
    """Print the A-Eye version."""
    rprint(f"A-Eye {__version__}")


@app.command()
def ingest(
    source: str = typer.Argument(
        ..., help="Local file path, or a video URL (YouTube/Vimeo/...)."
    ),
) -> None:
    """Resolve a local file or URL into a local video (downloads URLs via yt-dlp)."""
    try:
        src = ingest_video(source)
    except (FileNotFoundError, ValueError, RuntimeError) as exc:
        rprint(f"[red]✗[/] {exc}")
        raise typer.Exit(code=1) from exc

    rprint(f"[green]✓[/] [bold]{src.title or src.path.name}[/]")
    rprint(f"  path: {src.path}")
    if src.source_url:
        rprint(f"  url:  {src.source_url}")
    if src.duration:
        rprint(f"  duration: {src.duration:.0f}s")


@app.command()
def extract(
    source: str = typer.Argument(
        ..., help="Local file path, or a video URL (YouTube/Vimeo/...)."
    ),
) -> None:
    """Ingest a video, then extract audio + keyframes (+ sidecar subtitles)."""
    from .extract import extract as extract_video

    try:
        src = ingest_video(source)
        ext = extract_video(src)
    except (FileNotFoundError, ValueError, RuntimeError) as exc:
        rprint(f"[red]✗[/] {exc}")
        raise typer.Exit(code=1) from exc

    rprint(f"[green]✓[/] [bold]{src.title or src.path.name}[/]")
    if ext.duration:
        rprint(f"  duration:  {ext.duration:.1f}s")
    rprint(f"  keyframes: {len(ext.keyframes)}")
    rprint(f"  subtitles: {len(ext.subtitles)} cues")
    rprint(f"  audio:     {ext.audio_path}")
    rprint(f"  workdir:   {ext.workdir}")


if __name__ == "__main__":
    app()
