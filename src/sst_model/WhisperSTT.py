from typing import Literal, Optional

import numpy as np
import torch
from transformers import AutoProcessor, WhisperForConditionalGeneration

WhisperModelName = Literal[
    "openai/whisper-tiny",
    "openai/whisper-tiny.en",
    "openai/whisper-base",
    "openai/whisper-base.en",
    "openai/whisper-small",
    "openai/whisper-small.en",
    "openai/whisper-medium",
    "openai/whisper-medium.en",
    "openai/whisper-large",
    "openai/whisper-large-v2",
    "openai/whisper-large-v3",
]


class WhisperSTT:
    def __init__(
        self,
        model_name: WhisperModelName = "openai/whisper-medium.en",
        device: Optional[str] = None,
    ):
        self.device = device or ("cuda" if torch.cuda.is_available() else "cpu")
        self.processor = AutoProcessor.from_pretrained(model_name)
        self.model = WhisperForConditionalGeneration.from_pretrained(model_name).to(
            self.device
        )

    def stt(self, audio: tuple[int, np.ndarray]) -> str:
        sample_rate, waveform = audio
        waveform_tensor = torch.from_numpy(waveform).float()

        inputs = self.processor(
            waveform_tensor.squeeze(), sampling_rate=sample_rate, return_tensors="pt"
        ).to(self.device)

        with torch.no_grad():
            predicted_ids = self.model.generate(inputs["input_features"])

        return self.processor.batch_decode(predicted_ids, skip_special_tokens=True)[0]
