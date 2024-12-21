from lab04.lib.client.vsegpt import VsegptClient
from lab04.lib.client.yandex import YandexFoundationModelsClient


class LlamaClient(YandexFoundationModelsClient):
    """Клиент к LLaMa 3.1 8B (Yandex Foundation Models)"""

    name = 'LLaMa 3.1 8B'
    model = 'llama-lite/latest'


class GPTClient(VsegptClient):
    """Клиент к GPT-4o mini (Rapid API)"""

    name = 'GPT-4o mini'
    model = 'openai/gpt-4o-mini'
