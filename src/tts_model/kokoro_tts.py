import asyncio
from dataclasses import dataclass
from typing import AsyncGenerator, Generator, Literal, Optional

import numpy as np
from kokoro import KPipeline
from numpy.typing import NDArray

KokoroModelName = Literal["hexgrad/Kokoro-82M"]


@dataclass
class KokoroTTSOptions:
    lang_code: str = "a"  # 'a' = American English
    voice: str = "af_bella"  # change based on available voices
    speed: float = 1.0  # not used directly in Kokoro (for future use)
    volume: float = 1.0  # manual gain scaling (optional)


class KokoroTTS:
    def __init__(
        self,
        model_name: Optional[KokoroModelName] = "hexgrad/Kokoro-82M",
        options: Optional[KokoroTTSOptions] = None,
    ):
        self.options = options or KokoroTTSOptions()
        self.pipeline = KPipeline(repo_id=model_name, lang_code=self.options.lang_code)
        self.sample_rate = 24000  # fixed for Kokoro

    def tts(
        self, text: str, options: Optional[KokoroTTSOptions] = None
    ) -> tuple[int, NDArray[np.float32]]:
        options = options or self.options
        audio = None
        for _, _, chunk in self.pipeline(text, voice=options.voice):
            if audio is None:
                audio = chunk
            else:
                audio = np.concatenate([audio, chunk], axis=0)

        # Apply volume gain if needed
        audio = audio * options.volume
        return self.sample_rate, audio.cpu().numpy().astype(np.float32)

    async def stream_tts(
        self, text: str, options: Optional[KokoroTTSOptions] = None
    ) -> AsyncGenerator[tuple[int, NDArray[np.float32]], None]:
        sample_rate, audio = self.tts(text, options)
        chunk_size = int(sample_rate * 0.2)
        for i in range(0, len(audio), chunk_size):
            await asyncio.sleep(0.1)
            yield sample_rate, audio[i : i + chunk_size]

    def stream_tts_sync(
        self, text: str, options: Optional[KokoroTTSOptions] = None
    ) -> Generator[tuple[int, NDArray[np.float32]], None, None]:
        sample_rate, audio = self.tts(text, options)
        chunk_size = int(sample_rate * 0.2)
        for i in range(0, len(audio), chunk_size):
            yield sample_rate, audio[i : i + chunk_size]
