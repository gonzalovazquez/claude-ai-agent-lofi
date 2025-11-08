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
import os

import numpy as np
from rich.console import Console
from rich.panel import Panel
from rich.layout import Layout
from rich.live import Live
from rich.text import Text
from rich import box
from rich.markdown import Markdown

from src.audio_input import AudioFileReader, MicrophoneInput
from src.visualizer import WaveformVisualizer
from src.speech_to_text import SpeechToText, VoiceActivityDetector
from src.assistant import ClaudeAssistant, ConversationManager, create_assistant
import time
import signal
from dotenv import load_dotenv

# Load environment variables
load_dotenv()


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


def voice_assistant_mode(
    whisper_model: str = "base",
    device_index: int = None,
    personality: str = "lofi",
    recording_duration: float = 5.0,
):
    """
    Interactive voice assistant mode with Claude AI.

    Args:
        whisper_model: Whisper model size (tiny, base, small, medium, large)
        device_index: Audio input device index
        personality: Assistant personality (helpful, concise, friendly, professional, lofi)
        recording_duration: Duration to record for each voice input in seconds
    """
    # Check for API key
    api_key = os.getenv("ANTHROPIC_API_KEY")
    if not api_key:
        console.print("[red]Error: ANTHROPIC_API_KEY not found![/red]")
        console.print("[yellow]Please set your API key:[/yellow]")
        console.print("  1. Create a .env file in the project directory")
        console.print("  2. Add: ANTHROPIC_API_KEY=your_api_key_here")
        console.print("  3. Or set it as an environment variable")
        console.print("\n[dim]Get your API key from: https://console.anthropic.com/[/dim]")
        sys.exit(1)

    # Flag for graceful shutdown
    running = True

    def signal_handler(sig, frame):
        nonlocal running
        running = False

    signal.signal(signal.SIGINT, signal_handler)

    try:
        # Initialize components
        console.print(f"[cyan]Loading Whisper model '{whisper_model}'...[/cyan]")
        stt = SpeechToText(model_size=whisper_model)
        console.print(f"[green]✓ Whisper model loaded[/green]")

        console.print(f"[cyan]Initializing Claude AI assistant...[/cyan]")
        assistant = create_assistant(personality=personality)
        conversation = ConversationManager(assistant)
        console.print(f"[green]✓ Claude assistant ready[/green]")

        console.print(f"[cyan]Starting microphone...[/cyan]")
        mic = MicrophoneInput(sample_rate=16000, chunk_size=1024, buffer_size=50)
        mic.start_stream(device_index=device_index)
        console.print(f"[green]✓ Microphone active[/green]\n")

        # Display welcome message
        welcome_panel = Panel(
            "[bold cyan]🎙️  Voice Assistant Mode[/bold cyan]\n\n"
            "[green]Ready to chat![/green] Here's how it works:\n\n"
            "1. Press [bold]ENTER[/bold] to start recording\n"
            f"2. Speak for up to {recording_duration} seconds\n"
            "3. Your speech will be transcribed and sent to Claude\n"
            "4. Claude's response will be displayed\n\n"
            "[dim]Special commands:[/dim]\n"
            "  • Say 'goodbye' or 'exit' to quit\n"
            "  • Say 'clear history' to reset conversation\n"
            "  • Press Ctrl+C to exit anytime\n\n"
            f"[yellow]Personality:[/yellow] {personality.capitalize()}",
            title="Welcome",
            border_style="cyan",
            box=box.ROUNDED,
        )
        console.print(welcome_panel)

        # Conversation loop
        turn_number = 0

        while running:
            try:
                # Wait for user to press Enter
                console.print(f"\n[bold cyan]Turn {turn_number + 1}[/bold cyan]")
                input("[yellow]Press ENTER to start recording (or Ctrl+C to exit)...[/yellow] ")

                if not running:
                    break

                # Clear buffer before recording
                mic.clear_buffer()

                # Record audio
                console.print(f"[bold green]🎤 Recording for {recording_duration} seconds... Speak now![/bold green]")

                # Show live visualization while recording
                start_time = time.time()
                terminal_width = console.width - 4
                visualizer = WaveformVisualizer(width=terminal_width, height=15)

                with Live(console=console, refresh_per_second=20) as live:
                    while time.time() - start_time < recording_duration:
                        audio_data = mic.get_buffer()

                        if len(audio_data) > 0:
                            # Normalize and visualize
                            normalized = visualizer.normalize_audio(audio_data)
                            viz_lines = visualizer.create_waveform(normalized)
                            viz_text = "\n".join(viz_lines)

                            # Get levels
                            peak, rms = mic.get_levels()
                            peak_bars = int(peak * 30)
                            rms_bars = int(rms * 30)
                            peak_meter = "█" * peak_bars + "░" * (30 - peak_bars)

                            # Time remaining
                            elapsed = time.time() - start_time
                            remaining = max(0, recording_duration - elapsed)

                            status_text = (
                                f"[cyan]Time remaining: {remaining:.1f}s[/cyan]\n"
                                f"[green]Level: {peak_meter}[/green]"
                            )

                            layout = Layout()
                            layout.split_column(
                                Layout(Panel(
                                    viz_text,
                                    title="🎙️  Recording",
                                    border_style="green",
                                    box=box.ROUNDED,
                                )),
                                Layout(Panel(
                                    status_text,
                                    border_style="cyan",
                                    box=box.ROUNDED,
                                ), size=4),
                            )

                            live.update(layout)
                            time.sleep(0.05)

                # Get recorded audio
                audio_data = mic.get_buffer()

                if len(audio_data) == 0:
                    console.print("[yellow]No audio detected. Please try again.[/yellow]")
                    continue

                console.print("[cyan]🎯 Processing speech...[/cyan]")

                # Transcribe audio
                try:
                    result = stt.transcribe_audio_data(audio_data, sample_rate=16000)
                    transcribed_text = result['text']

                    if not transcribed_text or len(transcribed_text.strip()) < 2:
                        console.print("[yellow]No speech detected. Please try again.[/yellow]")
                        continue

                    # Display transcription
                    console.print(Panel(
                        f"[bold]{transcribed_text}[/bold]",
                        title="📝 You said",
                        border_style="blue",
                        box=box.ROUNDED,
                    ))

                    # Check for exit command
                    if conversation._is_exit_command(transcribed_text):
                        response = conversation.process_voice_input(transcribed_text)
                        console.print(Panel(
                            response,
                            title="🤖 Claude",
                            border_style="green",
                            box=box.ROUNDED,
                        ))
                        console.print("\n[cyan]Thank you for using Claude AI Agent LoFi! Goodbye! 👋[/cyan]")
                        break

                    # Get Claude's response
                    console.print("[cyan]🤖 Claude is thinking...[/cyan]")
                    response = conversation.process_voice_input(transcribed_text)

                    if response:
                        # Display Claude's response
                        console.print(Panel(
                            response,
                            title="🤖 Claude",
                            border_style="green",
                            box=box.ROUNDED,
                        ))

                    turn_number += 1

                except Exception as e:
                    console.print(f"[red]Transcription error: {e}[/red]")
                    console.print("[yellow]Please try speaking again.[/yellow]")
                    continue

            except KeyboardInterrupt:
                break
            except EOFError:
                # Handle Ctrl+D
                break
            except Exception as e:
                console.print(f"[red]Error: {e}[/red]")
                continue

        # Cleanup
        mic.stop_stream()
        mic.close()
        console.print("\n[cyan]Session ended. Goodbye![/cyan]")

    except Exception as e:
        console.print(f"[red]Fatal error: {e}[/red]")
        import traceback
        traceback.print_exc()
        sys.exit(1)


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="Claude AI Agent LoFi - CLI Sound Visualizer and AI Assistant",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Stage 1: Visualize a sound file as waveform
  python main.py file.wav

  # Stage 1: Visualize as spectrum analyzer
  python main.py file.wav --mode spectrum

  # Stage 2: Live microphone visualization
  python main.py --live

  # Stage 2: Live microphone with spectrum mode
  python main.py --live --mode spectrum

  # Stage 2: List available audio input devices
  python main.py --list-devices

  # Stage 3: Voice assistant mode (default, lofi personality)
  python main.py --assistant

  # Stage 3: Voice assistant with different personality
  python main.py --assistant --personality friendly

  # Stage 3: Voice assistant with smaller/faster Whisper model
  python main.py --assistant --whisper-model tiny

  # Stage 3: Voice assistant with longer recording duration
  python main.py --assistant --duration 10

