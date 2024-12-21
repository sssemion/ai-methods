import asyncio
from time import monotonic

from aiogram import Router
from aiogram.filters import CommandStart
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State
from aiogram.types import Message, ReplyKeyboardRemove

from lab04.bot import locals
from lab04.bot.keyboards import START_KEYBOARD, ASK_CONDITION_KEYBOARD, RESULT_KEYBOARD
from lab04.bot.service import LlmService, AVAILABLE_SERVICES

router = Router(name=__name__)


class Form(StatesGroup):
    """Класс, описывающий состояния системы FSM"""
    init = State()  # пользователь еще не начал подбор, может нажать "помощь"
    budget = State()
    vehicle_type = State()
    purpose = State()
    features = State()
    condition = State()
    models = State()
    result = State()


@router.message(CommandStart())
async def command_start(message: Message, state: FSMContext) -> None:
    """Обработчик команды /start"""
    await to_start(message, state)


async def to_start(message: Message, state: FSMContext) -> None:
    await state.set_state(Form.init)
    await message.answer(locals.START_GREETING, reply_markup=START_KEYBOARD)


@router.message(Form.init)
async def init_state_handler(message: Message, state: FSMContext) -> None:
    """Обработчик init-состояния"""
    if message.text == locals.HELP_BUTTON:
        await message.answer(locals.HELP)
    elif message.text == locals.START_BUTTON:
        await to_budget(message, state)
    else:
        await message.answer(locals.PRESS_BUTTON_ERROR)


async def to_budget(message: Message, state: FSMContext) -> None:
    await state.set_state(Form.budget)
    await message.answer(locals.ASK_BUDGET, reply_markup=ReplyKeyboardRemove())


@router.message(Form.budget)
async def budget_state_handler(message: Message, state: FSMContext) -> None:
    """Обработчик состояния budget"""
    await state.update_data(budget=message.text)
    await state.set_state(Form.vehicle_type)
    await message.answer(locals.ASK_VEHICLE_TYPE)


@router.message(Form.vehicle_type)
async def vehicle_type_state_handler(message: Message, state: FSMContext) -> None:
    """Обработчик состояния vehicle_type"""
    await state.update_data(vehicle_type=message.text)
    await state.set_state(Form.purpose)
    await message.answer(locals.ASK_PURPOSE)


@router.message(Form.purpose)
async def purpose_state_handler(message: Message, state: FSMContext) -> None:
    """Обработчик состояния purpose"""
    await state.update_data(purpose=message.text)
    await state.set_state(Form.features)
    await message.answer(locals.ASK_FEATURES)


@router.message(Form.features)
async def features_state_handler(message: Message, state: FSMContext) -> None:
    """Обработчик состояния features"""
    await state.update_data(features=message.text)
    await state.set_state(Form.condition)
    await message.answer(locals.ASK_CONDITION, reply_markup=ASK_CONDITION_KEYBOARD)


@router.message(Form.condition)
async def condition_state_handler(message: Message, state: FSMContext) -> None:
    """Обработчик состояния condition"""
    if message.text in locals.Condition:
        await state.update_data(condition=locals.Condition(message.text))
        await state.set_state(Form.models)
        await message.answer(locals.ASK_MODELS)
    else:
        await message.answer(locals.PRESS_BUTTON_ERROR)


@router.message(Form.models)
async def models_state_handler(message: Message, state: FSMContext) -> None:
    """Обработчик состояния models"""
    await state.update_data(models=message.text)
    await to_result(message, state)


async def to_result(message: Message, state: FSMContext) -> None:
    """Генерирует результат"""
    tasks = [
        asyncio.create_task(make_request_and_send_message(message, state, service))
        for service in AVAILABLE_SERVICES
    ]
    await state.set_state(Form.result)
    await asyncio.gather(*tasks)


async def make_request_and_send_message(message: Message, state: FSMContext, service: LlmService) -> None:
    """Генерирует ответ через service, обогащает мета-информацией и отправляет пользователю"""
    data = await state.get_data()
    start = monotonic()
    result = await service.search_vehicles(**data)
    await message.answer(
        f'Ответ от {service.client.name}, {monotonic() - start:.2f}с:\n\n{result}',
        reply_markup=RESULT_KEYBOARD,
    )


@router.message(Form.result)
async def result_state_handler(message: Message, state: FSMContext) -> None:
    """Обработчик состояния result"""
    match message.text:
        case locals.GENERATE_AGAIN_BUTTON:
            await to_result(message, state)
        case locals.TRY_AGAIN_BUTTON:
            await to_budget(message, state)
        case locals.START_AGAIN_BUTTON:
            await to_start(message, state)
        case _:
            await message.answer(locals.PRESS_BUTTON_ERROR)
            await state.clear()
