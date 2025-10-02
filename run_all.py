#!/usr/bin/env python3


import os
import sys
import subprocess
import time
import logging


logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)


def main():
    logger.info("🚀 Запуск всех компонентов AW_ZEO...")
    logger.info("💡 Этот скрипт запустит Web App и бота в отдельных процессах")

    try:
        logger.info("🌐 Запуск Web App...")
        webapp_process = subprocess.Popen([
            sys.executable, "run_webapp.py"
        ])

        time.sleep(3)

        logger.info("🤖 Запуск Telegram бота...")
        bot_process = subprocess.Popen([
            sys.executable, "run_bot.py"
        ])

        logger.info("✅ Все компоненты запущены!")
        logger.info("🌐 Web App: http://localhost:5000")
        logger.info("🤖 Бот: готов к работе в Telegram")
        logger.info("🛑 Для остановки закройте это окно или нажмите Ctrl+C")

        try:
            webapp_process.wait()
            bot_process.wait()
        except KeyboardInterrupt:
            logger.info("🛑 Остановка компонентов...")
            webapp_process.terminate()
            bot_process.terminate()

    except Exception as e:
        logger.error(f"❌ Ошибка запуска: {e}")


if __name__ == '__main__':
    main()