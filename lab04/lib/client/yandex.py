from abc import ABC, abstractmethod
from functools import cached_property
from typing import Any

from lab04.lib.client.abc import BaseLLMClient


class YandexFoundationModelsClient(BaseLLMClient, ABC):
    """
    Клиент к Yandex Foundation Models (Yandex Cloud)

    Yandex Foundation Models — это сервис больших генеративных моделей. Yandex Cloud предоставляет доступ к нейросетям
    YandexGPT, YandexART, а также некоторым другим open-source моделям
    """

    URL = 'https://llm.api.cloud.yandex.net/foundationModels/v1/completion'

    def __init__(self, folder: str, token: str):
        self.folder = folder
        self.token = token

    @property
    @abstractmethod
    def model(self) -> str:
        pass

    @cached_property
    def headers(self) -> dict[str, str]:
        return {'Authorization': f'Api-Key {self.token}', 'x-folder-id': self.folder}

    def _prepare_json(self, system_prompt: str, text: str, max_tokens: int, temperature: float) -> dict[str, Any]:
        return {
            'modelUri': f'gpt://{self.folder}/{self.model}',
            'completionOptions': {'maxTokens': max_tokens, 'temperature': temperature},
            'messages': [
                {'role': 'system', 'text': system_prompt},
                {'role': 'user', 'text': text},
            ],
        }

    def _parse_json(self, data: dict) -> str:
        return data['result']['alternatives'][0]['message']['text']
