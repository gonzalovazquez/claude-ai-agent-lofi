# 🎵 Claude AI Agent LoFi

A lofi Claude AI agent that runs on command line - visualize audio, interact with voice, and chat with AI.

## 🌟 Project Stages

### ✅ Stage 1: CLI Sound File Visualizer
Visualize audio files in your terminal with multiple visualization modes:
- **Waveform View**: See the amplitude over time
- **Spectrum Analyzer**: Frequency spectrum visualization
- **Oscilloscope View**: Detailed waveform with grid overlay

### ✅ Stage 2: Real-Time Voice Visualization
- Capture audio from microphone in real-time
- Live voice wave visualization as you speak
- Interactive audio level monitoring with VU meters
- Multiple visualization modes (waveform, spectrum, oscilloscope)
- Device selection and configuration
- Peak and RMS level indicators with color coding

### ✅ Stage 3: AI Personal Assistant (Current)
- Speech-to-text using OpenAI Whisper (local processing)
- Integration with Claude AI API for intelligent responses
- Conversational AI assistant with context memory
- Multiple personality modes (helpful, concise, friendly, professional, lofi)
- Real-time voice visualization during recording
- Voice command recognition (goodbye, clear history, etc.)
- Customizable recording duration and Whisper model selection

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

6. **Try voice assistant mode (Stage 3)**
   ```bash
   # First, set up your Claude API key
   # Option 1: Create a .env file
   cp .env.example .env
   # Edit .env and add your API key: ANTHROPIC_API_KEY=your_key_here

   # Option 2: Set environment variable
   export ANTHROPIC_API_KEY=your_key_here

   # Start the voice assistant
   python main.py --assistant

   # With different personality
   python main.py --assistant --personality friendly

   # With faster/smaller Whisper model
   python main.py --assistant --whisper-model tiny

   # With longer recording duration (10 seconds)
   python main.py --assistant --duration 10
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

### Stage 3: Voice Assistant

#### Basic Voice Assistant
```bash
python main.py --assistant
```

#### With Different Personalities
```bash
python main.py --assistant --personality helpful    # Detailed and informative
python main.py --assistant --personality concise    # Brief responses
python main.py --assistant --personality friendly   # Warm and casual
python main.py --assistant --personality professional  # Formal and structured
python main.py --assistant --personality lofi       # Chill and relaxed (default)
```

#### With Different Whisper Models
```bash
python main.py --assistant --whisper-model tiny     # Fastest, less accurate
python main.py --assistant --whisper-model base     # Balanced (default)
python main.py --assistant --whisper-model small    # Better accuracy
python main.py --assistant --whisper-model medium   # High accuracy
python main.py --assistant --whisper-model large    # Best accuracy, slowest
```

#### With Custom Recording Duration
```bash
python main.py --assistant --duration 3   # 3 second recordings
python main.py --assistant --duration 10  # 10 second recordings
```

#### Combined Options
```bash
python main.py --assistant --personality friendly --whisper-model tiny --duration 7
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
│   ├── speech_to_text.py     # Speech-to-text with Whisper
│   └── assistant.py          # Claude AI assistant integration
├── main.py                   # Main entry point
├── generate_sample.py        # Generate test audio files
├── requirements.txt          # Python dependencies
├── Dockerfile               # Docker container definition
├── docker-compose.yml       # Docker Compose configuration
├── .env.example            # Example environment variables
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

### Python Packages (All Stages)
- numpy>=1.24.0
- soundfile>=0.12.0
- rich>=13.7.0
- pyaudio>=0.2.13 (Stage 2 & 3)
- openai-whisper>=20231117 (Stage 3)
- anthropic>=0.18.0 (Stage 3)
- python-dotenv>=1.0.0 (Stage 3)

### System Dependencies
- **For Stage 2 & 3** (Audio input):
  - Linux: `portaudio19-dev` (`sudo apt-get install portaudio19-dev`)
  - macOS: PortAudio (`brew install portaudio`)
  - Windows: PyAudio wheels (usually pre-built)

- **For Stage 3** (Speech-to-text):
  - FFmpeg (required by Whisper)
  - Linux: `sudo apt-get install ffmpeg`
  - macOS: `brew install ffmpeg`
  - Windows: Download from ffmpeg.org

### API Keys (Stage 3)
- Anthropic API key for Claude AI
- Get it from: https://console.anthropic.com/
- Set as `ANTHROPIC_API_KEY` environment variable or in `.env` file

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

# Test Stage 3: Voice assistant (requires API key in .env)
python main.py --assistant --whisper-model tiny  # Quick test with fastest model
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
- [x] Stage 3: AI Assistant
  - [x] Speech-to-text with OpenAI Whisper (local)
  - [x] Claude AI API integration
  - [x] Conversational interface with history
  - [x] Multiple personality modes
  - [x] Voice command recognition
  - [x] Live visualization during recording
  - [x] Configurable Whisper models
  - [x] Customizable recording duration

## 📝 License

This project is open source and available under the MIT License.

## 🙏 Acknowledgments

- Built with Python and Rich for beautiful terminal output
- Audio processing powered by NumPy and libsndfile
- Speech recognition powered by OpenAI Whisper
- AI capabilities powered by Anthropic's Claude

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

#### PyAudio "could not import _portaudio"
- See troubleshooting steps at: https://stackoverflow.com/questions/36681836/pyaudio-could-not-import-portaudio
- Ensure PortAudio is properly installed before installing PyAudio

### Stage 3 Issues

#### "ANTHROPIC_API_KEY not found"
- Create a `.env` file in the project directory
- Add: `ANTHROPIC_API_KEY=your_key_here`
- Get your API key from: https://console.anthropic.com/

#### Whisper model download issues
- Whisper models are downloaded automatically on first use
- Models are cached in `~/.cache/whisper/`
- Ensure you have internet connection and sufficient disk space
- Model sizes: tiny (~75MB), base (~150MB), small (~500MB), medium (~1.5GB), large (~3GB)

#### "FFmpeg not found" error
- **Linux**: `sudo apt-get install ffmpeg`
- **macOS**: `brew install ffmpeg`
- **Windows**: Download from https://ffmpeg.org/ and add to PATH

#### Slow transcription
- Use a smaller Whisper model: `--whisper-model tiny` or `--whisper-model base`
- Faster models are less accurate but work well for clear speech

#### Claude API errors
- Check your API key is correct
- Verify you have API credits available
- Check your internet connection
- See https://console.anthropic.com/ for API status

#### "No speech detected"
- Speak louder and closer to the microphone
- Check microphone levels in system settings
- Try increasing `--duration` for longer recording time
- Ensure there's minimal background noise

## 📞 Contact & Support

For issues, questions, or contributions, please open an issue on the repository.

---

**Current Version**: 0.3.0 (Stage 3) ✨
**Status**: All Stages Complete! 🎉

Ready to use as a voice-controlled AI assistant!
