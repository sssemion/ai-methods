from aiogram.types import ReplyKeyboardMarkup, KeyboardButton

from lab04.bot import locals
from lab04.bot.locals import GENERATE_AGAIN_BUTTON, TRY_AGAIN_BUTTON, START_AGAIN_BUTTON

START_KEYBOARD = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text=locals.START_BUTTON), KeyboardButton(text=locals.HELP_BUTTON)],
    ],
    resize_keyboard=True,
)

ASK_CONDITION_KEYBOARD = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text=locals.Condition.NEW), KeyboardButton(text=locals.Condition.USED)],
        [KeyboardButton(text=locals.Condition.NO_MATTER)],
    ],
    resize_keyboard=True,
    one_time_keyboard=True,
)

RESULT_KEYBOARD = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text=GENERATE_AGAIN_BUTTON)],
        [KeyboardButton(text=TRY_AGAIN_BUTTON)],
        [KeyboardButton(text=START_AGAIN_BUTTON)],
    ],
    resize_keyboard=True,
    one_time_keyboard=True,
)