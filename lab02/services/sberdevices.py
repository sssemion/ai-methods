from lab02.services.abc import BaseGPTService


class SberDevicesRuGPT3Small(BaseGPTService):
    MODEL_NAME = 'sberbank-ai/rugpt3small_based_on_gpt2'

class SberDevicesRuGPT3Medium(BaseGPTService):
    MODEL_NAME = 'sberbank-ai/rugpt3medium_based_on_gpt2'
