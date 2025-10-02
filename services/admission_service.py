# AW_ZEO/services/admission_service.py


import pandas as pd
import logging
import json
from typing import Dict, List, Optional, Any

from config import (BACHELOR_FILE, MAGISTRATURA_FILE, DOCTORANTURA_FILE,
                    TEST_KLIMOVA_FILE, RECOMMENDATIONS_KLIMOV_FILE)

logger = logging.getLogger(__name__)


class AdmissionService:
    def __init__(self):
        self.bachelor_programs = self.load_bachelor_programs()
        self.magistratura_programs = self.load_magistratura_programs()
        self.doctorantura_programs = self.load_doctorantura_programs()
        self.klimov_test = self.load_klimov_test()
        self.klimov_recommendations = self.load_klimov_recommendations()

    def load_bachelor_programs(self) -> pd.DataFrame:
        try:
            df = pd.read_csv(BACHELOR_FILE, encoding='utf-8')
            logger.info(f"Программы бакалавриата загружены: {len(df)} записей")
            return df
        except Exception as e:
            logger.error(f"Ошибка загрузки бакалавриата: {e}")
            return pd.DataFrame()

    def load_magistratura_programs(self) -> pd.DataFrame:
        try:
            try:
                df = pd.read_csv(MAGISTRATURA_FILE, encoding='utf-8', sep=';')
            except:
                df = pd.read_csv(MAGISTRATURA_FILE, encoding='utf-8', sep=',')

            logger.info(f"Программы магистратуры загружены: {len(df)} записей")
            return df
        except Exception as e:
            logger.error(f"Ошибка загрузки магистратуры: {e}")
            fallback_data = {
                'Направление': ['Научно-педагогическое (2 года)', 'Профильное (1 год)'],
                'Код': ['М001', 'М002'],
                'Группа образовательных программ': ['Педагогика и психология', 'Право'],
                'Профильные предметы комплексного тестирования': ['Педагогика, Психология',
                                                                  'Теория государства и права'],
                'Проходной балл': [75, 50]
            }
            return pd.DataFrame(fallback_data)

    def load_doctorantura_programs(self) -> pd.DataFrame:
        try:
            try:
                df = pd.read_csv(DOCTORANTURA_FILE, encoding='utf-8', sep=';')
            except:
                df = pd.read_csv(DOCTORANTURA_FILE, encoding='utf-8', sep=',')

            logger.info(f"Программы докторантуры загружены: {len(df)} записей")
            return df
        except Exception as e:
            logger.error(f"Ошибка загрузки докторантуры: {e}")
            fallback_data = {
                'Код': ['D001', 'D010'],
                'Группа образовательных программ': ['Педагогика и психология', 'Подготовка педагогов математики'],
                'Необходимый уровень образования': ['Магистратура', 'Магистратура']
            }
            return pd.DataFrame(fallback_data)

    def load_klimov_test(self) -> List[Dict[str, Any]]:
        try:
            df = pd.read_csv(TEST_KLIMOVA_FILE, encoding='utf-8')
            test_questions = []

            for _, row in df.iterrows():
                question = {
                    'id': int(row['question_id']),
                    'option_a': {
                        'text': row['option_a_text'],
                        'category': row['option_a_category']
                    },
                    'option_b': {
                        'text': row['option_b_text'],
                        'category': row['option_b_category']
                    }
                }
                test_questions.append(question)

            logger.info(f"Тест Климова загружен: {len(test_questions)} вопросов")
            return test_questions

        except Exception as e:
            logger.error(f"Ошибка загрузки теста Климова: {e}")
            fallback_questions = [
                {
                    'id': 1,
                    'option_a': {'text': 'Ухаживать за животными', 'category': 'nature'},
                    'option_b': {'text': 'Обслуживать машины, приборы', 'category': 'tech'}
                },
                {
                    'id': 2,
                    'option_a': {'text': 'Помогать больным людям', 'category': 'person'},
                    'option_b': {'text': 'Составлять таблицы, схемы', 'category': 'sign'}
                }
            ]
            return fallback_questions

    def load_klimov_recommendations(self) -> Dict[str, Any]:
        try:
            df = pd.read_csv(RECOMMENDATIONS_KLIMOV_FILE, encoding='utf-8')
            recommendations = {}

            for _, row in df.iterrows():
                category = row['category_code']
                recommendations[category] = {
                    'name': row['category_name'],
                    'description': row['description'],
                    'programs': row['recommended_programs'].split(';')
                }

            logger.info(f"Рекомендации Климова загружены: {len(recommendations)} категорий")
            return recommendations

        except Exception as e:
            logger.error(f"Ошибка загрузки рекомендаций: {e}")
            # Создаем базовые рекомендации
            return {
                'nature': {
                    'name': 'Человек - Природа',
                    'description': 'Работа с природой и животными',
                    'programs': ['B013 Подготовка учителей биологии', 'B050 Биологические науки']
                },
                'tech': {
                    'name': 'Человек - Техника',
                    'description': 'Работа с техникой и механизмами',
                    'programs': ['B011 Подготовка учителей информатики', 'B057 Информационные технологии']
                },
                'person': {
                    'name': 'Человек - Человек',
                    'description': 'Работа с людьми',
                    'programs': ['B001 Педагогика и психология', 'B018 Подготовка учителей иностранного языка']
                },
                'sign': {
                    'name': 'Человек - Знаковая система',
                    'description': 'Работа с данными и знаками',
                    'programs': ['B009 Подготовка учителей математики', 'B055 Математика и статистика']
                },
                'art': {
                    'name': 'Человек - Художественный образ',
                    'description': 'Творческая работа',
                    'programs': ['B006 Подготовка учителей музыки', 'B007 Подготовка учителей художественного труда']
                }
            }

    def get_programs(self, program_type: str) -> Dict[str, Any]:
        try:
            if program_type == 'bachelor':
                programs = self.bachelor_programs
            elif program_type == 'magistratura':
                programs = self.magistratura_programs
            elif program_type == 'doctorantura':
                programs = self.doctorantura_programs
            else:
                programs = pd.DataFrame()

            # Конвертация в список словарей
            programs_list = []
            if not programs.empty:
                programs_list = programs.to_dict('records')

            return {
                'type': program_type,
                'count': len(programs_list),
                'programs': programs_list,
                'status': 'success'
            }

        except Exception as e:
            logger.error(f"Ошибка получения программ: {e}")
            return {
                'type': program_type,
                'count': 0,
                'programs': [],
                'status': 'error',
                'error': str(e)
            }

    def get_klimov_test(self) -> Dict[str, Any]:
        return {
            'test_name': 'Тест профессиональных предпочтений Климова',
            'questions_count': len(self.klimov_test),
            'questions': self.klimov_test,
            'status': 'success'
        }

    def get_recommendations(self, answers: List[Dict[str, Any]]) -> Dict[str, Any]:
        try:
            scores = {
                'nature': 0,
                'tech': 0,
                'person': 0,
                'sign': 0,
                'art': 0
            }

            for answer in answers:
                question_id = answer.get('question_id')
                selected_option = answer.get('selected_option')  # 'a' или 'b'

                if 0 <= question_id < len(self.klimov_test):
                    question = self.klimov_test[question_id]

                    if selected_option == 'a':
                        category = question['option_a']['category']
                    else:
                        category = question['option_b']['category']

                    if category in scores:
                        scores[category] += 1

            leading_category = max(scores.items(), key=lambda x: x[1])

            recommendation = self.klimov_recommendations.get(leading_category[0], {})

            return {
                'scores': scores,
                'leading_category': leading_category[0],
                'leading_score': leading_category[1],
                'recommendation': recommendation,
                'status': 'success'
            }

        except Exception as e:
            logger.error(f"Ошибка расчета рекомендаций: {e}")
            return {
                'scores': {},
                'leading_category': '',
                'leading_score': 0,
                'recommendation': {},
                'status': 'error',
                'error': str(e)
            }

    def search_programs_by_subjects(self, subject1: str, subject2: str) -> Dict[str, Any]:
        try:
            matching_programs = []

            if not self.bachelor_programs.empty:
                for _, program in self.bachelor_programs.iterrows():
                    profile_subjects = str(program.get('Профильные предметы', ''))
                    if subject1.lower() in profile_subjects.lower() and subject2.lower() in profile_subjects.lower():
                        matching_programs.append(program.to_dict())

            return {
                'subjects': [subject1, subject2],
                'count': len(matching_programs),
                'programs': matching_programs,
                'status': 'success'
            }

        except Exception as e:
            logger.error(f"Ошибка поиска по предметам: {e}")
            return {
                'subjects': [subject1, subject2],
                'count': 0,
                'programs': [],
                'status': 'error',
                'error': str(e)
            }