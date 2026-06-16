# SPDX-License-Identifier: Apache-2.0
# Copyright 2026 A-Eye contributors
"""A-Eye command-line interface."""
from __future__ import annotations

import sys

import typer
from rich import print as rprint
from rich.console import Console

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


@app.command()
def transcribe(
    source: str = typer.Argument(
        ..., help="Local file path, or a video URL (YouTube/Vimeo/...)."
    ),
) -> None:
    """Ingest + extract + transcribe; print the timestamped transcript."""
    from .extract import extract as extract_video
    from .transcribe import transcribe as transcribe_audio

    try:
        src = ingest_video(source)
        ext = extract_video(src)
        segments = transcribe_audio(ext.audio_path)
    except (FileNotFoundError, ValueError, RuntimeError) as exc:
        rprint(f"[red]✗[/] {exc}")
        raise typer.Exit(code=1) from exc

    rprint(f"[green]✓[/] [bold]{src.title or src.path.name}[/] — {len(segments)} segments")
    for seg in segments[:20]:
        rprint(f"  [dim]{seg.start:6.1f}–{seg.end:5.1f}[/] {seg.text}")
    if len(segments) > 20:
        rprint(f"  [dim]… {len(segments) - 20} more[/]")


@app.command()
def ask(
    source: str = typer.Argument(..., help="Local file path, or a video URL."),
    question: str = typer.Argument(..., help="Your question about the video."),
    reason: bool = typer.Option(False, "--reason", help="Deep Reasoning mode."),
    search: bool = typer.Option(False, "--search", help="Web Search mode."),
) -> None:
    """Run the full pipeline (ingest -> extract -> transcribe -> see -> index) and answer."""
    from .chat import ask as ask_video
    from .extract import extract as extract_video
    from .index import build_index, save_index
    from .transcribe import transcribe as transcribe_audio
    from .vision import see

    console = Console()
    try:
        with console.status("Ingesting…"):
            src = ingest_video(source)
        with console.status("Extracting audio + keyframes…"):
            ext = extract_video(src)
        with console.status("Transcribing…"):
            transcript = transcribe_audio(ext.audio_path)
        with console.status(f"Watching {len(ext.keyframes)} keyframe(s)…"):
            captions = see(ext.keyframes)
        index = build_index(src, ext, transcript, captions)
        save_index(index, ext.workdir / "index.json")
    except (FileNotFoundError, ValueError, RuntimeError) as exc:
        rprint(f"[red]✗[/] {exc}")
        raise typer.Exit(code=1) from exc

    rprint(f"[bold #E5392F]A-Eye[/] [dim]({src.title or src.path.name})[/]\n")
    for chunk in ask_video(index, question, deep_reasoning=reason, web_search=search):
        sys.stdout.write(chunk)
        sys.stdout.flush()
    sys.stdout.write("\n")


if __name__ == "__main__":
    app()