Stages:
  Stage 1: Sound file visualization ✅
  Stage 2: Real-time voice wave from microphone ✅
  Stage 3: Voice-to-text + Claude AI assistant ✅
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

    # Stage 3: Voice Assistant arguments
    parser.add_argument(
        "--assistant",
        "-a",
        action="store_true",
        help="Voice assistant mode with Claude AI (Stage 3)",
    )

    parser.add_argument(
        "--whisper-model",
        choices=["tiny", "base", "small", "medium", "large"],
        default="base",
        help="Whisper model size (default: base). tiny=fastest, large=most accurate",
    )

    parser.add_argument(
        "--personality",
        "-p",
        choices=["helpful", "concise", "friendly", "professional", "lofi"],
        default="lofi",
        help="Assistant personality (default: lofi)",
    )

    parser.add_argument(
        "--duration",
        type=float,
        default=5.0,
        help="Recording duration in seconds for each voice input (default: 5.0)",
    )

    parser.add_argument(
        "--version",
        action="version",
        version="Claude AI Agent LoFi v0.3.0 (Stage 3)",
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
    elif args.assistant:
        # Stage 3: Voice Assistant mode
        voice_assistant_mode(
            whisper_model=args.whisper_model,
            device_index=args.device,
            personality=args.personality,
            recording_duration=args.duration,
        )
    elif args.live:
        # Stage 2: Live visualization
        visualize_microphone_live(args.mode, args.device, args.refresh_rate)
    elif args.audio_file:
        # Stage 1: File visualization
        visualize_audio_file(args.audio_file, args.mode)
    else:
        parser.print_help()
        console.print("\n[yellow]Error: Please provide an audio file, use --live mode, or use --assistant mode[/yellow]")


if __name__ == "__main__":
    main()
