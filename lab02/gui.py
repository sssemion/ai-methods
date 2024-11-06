from dataclasses import dataclass, field
from datetime import datetime
from typing import Literal

import streamlit as st

from lab02.services.const import MODELS, GENERATIVE_PARAMS, BASE_TEXT


@dataclass
class Message:
    name: str
    avatar: Literal['user', 'assistant']
    text: str
    ts: datetime = field(default_factory=datetime.now)
    meta: str | None = None


def gui() -> None:
    """Инициализирует графический интерфейс на streamlit"""
    sidebar()
    st.session_state.setdefault('messages', [])
    st.title('Чат с ruGPT-3 от SberDevices')
    user_input = st.chat_input('Введите сообщение:', key='user_input')

    for message in st.session_state['messages']:
        with st.chat_message(name=message.name, avatar=message.avatar):
            render_message(message)

    init_message_if_needed()

    if user_input:
        send_message(user_input)

def init_message_if_needed():
    """Отправляет начальное подготовленное сообщение при первой загрузке приложения"""
    if not st.session_state.get('initialized', False):
        send_message(BASE_TEXT)
        st.session_state['initialized'] = True


def send_message(text: str) -> None:
    """Обработчик отправки сообщения пользователем"""
    user_message = Message('Вы', 'user', text)
    with st.chat_message(name=user_message.name, avatar=user_message.avatar):
        render_message(user_message)
    st.session_state['messages'].append(user_message)

    name = st.session_state['model_name']
    avatar = 'assistant'
    with st.chat_message(name=name, avatar=avatar), st.spinner():
        model = MODELS[name]
        params = {param_key: st.session_state[param_key] for param_key in GENERATIVE_PARAMS}
        gpt_message = Message(name, avatar, model.send_message(text, **params), meta=str(params))
        st.session_state['messages'].append(gpt_message)
        render_message(gpt_message)


def render_message(message: Message) -> None:
    """Отрисовывает контент сообщения на экране"""
    st.write(message.text)
    st.caption(f'{message.name}, {message.ts.strftime("%H:%M:%S")}')
    if message.meta:
        st.caption(message.meta)

def sidebar():
    """Инициализирует боковую панель с параметрами генерации"""
    with st.sidebar:
        st.selectbox('Модель', options=MODELS.keys(), index=0, key='model_name')
        for param_name, param_spec in GENERATIVE_PARAMS.items():
            st.slider(param_name,
                      min_value=param_spec.min,
                      max_value=param_spec.max,
                      step=param_spec.step,
                      value=param_spec.default,
                      key=param_name,
                      )

if __name__ == '__main__':
    gui()
