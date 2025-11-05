"""Audio visualization module for CLI."""

import numpy as np
from typing import List, Tuple


class WaveformVisualizer:
    """Visualize audio waveforms in the terminal."""

    def __init__(self, width: int = 80, height: int = 20):
        """
        Initialize the visualizer.

        Args:
            width: Width of the visualization in characters
            height: Height of the visualization in characters
        """
        self.width = width
        self.height = height

    def normalize_audio(self, audio_data: np.ndarray) -> np.ndarray:
        """
        Normalize audio data to [-1, 1] range.

        Args:
            audio_data: Raw audio samples

        Returns:
            Normalized audio data
        """
        if audio_data.dtype == np.int16:
            audio_data = audio_data.astype(np.float32) / 32768.0
        elif audio_data.dtype == np.int32:
            audio_data = audio_data.astype(np.float32) / 2147483648.0

        # Normalize to [-1, 1]
        max_val = np.max(np.abs(audio_data))
        if max_val > 0:
            audio_data = audio_data / max_val

        return audio_data

    def downsample_for_display(self, audio_data: np.ndarray, target_width: int) -> np.ndarray:
        """
        Downsample audio data to fit display width.

        Args:
            audio_data: Audio samples
            target_width: Target number of samples

        Returns:
            Downsampled audio data
        """
        if len(audio_data) <= target_width:
            return audio_data

        # Calculate chunk size
        chunk_size = len(audio_data) // target_width

        # Take RMS of each chunk for better visualization
        downsampled = []
        for i in range(target_width):
            start = i * chunk_size
            end = start + chunk_size
            if end > len(audio_data):
                end = len(audio_data)

            chunk = audio_data[start:end]
            # Use RMS for better representation of amplitude
            rms = np.sqrt(np.mean(chunk**2))
            downsampled.append(rms)

        return np.array(downsampled)

    def create_waveform(self, audio_data: np.ndarray) -> List[str]:
        """
        Create ASCII waveform visualization.

        Args:
            audio_data: Normalized audio samples

        Returns:
            List of strings representing the waveform
        """
        # Downsample to fit width
        samples = self.downsample_for_display(audio_data, self.width)

        # Create empty canvas
        canvas = [[' ' for _ in range(self.width)] for _ in range(self.height)]

        # Draw center line
        center = self.height // 2
        for x in range(self.width):
            canvas[center][x] = '─'

        # Draw waveform
        for x, sample in enumerate(samples):
            # Map sample to height
            y_offset = int(sample * (self.height // 2))
            y = center - y_offset

            # Clamp to canvas bounds
            y = max(0, min(self.height - 1, y))

            # Draw vertical line from center to sample
            if y < center:
                for yi in range(y, center):
                    canvas[yi][x] = '│'
            elif y > center:
                for yi in range(center + 1, y + 1):
                    canvas[yi][x] = '│'

            # Mark the peak
            canvas[y][x] = '█'

        # Convert canvas to strings
        return [''.join(row) for row in canvas]

    def create_spectrum_bars(self, audio_data: np.ndarray, num_bars: int = 40) -> List[str]:
        """
        Create spectrum analyzer style bars.

        Args:
            audio_data: Audio samples
            num_bars: Number of frequency bars

        Returns:
            List of strings representing the spectrum
        """
        # Perform FFT
        fft = np.fft.rfft(audio_data)
        magnitudes = np.abs(fft)

        # Split into frequency bands
        chunk_size = len(magnitudes) // num_bars
        bars = []

        for i in range(num_bars):
            start = i * chunk_size
            end = start + chunk_size
            # Take mean of the band
            band_magnitude = np.mean(magnitudes[start:end])
            bars.append(band_magnitude)

        # Normalize bars
        max_magnitude = max(bars) if max(bars) > 0 else 1
        bars = [b / max_magnitude for b in bars]

        # Create visualization
        lines = []
        for level in range(self.height - 1, -1, -1):
            line = ""
            threshold = level / self.height
            for bar_value in bars:
                if bar_value >= threshold:
                    line += "█"
                else:
                    line += " "
            lines.append(line)

        return lines

    def create_oscilloscope(self, audio_data: np.ndarray) -> List[str]:
        """
        Create oscilloscope-style visualization showing waveform details.

        Args:
            audio_data: Audio samples

        Returns:
            List of strings representing the oscilloscope view
        """
        # Take a window of samples
        window_size = min(len(audio_data), self.width * 10)
        samples = self.downsample_for_display(audio_data[:window_size], self.width)

        # Create canvas
        canvas = [[' ' for _ in range(self.width)] for _ in range(self.height)]

        # Draw grid
        center = self.height // 2
        for x in range(0, self.width, 10):
            for y in range(self.height):
                canvas[y][x] = '┊'

        for y in range(0, self.height, 5):
            for x in range(self.width):
                if canvas[y][x] == '┊':
                    canvas[y][x] = '┼'
                else:
                    canvas[y][x] = '┈'

        # Draw waveform on top
        for x in range(len(samples) - 1):
            y1 = int(center - samples[x] * (self.height // 2 - 1))
            y2 = int(center - samples[x + 1] * (self.height // 2 - 1))

            # Clamp
            y1 = max(0, min(self.height - 1, y1))
            y2 = max(0, min(self.height - 1, y2))

            # Draw line
            if y1 == y2:
                canvas[y1][x] = '━'
            else:
                step = 1 if y2 > y1 else -1
                for y in range(y1, y2 + step, step):
                    canvas[y][x] = '┃'

        return [''.join(row) for row in canvas]
