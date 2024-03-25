import logging
import pathlib

from aiogram import Bot, Router, Dispatcher
from aiogram.fsm.storage.redis import RedisStorage
from aiogram.webhook.aiohttp_server import SimpleRequestHandler, setup_application
from aiohttp.web import run_app
from aiohttp.web_app import Application
from redis.asyncio.client import Redis

router = Router()


@router.startup()
async def on_startup(bot: Bot, webhook_url: str):
    """On bot startup instructions"""

    await bot.set_webhook(url=webhook_url, drop_pending_updates=True)
    from bot.commands.bot_commands import set_commands
    await set_commands(bot)


@router.shutdown()
async def on_shutdown(bot: Bot):
    """On bot shutdown instructions"""

    logging.warning("Shutting down..")
    await bot.delete_webhook()
    await bot.session.close()


def setup_env():
    """Environment variables setup"""

    from dotenv import load_dotenv
    path = pathlib.Path(__file__).parent.parent
    dotenv_path = path.joinpath('.env')
    if dotenv_path.exists():
        load_dotenv(dotenv_path=dotenv_path)


def bot_start() -> None:
    """Bot starting"""

    from bot.config import Config
    bot = Bot(token=Config.BOT_TOKEN)
    redis = Redis(host=Config.REDIS_HOST,
                  port=Config.REDIS_PORT,
                  # username=Config.REDIS_USER,
                  # password=Config.REDIS_PASSWORD,
                  decode_responses=True)

    storage = RedisStorage(redis=redis)
    dp = Dispatcher(storage=storage)
    dp['webhook_url'] = Config.WEBHOOK_URL
    dp['redis'] = redis

    dp.include_router(router)

    from bot.utils.errors import ErrorsLogger
    dp.errors.register(ErrorsLogger)

    from bot.commands import register_user_commands
    register_user_commands(dp)

    handlers_router = Router()
    dp.include_router(handlers_router)

    from bot.chat.handlers import router as chat_router
    handlers_router.include_router(chat_router)

    app = Application()  # AIOHttp App
    app['bot'] = bot
    app['redis'] = redis

    SimpleRequestHandler(
        dispatcher=dp,
        bot=bot
    ).register(app, path=Config.WEBHOOK_PATH)

    setup_application(app, dp, bot=bot)

    run_app(app, host=Config.WEBAPP_HOST, port=Config.WEBAPP_PORT)


def main() -> None:
    """Main function"""

    logger = logging.getLogger(__name__)
    try:
        setup_env()
        bot_start()
    except (KeyboardInterrupt, SystemExit):
        logger.info('Bot stopped')


if __name__ == "__main__":
    logging.basicConfig(level=logging.DEBUG)
    main()
