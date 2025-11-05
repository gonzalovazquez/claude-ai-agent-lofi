#!/usr/bin/env python3
"""Generate a sample audio file for testing."""

import numpy as np
import soundfile as sf
from pathlib import Path


def generate_sample_audio(output_path: str, duration: float = 3.0, sample_rate: int = 44100):
    """
    Generate a sample audio file with multiple frequency components.

    Args:
        output_path: Path to save the audio file
        duration: Duration in seconds
        sample_rate: Sample rate in Hz
    """
    # Time array
    t = np.linspace(0, duration, int(sample_rate * duration))

    # Create a complex sound with multiple frequencies
    # Base frequency (A4 note = 440 Hz)
    signal = 0.3 * np.sin(2 * np.pi * 440 * t)

    # Add harmonics
    signal += 0.2 * np.sin(2 * np.pi * 880 * t)  # Octave above
    signal += 0.1 * np.sin(2 * np.pi * 1320 * t)  # Another harmonic

    # Add some lower frequency for bass
    signal += 0.15 * np.sin(2 * np.pi * 220 * t)

    # Add a slow amplitude modulation (tremolo effect)
    modulation = 0.5 + 0.5 * np.sin(2 * np.pi * 2 * t)
    signal = signal * modulation

    # Apply fade in/out to avoid clicks
    fade_samples = int(0.05 * sample_rate)
    fade_in = np.linspace(0, 1, fade_samples)
    fade_out = np.linspace(1, 0, fade_samples)

    signal[:fade_samples] *= fade_in
    signal[-fade_samples:] *= fade_out

    # Normalize
    signal = signal / np.max(np.abs(signal)) * 0.8

    # Save as WAV file
    sf.write(output_path, signal, sample_rate)
    print(f"Generated sample audio file: {output_path}")
    print(f"  Duration: {duration}s")
    print(f"  Sample rate: {sample_rate} Hz")
    print(f"  Samples: {len(signal)}")


if __name__ == "__main__":
    # Create samples directory
    samples_dir = Path("samples")
    samples_dir.mkdir(exist_ok=True)

    # Generate sample files
    generate_sample_audio("samples/sample_tone.wav", duration=3.0)

    print("\nSample file generated! Test it with:")
    print("  python main.py samples/sample_tone.wav")
    print("  python main.py samples/sample_tone.wav --mode spectrum")
    print("  python main.py samples/sample_tone.wav --mode oscilloscope")
