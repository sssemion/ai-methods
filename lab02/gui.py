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
        write_message(message)

    if user_input:
        user_message = Message('Вы', 'user', user_input)
        write_message(user_message)
        st.session_state['messages'].append(user_message)

        with st.spinner():
            model = MODELS[st.session_state['model_name']]
            params = {param_key: st.session_state[param_key] for param_key in GENERATIVE_PARAMS}
            gpt_message = Message(model.MODEL_NAME, 'assistant', model.send_message(user_input, **params), meta=params)
            st.session_state['messages'].append(gpt_message)
            write_message(gpt_message)


# def init_messages():

def write_message(message: Message) -> None:
    with st.chat_message(name=message.name, avatar=message.avatar):
        st.write(message.text)
        st.caption(f'{message.name}, {message.ts.strftime("%H:%M:%S")}')
        if message.meta:
            st.caption(message.meta)

def sidebar():
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
