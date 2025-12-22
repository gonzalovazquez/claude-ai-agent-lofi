"""Audio input handling module."""

import soundfile as sf
import numpy as np
from typing import Tuple, Optional, Callable
from pathlib import Path
import pyaudio
import threading
from collections import deque


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


class MicrophoneInput:
    """Handle real-time microphone input."""

    def __init__(
        self,
        sample_rate: int = 44100,
        chunk_size: int = 1024,
        channels: int = 1,
        buffer_size: int = 50,
    ):
        """
        Initialize microphone input.

        Args:
            sample_rate: Sampling rate in Hz
            chunk_size: Number of frames per buffer
            channels: Number of audio channels (1 for mono, 2 for stereo)
            buffer_size: Number of chunks to keep in rolling buffer
        """
        self.sample_rate = sample_rate
        self.chunk_size = chunk_size
        self.channels = channels
        self.buffer_size = buffer_size

        # PyAudio setup
        self.p = pyaudio.PyAudio()
        self.stream = None
        self.is_running = False

        # Rolling buffer for audio data
        self.audio_buffer = deque(maxlen=buffer_size)
        self._lock = threading.Lock()

        # Audio statistics
        self.peak_level = 0.0
        self.rms_level = 0.0

    def list_devices(self) -> list:
        """
        List all available audio input devices.

        Returns:
            List of device information dictionaries
        """
        devices = []
        for i in range(self.p.get_device_count()):
            device_info = self.p.get_device_info_by_index(i)
            if device_info['maxInputChannels'] > 0:
                devices.append({
                    'index': i,
                    'name': device_info['name'],
                    'channels': device_info['maxInputChannels'],
                    'sample_rate': int(device_info['defaultSampleRate']),
                })
        return devices

    def start_stream(self, device_index: Optional[int] = None):
        """
        Start capturing audio from microphone.

        Args:
            device_index: Index of the input device (None for default)
        """
        if self.is_running:
            return

        try:
            self.stream = self.p.open(
                format=pyaudio.paFloat32,
                channels=self.channels,
                rate=self.sample_rate,
                input=True,
                input_device_index=device_index,
                frames_per_buffer=self.chunk_size,
                stream_callback=self._audio_callback,
            )

            self.is_running = True
            self.stream.start_stream()

        except Exception as e:
            raise RuntimeError(f"Failed to start microphone stream: {e}")

    def _audio_callback(self, in_data, frame_count, time_info, status):
        """
        Callback function for audio stream.

        Args:
            in_data: Input audio data
            frame_count: Number of frames
            time_info: Time information
            status: Stream status

        Returns:
            Tuple of (None, pyaudio.paContinue)
        """
        # Convert bytes to numpy array
        audio_data = np.frombuffer(in_data, dtype=np.float32)

        # Convert stereo to mono if needed
        if self.channels > 1:
            audio_data = audio_data.reshape(-1, self.channels)
            audio_data = np.mean(audio_data, axis=1)

        # Update statistics
        self.peak_level = np.max(np.abs(audio_data))
        self.rms_level = np.sqrt(np.mean(audio_data**2))

        # Add to buffer
        with self._lock:
            self.audio_buffer.append(audio_data.copy())

        return (None, pyaudio.paContinue)

    def read_chunk(self) -> Optional[np.ndarray]:
        """
        Read the latest chunk of audio data from the microphone.

        Returns:
            Numpy array of audio samples, or None if no data available
        """
        with self._lock:
            if len(self.audio_buffer) == 0:
                return None
            return self.audio_buffer[-1].copy()

    def get_buffer(self) -> np.ndarray:
        """
        Get all audio data from the rolling buffer.

        Returns:
            Numpy array of concatenated audio samples
        """
        with self._lock:
            if len(self.audio_buffer) == 0:
                return np.array([])
            return np.concatenate(list(self.audio_buffer))

    def get_levels(self) -> Tuple[float, float]:
        """
        Get current audio levels.

        Returns:
            Tuple of (peak_level, rms_level)
        """
        return self.peak_level, self.rms_level

    def clear_buffer(self):
        """Clear the audio buffer."""
        with self._lock:
            self.audio_buffer.clear()

    def stop_stream(self):
        """Stop capturing audio."""
        if not self.is_running:
            return

        self.is_running = False

        if self.stream:
            self.stream.stop_stream()
            self.stream.close()
            self.stream = None

    def close(self):
        """Close the microphone input and cleanup resources."""
        self.stop_stream()
        self.p.terminate()

    def __enter__(self):
        """Context manager entry."""
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit."""
        self.close()
