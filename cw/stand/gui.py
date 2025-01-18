import os
from tempfile import NamedTemporaryFile
from pathlib import Path

from cw.stand.service import Service, MODELS

import streamlit as st


def gui() -> None:
    """Инициализирует графический интерфейс на streamlit"""
    st.title('Автоматическая транскрипция фортепианной музыки с помощью модели Omnizart')
    st.selectbox('Модель', options=MODELS.keys(), index=0, key='model_name')
    uploaded_file = st.file_uploader('Аудиофайл в формате .wav', ['wav'])

    service = Service()

    if st.button('Транскрибировать'):
        if uploaded_file is None:
            st.error('Пожалуйста, загрузите .wav файл.')
        else:
            with st.spinner():
                with NamedTemporaryFile(delete=False, suffix='.wav') as temp_wav:
                    temp_wav.write(uploaded_file.read())
                    wav_path = Path(temp_wav.name)

                output_mid = wav_path.with_suffix('.mid')

                service.transcribe(st.session_state['model_name'], wav_path, output_mid)

                # Отображаем ссылку для скачивания .mid файла
                with open(output_mid, 'rb') as f:
                    st.download_button(
                        label='Скачать результат (.mid)',
                        data=f,
                        file_name=os.path.basename(output_mid),
                        mime='audio/midi'
                    )

                os.remove(wav_path)
                os.remove(output_mid)


if __name__ == '__main__':
    gui()
