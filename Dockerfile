# Stages 1 & 2: Sound file visualizer + Live microphone visualization
FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Install system dependencies for audio processing
RUN apt-get update && apt-get install -y \
    libsndfile1 \
    portaudio19-dev \
    alsa-utils \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first for better caching
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY src/ ./src/
COPY main.py .

# Create directory for audio files
RUN mkdir -p /audio

# Set environment variables
ENV PYTHONUNBUFFERED=1

# Make main.py executable
RUN chmod +x main.py

# Default command shows help
ENTRYPOINT ["python", "main.py"]
CMD ["--help"]
