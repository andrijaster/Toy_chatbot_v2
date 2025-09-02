"""
Voice processing module for STT and TTS operations.
Handles speech-to-text and text-to-speech functionality using fastrtc.
"""

import logging
from typing import Generator, Optional

from fastrtc import get_stt_model, get_tts_model

logger = logging.getLogger(__name__)


class VoiceProcessor:
    """Handles speech-to-text and text-to-speech operations."""

    def __init__(self):
        """Initialize STT and TTS models."""
        try:
            self.stt_model = get_stt_model()
            self.tts_model = get_tts_model()
            logger.info("Voice models initialized successfully")
        except Exception as e:
            logger.exception("Error initializing voice models: %s", e)
            raise

    def speech_to_text(self, audio) -> str:
        """Convert audio to text using STT model."""
        try:
            return self.stt_model.stt(audio)
        except Exception as e:
            logger.exception("STT processing failed: %s", e)
            return ""

    def text_to_speech(self, text: str) -> Generator[bytes, None, None]:
        """Convert text to speech chunks using TTS model."""
        try:
            for chunk in self.tts_model.stream_tts_sync(text):
                yield chunk
        except Exception as e:
            logger.exception("TTS processing failed: %s", e)
            return

    def speak(self, text: str) -> Generator[bytes, None, None]:
        """Convenience method for text-to-speech."""
        return self.text_to_speech(text)


# Global voice processor instance
voice_processor: Optional[VoiceProcessor] = None


def get_voice_processor() -> VoiceProcessor:
    """Get or create the global voice processor instance."""
    global voice_processor
    if voice_processor is None:
        voice_processor = VoiceProcessor()
    return voice_processor


def initialize_voice_models() -> VoiceProcessor:
    """Initialize voice models and return processor instance."""
    return get_voice_processor()
