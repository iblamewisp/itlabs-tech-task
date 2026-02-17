# bot/main.py
import asyncio
import logging
from aiohttp import web
from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.redis import RedisStorage
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.webhook.aiohttp_server import SimpleRequestHandler, setup_application

from bot.config import load_config
from bot.handlers import start, tasks, edit_task, categories
from bot.dialogs import add_task, add_category
from bot.middlewares import RateLimitMiddleware, ServiceMiddleware
from bot.clients.http_client import HTTPClient

logger = logging.getLogger(__name__)


async def on_startup_webhook(bot: Bot, webhook_url: str, webhook_path: str):
    """Set webhook on startup"""
    full_url = f"{webhook_url}{webhook_path}"
    await bot.set_webhook(url=full_url, drop_pending_updates=True)
    logger.info(f"Webhook set to: {full_url}")


async def on_shutdown(bot: Bot):
    """Cleanup on shutdown"""
    await HTTPClient.close_session() 
    await bot.session.close()
    logger.info("Bot shutdown complete")


def setup_dispatcher(storage: RedisStorage) -> Dispatcher:
    """Setup dispatcher with middlewares and handlers"""
    dp = Dispatcher(storage=storage)
    
    # Middlewares
    service_middleware = ServiceMiddleware() 
    rate_limit_middleware = RateLimitMiddleware()
    
    dp.message.middleware(service_middleware)
    dp.callback_query.middleware(service_middleware)
    dp.message.middleware(rate_limit_middleware)
    
    # Handlers
    dp.include_router(start.router)
    dp.include_router(tasks.router)
    dp.include_router(categories.router)
    dp.include_router(add_task.router)
    dp.include_router(add_category.router)
    dp.include_router(edit_task.router)
    
    return dp


async def run_webhook(config):
    """Run bot with webhook"""
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    bot = Bot(
        token=config.bot_token,
        default=DefaultBotProperties(parse_mode=ParseMode.HTML)
    )
    
    storage = RedisStorage.from_url(config.redis_fsm_url)
    dp = setup_dispatcher(storage)
    
    webhook_path = f"/webhook/{config.bot_token}"
    dp.startup.register(
        lambda: on_startup_webhook(bot, config.webhook_url, webhook_path)
    )
    dp.shutdown.register(lambda: on_shutdown(bot))
    
    app = web.Application()
    webhook_handler = SimpleRequestHandler(dispatcher=dp, bot=bot)
    webhook_handler.register(app, path=webhook_path)
    setup_application(app, dp, bot=bot)
    
    logger.info("Starting webhook server on 0.0.0.0:8443")
    web.run_app(app, host="0.0.0.0", port=8443)


async def run_polling(config):
    """Run bot with polling"""
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    bot = Bot(
        token=config.bot_token,
        default=DefaultBotProperties(parse_mode=ParseMode.HTML)
    )
    
    storage = RedisStorage.from_url(config.redis_fsm_url)
    dp = setup_dispatcher(storage)
    
    logger.info("Starting polling...")
    
    try:
        await dp.start_polling(bot)
    finally:
        await HTTPClient.close_session()
        await bot.session.close()
        await storage.close()
        logger.info("Bot stopped")


async def main():
    """Main entry point"""
    config = load_config()
    
    if config.use_webhook:
        await run_webhook(config)
    else:
        await run_polling(config)


if __name__ == '__main__':
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("Bot stopped by user")