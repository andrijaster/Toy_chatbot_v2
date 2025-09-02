# Voice Features

## Overview

The storytelling assistant supports voice interaction through Speech-to-Text (STT) and Text-to-Speech (TTS) using the `fastrtc` library.

## Architecture

### VoiceProcessor Class
Located in `src/voice.py` - centralizes all voice operations:

```python
from src.voice import get_voice_processor

voice = get_voice_processor()
text = voice.speech_to_text(audio)
audio_chunks = voice.text_to_speech("Hello!")
```

### Key Methods
- `speech_to_text(audio)` - Convert audio to text
- `text_to_speech(text)` - Convert text to audio chunks
- `speak(text)` - Alias for text_to_speech

## Integration Points

### Server Module (`src/server.py`)
- Voice processor initialized at startup
- Audio processing in `process_audio_response()` function
- STT for user input, TTS for AI responses

### Error Handling
- Graceful fallback on STT/TTS failures
- Comprehensive logging for debugging
- Model initialization validation at startup

## Voice Workflow

1. **Audio Input** → STT processing → Text extraction
2. **Text Processing** → Story generation via LangGraph
3. **Response Generation** → TTS processing → Audio chunks
4. **Streaming Output** → Real-time audio playback

## Session Management

Voice sessions support:
- Story continuation detection
- New story initialization via voice commands
- Session reset with "new story" voice trigger
- User confirmation for story continuation

## Configuration

Voice models auto-initialize through `fastrtc`:
- No additional configuration required
- Models cached after first initialization
- Automatic error recovery and logging