# AW_ZEO/config.py


import os
import sys
from dotenv import load_dotenv
from pathlib import Path


project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))


env_path = project_root / '.env'
if env_path.exists():
    load_dotenv(env_path)
    print(f"✅ .env файл загружен из: {env_path}")
else:
    print(f"⚠️ .env файл не найден по пути: {env_path}")


BOT_TOKEN = os.getenv('BOT_TOKEN')
if not BOT_TOKEN:
    raise ValueError("❌ BOT_TOKEN не установлен! Проверьте файл .env")

WEBAPP_URL = os.getenv('WEBAPP_URL', '')

# Настройки базы данных
DATABASE_PATH = str(project_root / 'database' / 'aw_zeo.db')

# Настройки AI
OPENAI_API_KEY = os.getenv('OPENAI_API_KEY', '')

# Пути к файлам данных
DATA_PATH = str(project_root / 'data') + '/'
REG_FILE = DATA_PATH + 'reg.xlsx'
TIMETABLE_FILE = DATA_PATH + 'timetable.xlsx'
BACHELOR_FILE = DATA_PATH + 'bachelor.csv'
MAGISTRATURA_FILE = DATA_PATH + 'magistratura.csv'
DOCTORANTURA_FILE = DATA_PATH + 'doctorantura.csv'
TEST_KLIMOVA_FILE = DATA_PATH + 'test_klimova.csv'
RECOMMENDATIONS_KLIMOV_FILE = DATA_PATH + 'recomendations_klimov.csv'
FAQ_FILE = DATA_PATH + 'faq.pdf'

# Настройки Flask
FLASK_HOST = '0.0.0.0'
FLASK_PORT = 5000
FLASK_DEBUG = True


APP_NAME = 'AW_ZEO'
APP_VERSION = '2.0'


print(f"🔧 Конфигурация загружена:")
print(f"   App: {APP_NAME} v{APP_VERSION}")
print(f"   Bot Token: {'*' * 10}{BOT_TOKEN[-4:] if BOT_TOKEN else 'NOT SET'}")
print(f"   WebApp URL: {WEBAPP_URL}")
print(f"   Database: {DATABASE_PATH}")
print(f"   Data files:")
print(f"     - Moodle: {REG_FILE}")
print(f"     - Schedule: {TIMETABLE_FILE}")