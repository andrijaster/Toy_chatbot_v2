#!/usr/bin/env python3
"""
Simple FastRTC STT/TTS Demo
Using FastRTC Stream interface with custom models
"""

import os
import sys

import numpy as np
from fastrtc import (
    AdditionalOutputs,
    AlgoOptions,
    ReplyOnPause,
    SileroVadOptions,
    Stream,
)

sys.path.append(os.path.join(os.path.dirname(__file__), "..", "src"))

from sst_model.WhisperSTT import WhisperSTT
from tts_model.kokoro_tts import KokoroTTS, KokoroTTSOptions


class SimpleDemo:
    def __init__(self):
        print("Loading models...")
        self.stt_model = WhisperSTT("openai/whisper-medium.en")
        self.tts_model = KokoroTTS()
        print("Models loaded successfully!")

    def response_handler(self, audio: tuple[int, np.ndarray]):
        """Handle audio input and generate response."""
        text = self.stt_model.stt(audio)
        print(f"📝 You said: {text}")

        # Yield transcription info
        yield AdditionalOutputs(f"Transcription: {text}")

        # Echo back the text
        response_text = f"You said: {text}"

        # Generate TTS response
        tts_options = KokoroTTSOptions(
            lang_code="a",  # American English
            voice="bm_george",
            speed=1.0,
            volume=1.0,
        )

        print("🔊 Speaking response...")
        for chunk in self.tts_model.stream_tts_sync(response_text, tts_options):
            yield chunk

    def run_demo(self):
        """Run the streaming demo."""
        print("=" * 50)
        print("  FastRTC Streaming Demo")
        print("=" * 50)
        print("This will open a web interface.")
        print("Speak and the system will echo back what you said.")

        stream = Stream(
            handler=ReplyOnPause(
                self.response_handler,
                algo_options=AlgoOptions(
                    audio_chunk_duration=0.6,
                    started_talking_threshold=0.2,
                    speech_threshold=0.1,
                ),
                model_options=SileroVadOptions(
                    threshold=0.5,
                    min_speech_duration_ms=250,
                    min_silence_duration_ms=100,
                ),
                can_interrupt=True,
                input_sample_rate=16000,
                expected_layout="mono",
            ),
            modality="audio",
            additional_outputs_handler=lambda old, new: old + new,
            additional_outputs=[
                __import__("gradio").Textbox(label="Transcription", interactive=False)
            ],
        )

        print("Launching web interface...")
        stream.ui.launch(share=True)


def main():
    """Main function."""
    try:
        demo = SimpleDemo()
        demo.run_demo()
    except KeyboardInterrupt:
        print("\nBye!")
    except Exception as e:
        print(f"Error: {e}")


if __name__ == "__main__":
    main()
