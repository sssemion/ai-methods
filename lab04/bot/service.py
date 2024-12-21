import os

from lab04.bot import locals
from lab04.bot.clients import LlamaClient, GPTClient
from lab04.lib.client.abc import BaseLLMClient

SYSTEM_PROMPT = '''\
Ответь текстом без форматирования. Вместо этого добавь эмодзи к каждому логическому пункту ответа. Будь лаконичен'
'''

PROMPT_TEMPLATE = '''\
Пользователь ищет автомобиль и предоставил следующую информацию (прочерк означает, что параметр не важен):
- Тип автомобиля: {vehicle_type}
- Бюджет: {budget}
- Цели использования: {purpose}
- Важные характеристики: {features}
- Предпочтение по состоянию авто: {condition}
- Предпочитаемые марки или модели: {models}

На основе этой информации, предложи 3 модели автомобилей, которые соответствуют критериям пользователя. \
Объясни преимущества каждой модели с учетом бюджета, целей использования и значимых характеристик. Если возможно, \
укажи недостатки, на которые стоит обратить внимание, и предложи лучший выбор среди указанных вариантов. Также для \
каждого варианта напиши примерный ценовой диапазон на рынке, и состояние автомобиля за эти деньги.
'''

class LlmService:
    """Обертка над клиентом к LLM, реализующая логику формирования текстового запроса к модели"""

    def __init__(self, client: BaseLLMClient):
        self.client = client

    async def search_vehicles(
        self,
        budget: str,
        vehicle_type: str,
        purpose: str,
        features: str,
        condition: locals.Condition,
        models: str,
    ) -> str:
        text = PROMPT_TEMPLATE.format(
            budget=budget,
            vehicle_type=vehicle_type,
            purpose=purpose,
            features=features,
            condition=condition,
            models=models,
        )
        return await self.client.request(SYSTEM_PROMPT, text)


AVAILABLE_SERVICES = [
    LlmService(LlamaClient(os.getenv('YC_FOLDER'), os.getenv('YC_TOKEN'))),
    LlmService(GPTClient(os.getenv('VSEGPT_TOKEN'))),  # будет работать до 2024-12-23 23:32:19
]