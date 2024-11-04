import csv
import json
import os
import sys
from abc import ABC, abstractmethod
from collections import defaultdict
from dataclasses import dataclass
from datetime import datetime
from functools import cached_property
from typing import Any, Iterator

import requests
import streamlit as st

PROMPT = """Найди все упомянутые даты и время в тексте. Верни ответ в формате списка json, содержащего строки в формате 
ISO 8601. Пример ответа: ["2024-09-30T01:16:00", "2025-01-01", "14:56:06"}]. 
Если дат в тексте нет, верни пустой список []. Если в тексте содержится относительная дата, например "завтра", 
считай, что сегодня 1 января 2024 года. Если время не привязано к дате, верни просто время, например "12:30"
"""


@dataclass
class TextItem:
    text: str
    entities: set[str]


class Dataset:
    """Загружает датасет из файла"""
    def __init__(self, filename: str, csv_delimiter: str = ';'):
        self.filename = filename
        self.delimiter = csv_delimiter

    def __iter__(self) -> Iterator[TextItem]:
        with open(self.filename) as fd:
            reader = csv.reader(fd, delimiter=self.delimiter)
            for row in reader:
                text, entities = row
                yield TextItem(text, set(json.loads(entities)))


class BaseGPTClient(ABC):
    """Базовый клиент к GPT-модели для поиска именованных сущностей"""

    @property
    @abstractmethod
    def name(self) -> str:
        pass

    @abstractmethod
    def _get_json(self, text: str) -> dict[str, str]:
        pass

    @abstractmethod
    def find_entities(self, text: str) -> Iterator[str]:
        pass

    @property
    @abstractmethod
    def headers(self) -> dict[str, str]:
        pass

    @property
    @abstractmethod
    def URL(self) -> str:
        pass

    def make_request(self, text: str) -> dict[str, Any]:
        r = requests.post(self.URL, json=self._get_json(text), headers=self.headers)
        r.raise_for_status()
        return r.json()


class YandexGPTClient(BaseGPTClient):
    """Клиент к YandexGPT (Yandex Cloud)"""
    URL = 'https://llm.api.cloud.yandex.net/foundationModels/v1/completion'

    @property
    def name(self) -> str:
        return f'YandexGPT [{self.model}]'

    def __init__(self, folder: str, token: str, model: str = 'yandexgpt-lite/latest'):
        self.folder = folder
        self.token = token
        self.model = model

    @cached_property
    def headers(self) -> dict[str, str]:
        return {'Authorization': f'Bearer {os.getenv("YC_TOKEN")}', 'x-folder-id': self.folder}

    def _get_json(self, text: str) -> dict[str, Any]:
        return {
            'modelUri': f'gpt://{self.folder}/{self.model}',
            'completionOptions': {'maxTokens': 500, 'temperature': 0},
            'messages': [
                {'role': 'system', 'text': PROMPT},
                {'role': 'user', 'text': text},
            ],
        }

    def find_entities(self, text: str) -> Iterator[str]:
        data = self.make_request(text)
        yield from json.loads(data['result']['alternatives'][0]['message']['text'])


class ChatGPTClient(BaseGPTClient):
    """Клиент к ChatGPT (Rapid API)"""
    URL = 'https://chatgpt-42.p.rapidapi.com/chatgpt'
    name = 'ChatGPT 3.5'

    def __init__(self, token: str):
        self.token = token

    @cached_property
    def headers(self) -> dict[str, str]:
        return {'x-rapidapi-host': 'chatgpt-42.p.rapidapi.com', 'x-rapidapi-key': self.token}

    def _get_json(self, text: str) -> dict[str, Any]:
        return {
            "model": "gpt-3.5-turbo",
            'messages': [
                {'role': 'system', 'content': PROMPT},
                {'role': 'user', 'content': text},
            ],
            "max_new_tokens": 100, "temperature": 0, "top_p": 0.7, "top_k": 50, "repetition_penalty": 0,
            "stop": ["<|im_start|>", "<|im_end|>"]
        }

    def find_entities(self, text: str) -> Iterator[str]:
        data = self.make_request(text)
        yield from json.loads(data['result'])


def calc_score(models: list[BaseGPTClient]) -> None:
    """Загружает датасет и считает метрики для каждой модели"""
    scores = defaultdict(int)
    dataset = Dataset('ai/lab01_data.csv')
    for i, item in enumerate(dataset, 1):
        for model in models:
            print(f'[{i}] Делаем запрос в {model.name}')
            result = set(model.find_entities(item.text))

            if item.entities:
                scores[model] += len(result & item.entities) / len(item.entities)
            else:
                scores[model] += (1 - bool(item.entities))

    for model, score in scores.items():
        print(f'Total {model.name} score: {score / i * 100:.2f}%')


def gui(models: list[BaseGPTClient]) -> None:
    """Инициализирует streamlit GUI"""
    q = st.text_area("Введите текст")
    button = st.button("Найти даты")
    if button:
        if q:
            for model in models:
                st.markdown(f'###### {model.name}')
                with st.spinner():
                    dates = []
                    for item in model.find_entities(q):
                        try:
                            d = datetime.fromisoformat(item)
                        except ValueError:
                            d = f'{item} [Invalid ISO format]'
                        dates.append(d)
                if not dates:
                    st.write('Дат не найдено')
                else:
                    st.write(*dates)
        else:
            st.error('Поле не заполнено')


def main():
    models = [
        YandexGPTClient(folder=os.getenv('YC_FOLDER'), token=os.getenv('YC_TOKEN')),
        YandexGPTClient(folder=os.getenv('YC_FOLDER'), token=os.getenv('YC_TOKEN'), model='yandexgpt/latest'),
        ChatGPTClient(token=os.getenv('RAPIDAPI_CHATGPT_TOKEN')),
    ]
    _, *args = sys.argv
    if not args:
        return gui(models)
    if len(args) == 1 and args[0] == 'metrics':
        return calc_score(models)
    raise Exception('Invalid args')


if __name__ == '__main__':
    main()
    # Привет! Сегодня мой первый рабочий день, а уже 20 числа будет первая зарплата
