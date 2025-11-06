# 🎵 Claude AI Agent LoFi

A lofi Claude AI agent that runs on command line - visualize audio, interact with voice, and chat with AI.

## 🌟 Project Stages

### ✅ Stage 1: CLI Sound File Visualizer
Visualize audio files in your terminal with multiple visualization modes:
- **Waveform View**: See the amplitude over time
- **Spectrum Analyzer**: Frequency spectrum visualization
- **Oscilloscope View**: Detailed waveform with grid overlay

### ✅ Stage 2: Real-Time Voice Visualization (Current)
- Capture audio from microphone in real-time
- Live voice wave visualization as you speak
- Interactive audio level monitoring with VU meters
- Multiple visualization modes (waveform, spectrum, oscilloscope)
- Device selection and configuration
- Peak and RMS level indicators with color coding

### 🚧 Stage 3: AI Personal Assistant (Planned)
- Speech-to-text using OpenAI Whisper
- Integration with Claude AI API
- Conversational AI assistant interface
- Voice commands and responses

## 🚀 Quick Start

### Prerequisites
- Python 3.11+
- Docker (optional, for containerized usage)

### Local Installation

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd claude-ai-agent-lofi
   ```

2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Generate a sample audio file**
   ```bash
   python generate_sample.py
   ```

4. **Run the visualizer**
   ```bash
   # Waveform view (default)
   python main.py samples/sample_tone.wav

   # Spectrum analyzer
   python main.py samples/sample_tone.wav --mode spectrum

   # Oscilloscope view
   python main.py samples/sample_tone.wav --mode oscilloscope
   ```

5. **Try live microphone visualization (Stage 2)**
   ```bash
   # List available audio input devices
   python main.py --list-devices

   # Live microphone visualization
   python main.py --live

   # Live with spectrum analyzer
   python main.py --live --mode spectrum

   # Use specific audio device
   python main.py --live --device 1
   ```

### Docker Usage

1. **Build the Docker image**
   ```bash
   docker build -t claude-ai-agent-lofi .
   ```

2. **Run with your audio file**
   ```bash
   # Create samples directory if it doesn't exist
   mkdir -p samples

   # Copy your audio file to samples/
   # Then run the container
   docker run -it --rm -v $(pwd)/samples:/audio claude-ai-agent-lofi /audio/your_file.wav
   ```

3. **Using Docker Compose**
   ```bash
   # Build and run
   docker-compose build

   # Visualize an audio file
   docker-compose run --rm lofi-agent /audio/sample_tone.wav

   # With different modes
   docker-compose run --rm lofi-agent /audio/sample_tone.wav --mode spectrum
   docker-compose run --rm lofi-agent /audio/sample_tone.wav --mode oscilloscope

   # Stage 2: Live microphone (requires audio device access)
   docker-compose run --rm lofi-agent --live
   docker-compose run --rm lofi-agent --live --mode spectrum
   ```

## 📖 Usage Examples

### Stage 1: File Visualization

#### Basic Visualization
```bash
python main.py my_audio.wav
```

#### Spectrum Analyzer Mode
```bash
python main.py my_audio.wav --mode spectrum
```

#### Oscilloscope Mode
```bash
python main.py my_audio.wav --mode oscilloscope
```

### Stage 2: Live Microphone

#### List Available Devices
```bash
python main.py --list-devices
```

#### Live Waveform
```bash
python main.py --live
```

#### Live Spectrum Analyzer
```bash
python main.py --live --mode spectrum
```

#### Live Oscilloscope
```bash
python main.py --live --mode oscilloscope
```

#### Use Specific Device
```bash
python main.py --live --device 1
```

#### Adjust Refresh Rate
```bash
python main.py --live --refresh-rate 0.1  # Slower refresh
python main.py --live --refresh-rate 0.02  # Faster refresh
```

### Help
```bash
python main.py --help
```

## 🎨 Visualization Modes

### Waveform View 🌊
Displays the audio waveform showing amplitude changes over time. Great for seeing the overall structure and dynamics of your audio.

### Spectrum Analyzer 📊
Shows frequency distribution using FFT (Fast Fourier Transform). Visualizes the audio as frequency bars - perfect for analyzing the frequency content.

### Oscilloscope View 〰️
Detailed waveform view with a grid overlay, similar to a real oscilloscope. Useful for examining the precise shape of the audio signal.

## 🏗️ Project Structure

```
claude-ai-agent-lofi/
├── src/
│   ├── __init__.py           # Package initialization
│   ├── visualizer.py         # Audio visualization logic
│   ├── audio_input.py        # Audio file and mic input handling
│   ├── speech_to_text.py     # Stage 3: STT (planned)
│   └── assistant.py          # Stage 3: Claude AI (planned)
├── main.py                   # Main entry point
├── generate_sample.py        # Generate test audio files
├── requirements.txt          # Python dependencies
├── Dockerfile               # Docker container definition
├── docker-compose.yml       # Docker Compose configuration
├── .dockerignore           # Docker ignore file
├── .gitignore              # Git ignore file
└── README.md               # This file
```

## 🔧 Supported Audio Formats

- WAV (.wav)
- FLAC (.flac)
- OGG (.ogg)
- MP3 (.mp3)

## 📋 Requirements

### Stages 1 & 2 (Current)
- numpy>=1.24.0
- soundfile>=0.12.0
- rich>=13.7.0
- pyaudio>=0.2.13

### System Dependencies (for Stage 2)
- portaudio19-dev (Linux)
- PortAudio (macOS: `brew install portaudio`)
- PyAudio wheels (Windows)

### Stage 3 (Planned)
- openai-whisper>=20231117
- anthropic>=0.18.0

## 🛠️ Development

### Running Tests
```bash
# Generate sample audio for testing
python generate_sample.py

