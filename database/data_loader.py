# AW_ZEO/database/data_loader.py


import sqlite3
import logging
from typing import Dict, Any

from config import DATABASE_PATH
from services.moodle_service import MoodleService
from services.admission_service import AdmissionService

logger = logging.getLogger(__name__)


class DataLoader:
    def __init__(self):
        self.db_path = DATABASE_PATH
        self.moodle_service = MoodleService()
        self.admission_service = AdmissionService()

    def load_all_data(self) -> Dict[str, Any]:
        results = {}

        try:
            results['moodle'] = self.load_moodle_data()

            results['programs'] = self.load_educational_programs()

            results['klimov_test'] = self.load_klimov_test()

            logger.info("Все данные успешно загружены")
            return results

        except Exception as e:
            logger.error(f"Ошибка загрузки данных: {e}")
            return {'error': str(e)}

    def load_moodle_data(self) -> Dict[str, Any]:
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()

                cursor.execute('''
                    CREATE TABLE IF NOT EXISTS moodle_credentials (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        phone_number TEXT UNIQUE,
                        login TEXT NOT NULL,
                        password TEXT NOT NULL,
                        email TEXT,
                        student_group TEXT,
                        full_name TEXT,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    )
                ''')

                conn.commit()

                return {'status': 'success', 'message': 'Данные Moodle загружены'}

        except Exception as e:
            logger.error(f"Ошибка загрузки данных Moodle: {e}")
            return {'status': 'error', 'error': str(e)}

    def load_educational_programs(self) -> Dict[str, Any]:
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()

                cursor.execute('''
                    CREATE TABLE IF NOT EXISTS bachelor_programs (
                        program_id TEXT PRIMARY KEY,
                        program_name TEXT NOT NULL,
                        ent_score INTEGER,
                        profile_subjects TEXT,
                        description TEXT,
                        career_prospects TEXT,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    )
                ''')

                conn.commit()

                return {'status': 'success', 'message': 'Образовательные программы загружены'}

        except Exception as e:
            logger.error(f"Ошибка загрузки образовательных программ: {e}")
            return {'status': 'error', 'error': str(e)}

    def load_klimov_test(self) -> Dict[str, Any]:
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()

                cursor.execute('''
                    CREATE TABLE IF NOT EXISTS klimov_questions (
                        question_id INTEGER PRIMARY KEY,
                        question_text TEXT NOT NULL,
                        option_a_text TEXT NOT NULL,
                        option_a_category TEXT NOT NULL,
                        option_b_text TEXT NOT NULL, 
                        option_b_category TEXT NOT NULL,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    )
                ''')

                test_questions = self.admission_service.klimov_test
                for question in test_questions:
                    cursor.execute('''
                        INSERT OR REPLACE INTO klimov_questions 
                        (question_id, question_text, option_a_text, option_a_category, 
                         option_b_text, option_b_category)
                        VALUES (?, ?, ?, ?, ?, ?)
                    ''', (question['id'], f"Вопрос {question['id']}",
                          question['option_a']['text'], question['option_a']['category'],
                          question['option_b']['text'], question['option_b']['category']))

                conn.commit()

                return {'status': 'success', 'message': f'Тест Климова загружен: {len(test_questions)} вопросов'}

        except Exception as e:
            logger.error(f"Ошибка загрузки теста Климова: {e}")
            return {'status': 'error', 'error': str(e)}

    def update_data(self) -> Dict[str, Any]:
        try:
            results = self.load_all_data()

            for module, result in results.items():
                if result.get('status') == 'success':
                    logger.info(f"Модуль {module} успешно обновлен")
                else:
                    logger.warning(f"Модуль {module} не обновлен: {result.get('error')}")

            return {'status': 'success', 'results': results}

        except Exception as e:
            logger.error(f"Ошибка обновления данных: {e}")
            return {'status': 'error', 'error': str(e)}