"""Speech-to-text module using OpenAI Whisper."""

import whisper
import numpy as np
import tempfile
import soundfile as sf
from typing import Optional
from pathlib import Path


class SpeechToText:
    """Convert speech audio to text using Whisper."""

    def __init__(self, model_size: str = "base"):
        """
        Initialize the speech-to-text engine.

        Args:
            model_size: Whisper model size (tiny, base, small, medium, large)
                       tiny: fastest, least accurate (~1GB RAM)
                       base: good balance (~1GB RAM)
                       small: better accuracy (~2GB RAM)
                       medium: high accuracy (~5GB RAM)
                       large: best accuracy (~10GB RAM)
        """
        self.model_size = model_size
        self.model = None
        self._load_model()

    def _load_model(self):
        """Load the Whisper model."""
        try:
            self.model = whisper.load_model(self.model_size)
        except Exception as e:
            raise RuntimeError(f"Failed to load Whisper model '{self.model_size}': {e}")

    def transcribe_audio_data(
        self,
        audio_data: np.ndarray,
        sample_rate: int = 16000,
        language: Optional[str] = None,
    ) -> dict:
        """
        Transcribe audio data to text.

        Args:
            audio_data: Audio samples as numpy array
            sample_rate: Sample rate of the audio
            language: Language code (e.g., 'en', 'es', 'fr') or None for auto-detect

        Returns:
            Dictionary with transcription results:
            {
                'text': str,           # Transcribed text
                'language': str,       # Detected/specified language
                'segments': list,      # Detailed segments with timestamps
                'confidence': float    # Average confidence (if available)
            }
        """
        if self.model is None:
            raise RuntimeError("Whisper model not loaded")

        try:
            # Whisper expects 16kHz audio, so resample if needed
            if sample_rate != 16000:
                audio_data = self._resample_audio(audio_data, sample_rate, 16000)

            # Ensure audio is float32 and in [-1, 1] range
            if audio_data.dtype != np.float32:
                audio_data = audio_data.astype(np.float32)

            # Normalize if needed
            max_val = np.max(np.abs(audio_data))
            if max_val > 1.0:
                audio_data = audio_data / max_val

            # Transcribe
            result = self.model.transcribe(
                audio_data,
                language=language,
                fp16=False,  # Use FP32 for better compatibility
            )

            # Calculate average confidence if segments available
            confidence = 0.0
            if 'segments' in result and result['segments']:
                # Whisper doesn't always provide confidence, estimate from segments
                confidence = sum(1.0 for seg in result['segments']) / len(result['segments'])

            return {
                'text': result['text'].strip(),
                'language': result.get('language', 'unknown'),
                'segments': result.get('segments', []),
                'confidence': confidence,
            }

        except Exception as e:
            raise RuntimeError(f"Transcription failed: {e}")

    def transcribe_file(
        self,
        file_path: str,
        language: Optional[str] = None,
    ) -> dict:
        """
        Transcribe an audio file to text.

        Args:
            file_path: Path to the audio file
            language: Language code or None for auto-detect

        Returns:
            Dictionary with transcription results
        """
        if self.model is None:
            raise RuntimeError("Whisper model not loaded")

        try:
            result = self.model.transcribe(
                str(file_path),
                language=language,
                fp16=False,
            )

            confidence = 0.0
            if 'segments' in result and result['segments']:
                confidence = sum(1.0 for seg in result['segments']) / len(result['segments'])

            return {
                'text': result['text'].strip(),
                'language': result.get('language', 'unknown'),
                'segments': result.get('segments', []),
                'confidence': confidence,
            }

        except Exception as e:
            raise RuntimeError(f"File transcription failed: {e}")

    def _resample_audio(
        self,
        audio_data: np.ndarray,
        orig_sr: int,
        target_sr: int,
    ) -> np.ndarray:
        """
        Resample audio to target sample rate.

        Args:
            audio_data: Input audio samples
            orig_sr: Original sample rate
            target_sr: Target sample rate

        Returns:
            Resampled audio
        """
        # Simple linear interpolation resampling
        duration = len(audio_data) / orig_sr
        target_length = int(duration * target_sr)

        # Use numpy's interp for resampling
        x_old = np.linspace(0, duration, len(audio_data))
        x_new = np.linspace(0, duration, target_length)
        audio_resampled = np.interp(x_new, x_old, audio_data)

        return audio_resampled.astype(np.float32)

    def is_speech_detected(
        self,
        audio_data: np.ndarray,
        threshold: float = 0.02,
        min_duration: float = 0.3,
        sample_rate: int = 16000,
    ) -> bool:
        """
        Detect if the audio contains speech (simple energy-based VAD).

        Args:
            audio_data: Audio samples
            threshold: Energy threshold for speech detection
            min_duration: Minimum duration in seconds to consider as speech
            sample_rate: Sample rate of the audio

        Returns:
            True if speech is detected, False otherwise
        """
        # Calculate RMS energy
        rms = np.sqrt(np.mean(audio_data**2))

        # Check if audio is long enough
        duration = len(audio_data) / sample_rate

        return rms > threshold and duration >= min_duration

    def get_model_info(self) -> dict:
        """
        Get information about the loaded model.

        Returns:
            Dictionary with model information
        """
        return {
            'model_size': self.model_size,
            'loaded': self.model is not None,
        }


class VoiceActivityDetector:
    """Simple voice activity detector based on energy levels."""

    def __init__(
        self,
        energy_threshold: float = 0.02,
        speech_pad_ms: int = 300,
        sample_rate: int = 16000,
    ):
        """
        Initialize voice activity detector.

        Args:
            energy_threshold: Energy threshold for voice detection
            speech_pad_ms: Padding in milliseconds before/after speech
            sample_rate: Audio sample rate
        """
        self.energy_threshold = energy_threshold
        self.speech_pad_ms = speech_pad_ms
        self.sample_rate = sample_rate
        self.speech_pad_samples = int((speech_pad_ms / 1000.0) * sample_rate)

    def detect(self, audio_data: np.ndarray) -> bool:
        """
        Detect if audio contains voice activity.

        Args:
            audio_data: Audio samples

        Returns:
            True if voice activity detected
        """
        # Calculate RMS energy
        rms = np.sqrt(np.mean(audio_data**2))
        return rms > self.energy_threshold

    def find_speech_segments(
        self,
        audio_data: np.ndarray,
        chunk_size: int = 1024,
    ) -> list:
        """
        Find speech segments in audio data.

        Args:
            audio_data: Audio samples
            chunk_size: Size of chunks to analyze

        Returns:
            List of (start_sample, end_sample) tuples for speech segments
        """
        segments = []
        is_speech = False
        start_sample = 0

        for i in range(0, len(audio_data), chunk_size):
            chunk = audio_data[i:i + chunk_size]
            has_speech = self.detect(chunk)

            if has_speech and not is_speech:
                # Speech started
                start_sample = max(0, i - self.speech_pad_samples)
                is_speech = True
            elif not has_speech and is_speech:
                # Speech ended
                end_sample = min(len(audio_data), i + self.speech_pad_samples)
                segments.append((start_sample, end_sample))
                is_speech = False

        # Handle case where speech continues to the end
        if is_speech:
            segments.append((start_sample, len(audio_data)))

        return segments
