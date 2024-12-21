import asyncio

from lab04.bot.bot import run_bot

if __name__ == '__main__':
    print('Запускаем поллинг')
    asyncio.run(run_bot())
