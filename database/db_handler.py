# AW_ZEO/database/db_handler.py

import sqlite3
import logging
from datetime import datetime
from typing import Optional, Dict, Any

from config import DATABASE_PATH
from database.models import User

logger = logging.getLogger(__name__)


class DatabaseHandler:
    def __init__(self):
        self.db_path = DATABASE_PATH
        self.init_database()

    def init_database(self):
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()

                cursor.execute('''
                    CREATE TABLE IF NOT EXISTS users (
                        user_id INTEGER PRIMARY KEY,
                        username TEXT,
                        first_name TEXT NOT NULL,
                        last_name TEXT,
                        phone_number TEXT NOT NULL,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        last_active TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    )
                ''')

                cursor.execute('''
                    CREATE TABLE IF NOT EXISTS user_sessions (
                        session_id INTEGER PRIMARY KEY AUTOINCREMENT,
                        user_id INTEGER,
                        start_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        end_time TIMESTAMP,
                        actions_count INTEGER DEFAULT 0,
                        FOREIGN KEY (user_id) REFERENCES users (user_id)
                    )
                ''')

                cursor.execute('''
                    CREATE TABLE IF NOT EXISTS klimov_results (
                        result_id INTEGER PRIMARY KEY AUTOINCREMENT,
                        user_id INTEGER,
                        test_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        nature_score INTEGER DEFAULT 0,
                        tech_score INTEGER DEFAULT 0,
                        person_score INTEGER DEFAULT 0,
                        sign_score INTEGER DEFAULT 0,
                        art_score INTEGER DEFAULT 0,
                        recommended_category TEXT,
                        FOREIGN KEY (user_id) REFERENCES users (user_id)
                    )
                ''')

                conn.commit()
                logger.info("База данных инициализирована успешно")

        except sqlite3.Error as e:
            logger.error(f"Ошибка инициализации базы данных: {e}")

    def save_user(self, user_id: int, username: str, first_name: str,
                  last_name: str, phone_number: str) -> bool:
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()

                cursor.execute('''
                    INSERT OR REPLACE INTO users 
                    (user_id, username, first_name, last_name, phone_number, last_active)
                    VALUES (?, ?, ?, ?, ?, ?)
                ''', (user_id, username, first_name, last_name, phone_number, datetime.now()))

                conn.commit()
                logger.info(f"Пользователь {user_id} сохранен в базу")
                return True

        except sqlite3.Error as e:
            logger.error(f"Ошибка сохранения пользователя: {e}")
            return False

    def get_user(self, user_id: int) -> Optional[User]:
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()

                cursor.execute('''
                    SELECT user_id, username, first_name, last_name, phone_number, created_at, last_active
                    FROM users WHERE user_id = ?
                ''', (user_id,))

                row = cursor.fetchone()
                if row:
                    return User(*row)
                return None

        except sqlite3.Error as e:
            logger.error(f"Ошибка получения пользователя: {e}")
            return None

    def update_user_activity(self, user_id: int) -> bool:
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()

                cursor.execute('''
                    UPDATE users SET last_active = ? WHERE user_id = ?
                ''', (datetime.now(), user_id))

                conn.commit()
                return True

        except sqlite3.Error as e:
            logger.error(f"Ошибка обновления активности: {e}")
            return False