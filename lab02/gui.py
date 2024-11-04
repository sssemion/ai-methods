import enum
from abc import ABC, abstractmethod
from datetime import datetime

import streamlit as st


class BaseMessage(ABC):
    """Базовый класс сообщения"""

    class Alignment(enum.StrEnum):
        LEFT = 'left'
        RIGHT = 'right'

    TEXT_ALIGN: Alignment = Alignment.LEFT

    def __init__(self, text: str, ts: datetime | None = None):
        self.text = text
        self.ts = ts or datetime.now()

    @property
    @abstractmethod
    def NAME(self) -> str:
        pass

    @property
    @abstractmethod
    def BG_COLOR(self) -> str:
        pass

    def format(self) -> str:
        """Форматирует сообщение и возвращает html представление для вывода через `st.markdown()`"""
        return f'''
        <div style="text-align: {self.TEXT_ALIGN}; background-color: {self.BG_COLOR}; padding: 10px; border-radius: 5px; margin-bottom: 10px;">
            <span style="font-weight: bold;">{self.NAME}:</span> {self.text}<br>
            <span style="font-size: small;">{self.ts.strftime('%H:%M')}</span>
        </div>
        '''


class UserMessage(BaseMessage):
    """Пользовательское сообщение"""
    BG_COLOR = 'rgb(28 142 179)'
    TEXT_ALIGN = BaseMessage.Alignment.RIGHT
    NAME = 'Вы'


class GPTMessage(BaseMessage):
    """Сообщение от GPT-модели"""
    BG_COLOR = '#888888'
    NAME = 'Модель'


def main():
    """Инициализирует графический интерфейс на streamlit"""
    st.session_state.setdefault('messages', list[BaseMessage]())
    st.title('Чат с ruGPT-3 от SberDevices')
    st.text_input('Введите ваше сообщение:', key='user_input', on_change=message_handler)
    for message in st.session_state['messages']:
        st.markdown(message.format(), unsafe_allow_html=True)


def message_handler():
    """Обработчик сообщения, вызываемый по нажатию кнопки `отправить`"""
    if st.session_state['user_input']:
        st.session_state['messages'].append(UserMessage(st.session_state['user_input']))
        st.session_state['messages'].append(GPTMessage(st.session_state['user_input']))
        st.session_state['user_input'] = ''


if __name__ == '__main__':
    main()
