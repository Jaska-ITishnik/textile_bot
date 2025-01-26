import asyncio
import logging
import os
import sys

from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.redis import RedisStorage
from dotenv import load_dotenv
from redis.asyncio import Redis

from bot import admin_router, user_router
from bot.bot_commands.all_commands import on_startup, on_shutdown
from bot.handlers.customer_handler import customer_router


load_dotenv('.env')
TOKEN = os.getenv("BOT_TOKEN")
redis = Redis()
storage = RedisStorage(redis=redis)
dp = Dispatcher(storage=storage)


async def main() -> None:
    bot = Bot(token=TOKEN)
    dp.include_routers(user_router, admin_router, customer_router)
    dp.startup.register(on_startup)
    dp.shutdown.register(on_shutdown)
    await dp.start_polling(bot)


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, stream=sys.stdout)
    asyncio.run(main())