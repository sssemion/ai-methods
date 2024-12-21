from abc import ABC, abstractmethod

from aiohttp import ClientSession


class BaseLLMClient(ABC):
    """Базовый клиент к LLM-модели"""

    @property
    @abstractmethod
    def name(self) -> str:
        pass

    @abstractmethod
    def _prepare_json(self, system_prompt: str, text: str, max_tokens: int, temperature: float) -> dict[str, str]:
        pass

    @property
    @abstractmethod
    def headers(self) -> dict[str, str]:
        pass

    @property
    @abstractmethod
    def URL(self) -> str:
        pass

    async def request(self, system_prompt: str, text: str, max_tokens: int = 500, temperature: float = 0.3) -> str:
        async with ClientSession() as session:
            async with session.post(
                self.URL,
                json=self._prepare_json(system_prompt, text, max_tokens, temperature),
                headers=self.headers,
            ) as r:
                r.raise_for_status()
                return self._parse_json(await r.json())

    @abstractmethod
    def _parse_json(self, data: dict) -> str:
        pass
