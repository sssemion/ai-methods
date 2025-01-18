from functools import cached_property
from pathlib import Path

import omnizart
from omnizart.music import MusicTranscription

MODELS = {
    'piano (Pretrained)': '/home/ssemion/venv8/lib/python3.8/site-packages/omnizart/checkpoints/music/music_piano',
    'piano (Finetiuned)': 'cw/model',
}

class Service:
    @cached_property
    def transcription(self):
        return MusicTranscription()

    def transcribe(self, model: str, wav_path: Path, mid_path: Path) -> None:
        self.transcription.transcribe(
            str(wav_path),
            model_path=MODELS[model],
            output=str(mid_path),
        )
