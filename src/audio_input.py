"""Audio input handling module."""

import soundfile as sf
import numpy as np
from typing import Tuple, Optional
from pathlib import Path


class AudioFileReader:
    """Handle reading and processing audio files."""

    SUPPORTED_FORMATS = ['.wav', '.flac', '.ogg', '.mp3']

    def __init__(self, file_path: str):
        """
        Initialize the audio file reader.

        Args:
            file_path: Path to the audio file
        """
        self.file_path = Path(file_path)
        self._validate_file()

    def _validate_file(self):
        """Validate that the file exists and has a supported format."""
        if not self.file_path.exists():
            raise FileNotFoundError(f"Audio file not found: {self.file_path}")

        if self.file_path.suffix.lower() not in self.SUPPORTED_FORMATS:
            raise ValueError(
                f"Unsupported audio format: {self.file_path.suffix}. "
                f"Supported formats: {', '.join(self.SUPPORTED_FORMATS)}"
            )

    def read(self) -> Tuple[np.ndarray, int]:
        """
        Read the audio file.

        Returns:
            Tuple of (audio_data, sample_rate)
        """
        try:
            audio_data, sample_rate = sf.read(str(self.file_path))

            # Convert stereo to mono if needed
            if len(audio_data.shape) > 1:
                audio_data = np.mean(audio_data, axis=1)

            return audio_data, sample_rate

        except Exception as e:
            raise RuntimeError(f"Failed to read audio file: {e}")

    def read_segment(
        self, start_time: float = 0, duration: Optional[float] = None
    ) -> Tuple[np.ndarray, int]:
        """
        Read a segment of the audio file.

        Args:
            start_time: Start time in seconds
            duration: Duration in seconds (None for entire file)

        Returns:
            Tuple of (audio_data, sample_rate)
        """
        try:
            info = sf.info(str(self.file_path))
            sample_rate = info.samplerate

            start_frame = int(start_time * sample_rate)
            frames = None if duration is None else int(duration * sample_rate)

            audio_data, _ = sf.read(
                str(self.file_path), start=start_frame, frames=frames
            )

            # Convert stereo to mono if needed
            if len(audio_data.shape) > 1:
                audio_data = np.mean(audio_data, axis=1)

            return audio_data, sample_rate

        except Exception as e:
            raise RuntimeError(f"Failed to read audio segment: {e}")

    def get_info(self) -> dict:
        """
        Get information about the audio file.

        Returns:
            Dictionary with file information
        """
        info = sf.info(str(self.file_path))

        return {
            'duration': info.duration,
            'sample_rate': info.samplerate,
            'channels': info.channels,
            'format': info.format,
            'subtype': info.subtype,
            'frames': info.frames,
        }


# Placeholder for Stage 2: Microphone input
class MicrophoneInput:
    """Handle real-time microphone input (Stage 2)."""

    def __init__(self, sample_rate: int = 44100, chunk_size: int = 1024):
        """
        Initialize microphone input.

        Args:
            sample_rate: Sampling rate in Hz
            chunk_size: Number of frames per buffer
        """
        self.sample_rate = sample_rate
        self.chunk_size = chunk_size
        # TODO: Implement with pyaudio in Stage 2

    def start_stream(self):
        """Start capturing audio from microphone."""
        raise NotImplementedError("Microphone input will be implemented in Stage 2")

    def read_chunk(self) -> np.ndarray:
        """Read a chunk of audio data from the microphone."""
        raise NotImplementedError("Microphone input will be implemented in Stage 2")

    def stop_stream(self):
        """Stop capturing audio."""
        raise NotImplementedError("Microphone input will be implemented in Stage 2")
