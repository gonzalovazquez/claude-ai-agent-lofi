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

from src.audio_input import AudioFileReader, MicrophoneInput
from src.visualizer import WaveformVisualizer
import time
import signal


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


def list_audio_devices():
    """List all available audio input devices."""
    try:
        with MicrophoneInput() as mic:
            devices = mic.list_devices()

            if not devices:
                console.print("[yellow]No audio input devices found.[/yellow]")
                return

            console.print("\n[cyan]Available Audio Input Devices:[/cyan]\n")
            for device in devices:
                console.print(f"  [{device['index']}] {device['name']}")
                console.print(f"      Channels: {device['channels']}, Sample Rate: {device['sample_rate']} Hz")

    except Exception as e:
        console.print(f"[red]Error listing devices: {e}[/red]")
        sys.exit(1)


def visualize_microphone_live(mode: str = "waveform", device_index: int = None, refresh_rate: float = 0.05):
    """
    Visualize microphone input in real-time.

    Args:
        mode: Visualization mode (waveform, spectrum, oscilloscope)
        device_index: Index of the audio input device (None for default)
        refresh_rate: Display refresh rate in seconds
    """
    # Flag to handle graceful shutdown
    running = True

    def signal_handler(sig, frame):
        nonlocal running
        running = False

    signal.signal(signal.SIGINT, signal_handler)

    try:
        # Initialize microphone
        console.print(f"[cyan]Starting microphone input...[/cyan]")
        mic = MicrophoneInput(sample_rate=44100, chunk_size=2048, buffer_size=30)

        # Start the audio stream
        mic.start_stream(device_index=device_index)
        console.print(f"[green]Microphone active! Speak to see visualization.[/green]")
        console.print(f"[dim]Press Ctrl+C to stop[/dim]\n")

        # Initialize visualizer
        terminal_width = console.width - 4
        visualizer = WaveformVisualizer(width=terminal_width, height=20)

        # Set title based on mode
        if mode == "waveform":
            title = "🎙️  Live Waveform"
        elif mode == "spectrum":
            title = "🎙️  Live Spectrum"
        elif mode == "oscilloscope":
            title = "🎙️  Live Oscilloscope"
        else:
            title = "🎙️  Live Audio"

        # Start live display
        with Live(console=console, refresh_per_second=int(1/refresh_rate)) as live:
            while running:
                try:
                    # Get audio data from buffer
                    audio_data = mic.get_buffer()

                    if len(audio_data) == 0:
                        # No audio yet, show waiting message
                        layout = Layout()
                        layout.split_column(
                            Layout(Panel(
                                "[dim]Waiting for audio input...[/dim]\n" * 10,
                                title=title,
                                border_style="yellow",
                                box=box.ROUNDED,
                            )),
                            Layout(Panel(
                                "[dim]Peak: 0.0000  |  RMS: 0.0000[/dim]",
                                title="📊 Audio Levels",
                                border_style="blue",
                                box=box.ROUNDED,
                            ), size=3),
                        )
                        live.update(layout)
                        time.sleep(refresh_rate)
                        continue

                    # Normalize audio
                    audio_data = visualizer.normalize_audio(audio_data)

                    # Generate visualization
                    if mode == "waveform":
                        viz_lines = visualizer.create_waveform(audio_data)
                    elif mode == "spectrum":
                        viz_lines = visualizer.create_spectrum_bars(audio_data, num_bars=terminal_width - 4)
                    elif mode == "oscilloscope":
                        viz_lines = visualizer.create_oscilloscope(audio_data)
                    else:
                        viz_lines = ["[red]Unknown mode[/red]"]

                    viz_text = "\n".join(viz_lines)

                    # Get audio levels
                    peak, rms = mic.get_levels()

                    # Create VU meter
                    peak_bars = int(peak * 40)
                    rms_bars = int(rms * 40)

                    peak_meter = "█" * peak_bars + "░" * (40 - peak_bars)
                    rms_meter = "█" * rms_bars + "░" * (40 - rms_bars)

                    # Determine color based on levels
                    peak_color = "red" if peak > 0.9 else "yellow" if peak > 0.7 else "green"
                    rms_color = "red" if rms > 0.9 else "yellow" if rms > 0.7 else "green"

                    levels_text = (
                        f"[{peak_color}]Peak: {peak:.4f}[/{peak_color}]  [{peak_color}]{peak_meter}[/{peak_color}]\n"
                        f"[{rms_color}]RMS:  {rms:.4f}[/{rms_color}]  [{rms_color}]{rms_meter}[/{rms_color}]"
                    )

                    # Create layout with visualization and levels
                    layout = Layout()
                    layout.split_column(
                        Layout(Panel(
                            viz_text,
                            title=title,
                            border_style="green",
                            box=box.ROUNDED,
                        )),
                        Layout(Panel(
                            levels_text,
                            title="📊 Audio Levels",
                            border_style="blue",
                            box=box.ROUNDED,
                        ), size=5),
                    )

                    live.update(layout)
                    time.sleep(refresh_rate)

                except KeyboardInterrupt:
                    break
                except Exception as e:
                    console.print(f"[red]Error during visualization: {e}[/red]")
                    break

        # Cleanup
        mic.stop_stream()
        mic.close()
        console.print("\n[cyan]Microphone stopped.[/cyan]")

    except Exception as e:
        console.print(f"[red]Error: {e}[/red]")
        console.print("[yellow]Tip: Make sure you have a microphone connected and permissions are granted.[/yellow]")
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

  # Live microphone visualization (Stage 2)
  python main.py --live

  # Live microphone with spectrum mode
  python main.py --live --mode spectrum

  # List available audio input devices
  python main.py --list-devices

  # Use specific audio device
  python main.py --live --device 1

Stages:
  Stage 1: Sound file visualization ✅
  Stage 2: Real-time voice wave from microphone ✅
  Stage 3: Voice-to-text + Claude AI assistant (Planned)
        """,
    )

    parser.add_argument(
        "audio_file",
        nargs="?",
        help="Path to the audio file to visualize (not needed for --live mode)",
    )

    parser.add_argument(
        "--mode",
        "-m",
        choices=["waveform", "spectrum", "oscilloscope"],
        default="waveform",
        help="Visualization mode (default: waveform)",
    )

    parser.add_argument(
        "--live",
        "-l",
        action="store_true",
        help="Live microphone visualization (Stage 2)",
    )

    parser.add_argument(
        "--list-devices",
        action="store_true",
        help="List available audio input devices",
    )

    parser.add_argument(
        "--device",
        "-d",
        type=int,
        help="Audio input device index (use --list-devices to see available devices)",
    )

    parser.add_argument(
        "--refresh-rate",
        "-r",
        type=float,
        default=0.05,
        help="Display refresh rate in seconds (default: 0.05)",
    )

    parser.add_argument(
        "--version",
        action="version",
        version="Claude AI Agent LoFi v0.2.0 (Stage 2)",
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

    # Handle different modes
    if args.list_devices:
        list_audio_devices()
    elif args.live:
        visualize_microphone_live(args.mode, args.device, args.refresh_rate)
    elif args.audio_file:
        visualize_audio_file(args.audio_file, args.mode)
    else:
        parser.print_help()
        console.print("\n[yellow]Error: Please provide an audio file or use --live mode[/yellow]")


if __name__ == "__main__":
    main()
