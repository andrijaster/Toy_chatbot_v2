import asyncio
import numpy as np
from dataclasses import dataclass
from numpy.typing import NDArray
from typing import Optional, AsyncGenerator, Generator


@dataclass
class SimpleTTSOptions:
    pitch: float = 1.0  # 1.0 = normal pitch
    speed: float = 1.0  # 1.0 = normal speed (higher = shorter duration)
    volume: float = 1.0  # 1.0 = normal volume


class SimpleTTS:
    def __init__(self, sample_rate: int = 24000):
        self.sample_rate = sample_rate

    def tts(
        self, text: str, options: Optional[SimpleTTSOptions] = None
    ) -> tuple[int, NDArray[np.float32]]:
        options = options or SimpleTTSOptions()

        # Apply speed: faster speech = shorter duration
        duration = max(0.3, 1.0 / options.speed)
        t = np.linspace(0, duration, int(self.sample_rate * duration), endpoint=False)

        # Apply pitch: modify frequency
        base_freq = 220.0
        freq = base_freq * options.pitch

        # Apply volume
        audio = options.volume * 0.3 * np.sin(2 * np.pi * freq * t).astype(np.float32)

        return self.sample_rate, audio

    async def stream_tts(
        self, text: str, options: Optional[SimpleTTSOptions] = None
    ) -> AsyncGenerator[tuple[int, NDArray[np.float32]], None]:
        sample_rate, audio = self.tts(text, options)
        chunk_size = int(sample_rate * 0.2)
        for i in range(0, len(audio), chunk_size):
            await asyncio.sleep(0.1)
            yield sample_rate, audio[i : i + chunk_size]

    def stream_tts_sync(
        self, text: str, options: Optional[SimpleTTSOptions] = None
    ) -> Generator[tuple[int, NDArray[np.float32]], None, None]:
        sample_rate, audio = self.tts(text, options)
        chunk_size = int(sample_rate * 0.2)
        for i in range(0, len(audio), chunk_size):
            yield sample_rate, audio[i : i + chunk_size]
