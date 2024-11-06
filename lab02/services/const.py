from dataclasses import dataclass
from typing import Generic, TypeVar

from lab02.services.sberdevices import SberDevicesRuGPT3Small, SberDevicesRuGPT3Medium

MODELS = {model.MODEL_NAME: model for model in (
    SberDevicesRuGPT3Small(),
    SberDevicesRuGPT3Medium(),
)}


T = TypeVar('T', int, float)

@dataclass
class ParamSpec(Generic[T]):
    """Конфиг параметра генерации"""
    min: T
    max: T
    step: T
    default: T


GENERATIVE_PARAMS: dict[str, ParamSpec] = {
    'max_length': ParamSpec(50, 2000, 50, 500),
    'temperature': ParamSpec(0.0, 5.0, 0.05, 1.0),
    'top_k': ParamSpec(0, 100, 1, 50),
    'top_p': ParamSpec(0.0, 1.0, 0.05, 0.9),
    'repetition_penalty': ParamSpec(1.0, 2.0, 0.05, 1.2),
}

BASE_TEXT = """
ОТЧЕТ
ПО КУРСОВОЙ НАУЧНО-ИССЛЕДОВАТЕЛЬСКОЙ РАБОТЕ
на тему:
"Применение методов машинного обучения для детектирования аномалий во временных рядах метрик информационных систем"

ЦЕЛИ И ЗАДАЧИ\n
Целью данной работы является изучение и применение методов машинного обучения для анализа временных рядов метрик 
информационных систем и детектирования аномалий с целью повышения его надежности и стабильности. Для достижения этой 
цели, необходимо решить следующие задачи:
""".strip()