#!/usr/bin/env python3
"""
Claude AI Agent LoFi - CLI Sound Visualizer and AI Assistant

Stage 1: Sound file visualization
Stage 2: Real-time voice wave visualization
Stage 3: Voice-to-text + Claude AI personal assistant
"""

import argparse
import sys
from pathlib import Path

import numpy as np
from rich.console import Console
from rich.panel import Panel
from rich.layout import Layout
from rich.live import Live
from rich.text import Text
from rich import box

from src.audio_input import AudioFileReader
from src.visualizer import WaveformVisualizer


console = Console()


def visualize_audio_file(file_path: str, mode: str = "waveform"):
    """
    Visualize an audio file in the terminal.

    Args:
        file_path: Path to the audio file
        mode: Visualization mode (waveform, spectrum, oscilloscope)
    """
    try:
        # Read audio file
        console.print(f"[cyan]Loading audio file: {file_path}[/cyan]")
        reader = AudioFileReader(file_path)

        # Get file info
        info = reader.get_info()
        console.print("\n[yellow]Audio File Information:[/yellow]")
        console.print(f"  Duration: {info['duration']:.2f} seconds")
        console.print(f"  Sample Rate: {info['sample_rate']} Hz")
        console.print(f"  Channels: {info['channels']}")
        console.print(f"  Format: {info['format']} ({info['subtype']})")
        console.print()

        # Read audio data
        audio_data, sample_rate = reader.read()

        # Create visualizer
        terminal_width = console.width - 4  # Account for panel borders
        visualizer = WaveformVisualizer(width=terminal_width, height=20)

        # Normalize audio
        audio_data = visualizer.normalize_audio(audio_data)

        # Generate visualization based on mode
        console.print(f"[cyan]Generating {mode} visualization...[/cyan]\n")

        if mode == "waveform":
            viz_lines = visualizer.create_waveform(audio_data)
            title = "🎵 Waveform View"
        elif mode == "spectrum":
            viz_lines = visualizer.create_spectrum_bars(audio_data, num_bars=terminal_width - 4)
            title = "📊 Spectrum Analyzer"
        elif mode == "oscilloscope":
            viz_lines = visualizer.create_oscilloscope(audio_data)
            title = "〰️  Oscilloscope View"
        else:
            console.print(f"[red]Unknown visualization mode: {mode}[/red]")
            return

        # Display visualization
        viz_text = "\n".join(viz_lines)
        panel = Panel(
            viz_text,
            title=title,
            border_style="green",
            box=box.ROUNDED,
        )

        console.print(panel)

        # Show audio statistics
        console.print("\n[yellow]Audio Statistics:[/yellow]")
        console.print(f"  Peak Amplitude: {np.max(np.abs(audio_data)):.4f}")
        console.print(f"  RMS Level: {np.sqrt(np.mean(audio_data**2)):.4f}")
        console.print(f"  Samples: {len(audio_data):,}")

    except Exception as e:
        console.print(f"[red]Error: {e}[/red]")
        sys.exit(1)


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="Claude AI Agent LoFi - CLI Sound Visualizer and AI Assistant",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Visualize a sound file as waveform
  python main.py file.wav

  # Visualize as spectrum analyzer
  python main.py file.wav --mode spectrum

  # Visualize as oscilloscope
  python main.py file.wav --mode oscilloscope

Stages:
  Stage 1 (Current): Sound file visualization
  Stage 2 (Planned): Real-time voice wave from microphone
  Stage 3 (Planned): Voice-to-text + Claude AI assistant
        """,
    )

    parser.add_argument(
        "audio_file",
        help="Path to the audio file to visualize",
    )

    parser.add_argument(
        "--mode",
        "-m",
        choices=["waveform", "spectrum", "oscilloscope"],
        default="waveform",
        help="Visualization mode (default: waveform)",
    )

    parser.add_argument(
        "--version",
        action="version",
        version="Claude AI Agent LoFi v0.1.0 (Stage 1)",
    )

    args = parser.parse_args()

    # Display welcome banner
    console.print(
        Panel.fit(
            "[bold cyan]Claude AI Agent LoFi[/bold cyan]\n"
            "[dim]CLI Sound Visualizer & AI Assistant[/dim]",
            border_style="cyan",
        )
    )
    console.print()

    # Visualize the audio file
    visualize_audio_file(args.audio_file, args.mode)


if __name__ == "__main__":
    main()
