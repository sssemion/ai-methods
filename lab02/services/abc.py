from abc import ABC, abstractmethod
from functools import cached_property
from typing import cast

import torch
from transformers import GPT2Tokenizer, GPT2LMHeadModel


class BaseGPTService(ABC):
    """Базовый класс для сервиса GPT-моделей"""

    @property
    @abstractmethod
    def MODEL_NAME(self) -> str:
        """Название модели"""

    @cached_property
    def tokenizer(self) -> GPT2Tokenizer:
        """Токенайзер"""
        return GPT2Tokenizer.from_pretrained(self.MODEL_NAME)

    @cached_property
    def model(self) -> GPT2LMHeadModel:
        """Модель"""
        return GPT2LMHeadModel.from_pretrained(self.MODEL_NAME)

    def send_message(self,
                     text: str,
                     max_length: int,
                     temperature: float,
                     top_k: int,
                     top_p: float,
                     repetition_penalty: float,
                     ) -> str:
        """
        Интерфейс взаимодействия с GPT-моделью, генерирует текст на основе входной строки
        Params:
            text: Начальный текст, с которого начинается генерация.
            max_length: Максимальная длина генерируемой последовательности токенов.
            temperature: Значение температуры для управления креативностью генерации (значения ниже 1.0 приводят к более
                детерминированным результатам, значения выше 1.0 — к более случайным).
            top_k: Параметр, ограничивающий количество возможных токенов для выбора на каждом шаге семплирования.
            top_p: Параметр nucleus sampling, ограничивающий выбор токенов по совокупной вероятности.
            repetition_penalty: Штраф за повторение токенов, используемый для снижения вероятности повторов в выходном
                тексте
        """
        input_ids = cast(torch.Tensor, self.tokenizer.encode(text, return_tensors='pt'))
        out = self.model.generate(input_ids,
                                  do_sample=True,
                                  max_length=max_length,
                                  temperature=temperature,
                                  top_k=top_k,
                                  top_p=top_p,
                                  repetition_penalty=repetition_penalty,
                                  )
        return '\n'.join(list(map(self.tokenizer.decode, out)))
