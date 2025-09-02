FROM python:3.11.13-slim

# Set working directory
WORKDIR /app

# Install system packages if needed (adjust if fastrtc/langgraph require others)
RUN apt-get update && apt-get install -y \
    libssl-dev \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Pre-download models
RUN python -c "from fastrtc import get_stt_model, get_tts_model; get_stt_model(); get_tts_model()"

# Copy source code
COPY ./src ./src

# Expose FastAPI port
EXPOSE 7861
EXPOSE 7862

# Run your FastAPI server
CMD ["python", "src/server.py"]
