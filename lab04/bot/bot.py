import os
from aiogram import Bot, Dispatcher

from lab04.bot.handlers import router


bot = Bot(token=os.getenv('BOT_TOKEN'))
dp = Dispatcher()
dp.include_router(router)

async def run_bot():
    await dp.start_polling(bot)
