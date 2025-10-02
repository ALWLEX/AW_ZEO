#!/usr/bin/env python3


import logging
import sys
import os


project_root = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, project_root)


logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)


def main():
    try:
        from app import AWZeoBot

        logger.info("🤖 Запуск AW_ZEO Telegram бота...")
        logger.info("✅ Бот инициализируется...")

        bot = AWZeoBot()
        logger.info("🎯 Бот готов к работе!")
        logger.info("💬 Напишите /start в Telegram")
        logger.info("🛑 Остановка: Ctrl+C")


        bot.application.run_polling()

    except KeyboardInterrupt:
        logger.info("🛑 Бот остановлен пользователем")
    except Exception as e:
        logger.error(f"❌ Ошибка запуска бота: {e}")
        return False


if __name__ == '__main__':
    main()