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
        from web_app.app import app

        logger.info("🚀 Запуск AW_ZEO Web App...")
        logger.info("🌐 Доступен по: http://localhost:5000")
        logger.info("📱 Для бота запустите: python run_bot.py")
        logger.info("🎯 Все функции доступны через Web интерфейс")
        logger.info("🛑 Остановка: Ctrl+C")

        app.run(host='0.0.0.0', port=5000, debug=True)

    except Exception as e:
        logger.error(f"❌ Ошибка запуска Web App: {e}")
        sys.exit(1)


if __name__ == '__main__':
    main()