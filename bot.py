import logging
import asyncio

from aiogram import Bot, Dispatcher
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.contrib.fsm_storage.redis import RedisStorage
from aiogram.utils import executor

from config import BOT_TOKEN, use_redis
from filters.filters import IsDirectStart, IsDirectM, IsDirectC, IsDirectAdminC, IsDirectAdminM
from handlers.user_handlers.users import register_user_commands_callbacks
from handlers.user_handlers.quests import register_user_quest_callbacks
from handlers.admin_handlers.admins import register_admin_commands_callbacks
from handlers.admin_handlers.manage_quests import register_quest_commands_callbacks
from handlers.admin_handlers.manage_achievements import register_achievement_commands_callbacks

# don't forget to run db/models.py


def register_all_handlers(user_commands, user_quest_commands, admin_commands, quest_manage_commands, achievement_manage_commands):
    user_commands()
    user_quest_commands()
    admin_commands()
    quest_manage_commands()
    achievement_manage_commands()


logger = logging.getLogger(__name__)
bot = Bot(BOT_TOKEN, parse_mode='HTML')
dp = Dispatcher(bot)


async def main():
    logging.basicConfig(level=logging.INFO,
                        format="%(asctime)s - %(levelname)s - %(name)s - %(message)s",)
    logger.error("Starting bot")

    if use_redis:
        dp.storage = RedisStorage()
    else:
        dp.storage = MemoryStorage

    dp.filters_factory.bind(IsDirectStart)  # is_direct_start
    dp.filters_factory.bind(IsDirectM)  # is_direct_message
    dp.filters_factory.bind(IsDirectC)  # is_direct_callback
    dp.filters_factory.bind(IsDirectAdminC)  # admin_callback
    dp.filters_factory.bind(IsDirectAdminM)  # admin_message

    register_all_handlers(register_user_commands_callbacks, register_user_quest_callbacks,
                          register_admin_commands_callbacks, register_quest_commands_callbacks,
                          register_achievement_commands_callbacks,)

    try:
        executor.start_polling(dp, skip_updates=True)
    finally:
        await dp.storage.close()
        await dp.storage.wait_closed()
        await bot.session.close()


if __name__ == '__main__':
    try:
        asyncio.run(main())
    except (KeyboardInterrupt, SystemExit):
        logger.error("Bot stopped!")
