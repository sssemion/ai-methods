from abc import ABC, abstractmethod
from functools import cached_property
from typing import Any

from lab04.lib.client.abc import BaseLLMClient


class VsegptClient(BaseLLMClient, ABC):
    """
    Абстрактный клиент к VseGpt API

    Vsegpt - сервис-агрегатор, который позволяет подключиться к chatGPT и другим современным нейросетям для генерации
    текста
    """

    URL = 'https://api.vsegpt.ru/v1/chat/completions'

    def __init__(self, token: str):
        self.token = token

    @cached_property
    def headers(self) -> dict[str, str]:
        return {'Authorization': f'Bearer {self.token}'}

    @property
    @abstractmethod
    def model(self) -> str:
        pass

    def _prepare_json(self, system_prompt: str, text: str, max_tokens: int, temperature: float) -> dict[str, Any]:
        return {
            'model': self.model,
            'messages': [
                {'role': 'system', 'content': system_prompt},
                {'role': 'user', 'content': text},
            ],
            'max_new_tokens': max_tokens,
            'temperature': temperature,
        }

    def _parse_json(self, data: dict) -> str:
        return data['choices'][0]['message']['content']