# Test Stage 1: File visualization modes
python main.py samples/sample_tone.wav --mode waveform
python main.py samples/sample_tone.wav --mode spectrum
python main.py samples/sample_tone.wav --mode oscilloscope

# Test Stage 2: Live microphone
python main.py --list-devices  # List available devices
python main.py --live  # Start live visualization
```

### Contributing
Contributions are welcome! This project is in active development.

## 🗺️ Roadmap

- [x] Stage 1: Basic audio file visualization
  - [x] Waveform visualization
  - [x] Spectrum analyzer
  - [x] Oscilloscope view
  - [x] Docker support
- [x] Stage 2: Real-time voice input
  - [x] Microphone capture with PyAudio
  - [x] Live visualization with all three modes
  - [x] Audio level monitoring (Peak & RMS)
  - [x] VU meters with color coding
  - [x] Device selection and configuration
  - [x] Real-time audio streaming
- [ ] Stage 3: AI Assistant
  - [ ] Speech-to-text integration
  - [ ] Claude AI API integration
  - [ ] Conversational interface
  - [ ] Voice command system

## 📝 License

This project is open source and available under the MIT License.

## 🙏 Acknowledgments

- Built with Python and Rich for beautiful terminal output
- Audio processing powered by NumPy and libsndfile
- Future AI capabilities powered by Anthropic's Claude

## 💡 Tips

- For best visualization results, use audio files with varied dynamics
- Terminal width affects visualization quality - wider terminals show more detail
- Try different modes to see different aspects of your audio
- Mono audio files work best; stereo files are automatically converted to mono

## 🐛 Troubleshooting

### Stage 1 Issues

#### "Audio file not found"
Make sure the file path is correct and the file exists.

#### "Unsupported audio format"
Check that your file is in WAV, FLAC, OGG, or MP3 format.

#### Docker volume issues
Ensure your audio files are in the `samples/` directory when using Docker.

### Stage 2 Issues

#### "No audio input devices found"
- **Linux**: Make sure ALSA is installed and your microphone is connected
- **macOS**: Grant microphone permissions in System Preferences → Security & Privacy
- **Docker**: Ensure you're using `--device /dev/snd:/dev/snd` flag or the docker-compose configuration

#### PyAudio installation errors
- **Linux**: Install `portaudio19-dev` first: `sudo apt-get install portaudio19-dev`
- **macOS**: Install PortAudio: `brew install portaudio`
- **Windows**: Use pre-built PyAudio wheels

#### "Permission denied" accessing microphone
- Check that your user has permissions to access audio devices
- On Linux, add your user to the `audio` group: `sudo usermod -a -G audio $USER`

### Stage 3 Issue

### No pyaudio could not import _portaudio
- Conduct steps as outlined https://stackoverflow.com/questions/36681836/pyaudio-could-not-import-portaudio.

## 📞 Contact & Support

For issues, questions, or contributions, please open an issue on the repository.

---

**Current Version**: 0.2.0 (Stage 2)
**Status**: Active Development 🚀
