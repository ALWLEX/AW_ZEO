# AW_ZEO/services/ai_service.py

import openai
import logging
import re
from typing import Dict, Any, Optional

from config import OPENAI_API_KEY

logger = logging.getLogger(__name__)


class AIService:
    def __init__(self):
        self.client = None
        if OPENAI_API_KEY:
            try:
                self.client = openai.AsyncOpenAI(api_key=OPENAI_API_KEY)
                logger.info("OpenAI клиент инициализирован")
            except Exception as e:
                logger.error(f"Ошибка инициализации OpenAI: {e}")

        self.keywords = {
            'расписание': ['расписание', 'пары', 'когда учиться', 'распис', 'занятия'],
            'moodle': ['логин', 'пароль', 'moodle', 'аккаунт', 'учетные данные'],
            'поступление': ['поступление', 'ент', 'баллы', 'абитуриент', 'поступить'],
            'тест': ['тест', 'климова', 'профориентация', 'профессия'],
            'программы': ['программы', 'специальности', 'факультет', 'образование']
        }

    async def process_natural_language(self, text: str, user_id: int) -> str:
        try:
            if self.client:
                return await self.process_with_gpt(text, user_id)
            else:
                return self.fallback_response(text)

        except Exception as e:
            logger.error(f"Ошибка обработки естественного языка: {e}")
            return self.fallback_response(text)

    async def process_with_gpt(self, text: str, user_id: int) -> str:
        try:
            system_prompt = """
            Ты - AW_ZEO, умный помощник для студентов и абитуриентов КРУ им. А. Байтурсынова.
            Отвечай дружелюбно, но по делу. Используй уважительное обращение на "вы".

            Основные функции бота:
            1. Расписание пар - показывает когда и какие пары
            2. Учетные данные Moodle - логины и пароли
            3. Информация о поступлении - программы, баллы ЕНТ
            4. Тест Климова - профориентация
            5. Образовательные программы - бакалавриат, магистратура, докторантура

            Отвечай кратко и полезно. Если вопрос не по теме, вежливо направляй в нужный раздел.
            """

            response = await self.client.chat.completions.create(
                model="gpt-5-turbo",
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": text}
                ],
                max_tokens=500
            )

            return response.choices[0].message.content

        except Exception as e:
            logger.error(f"Ошибка GPT обработки: {e}")
            return self.fallback_response(text)

    def fallback_response(self, text: str) -> str:
        text_lower = text.lower()

        if any(word in text_lower for word in self.keywords['расписание']):
            return "📅 Чтобы посмотреть расписание, откройте приложение и перейдите в раздел 'Расписание'. Там вы сможете выбрать свою группу и посмотреть пары на любой день!"

        elif any(word in text_lower for word in self.keywords['moodle']):
            return "🎓 Ваши данные для Moodle можно получить в разделе 'Moodle' приложения. Там же есть инструкции по входу в систему!"

        elif any(word in text_lower for word in self.keywords['поступление']):
            return "🎯 Вся информация о поступлении, включая программы, проходные баллы и документы, доступна в разделе 'Поступление'. Там же можно пройти профориентационный тест!"

        elif any(word in text_lower for word in self.keywords['тест']):
            return "🧩 Тест Климова поможет определить подходящие профессии! Пройдите его в разделе 'Поступление' -> 'Профориентация'."

        elif any(word in text_lower for word in self.keywords['программы']):
            return "📚 Информация обо всех образовательных программах (бакалавриат, магистратура, докторантура) доступна в разделе 'Поступление'."

        else:
            return "🤖 Я понял ваш вопрос! Для получения точной информации откройте приложение AW_ZEO - там есть все необходимые разделы:\n\n• 📅 Расписание\n• 🎓 Moodle\n• 🎯 Поступление\n• 👤 Профиль\n\nИли задайте вопрос более конкретно!"

    def process_message(self, message: str, user_id: str) -> str:
        return self.fallback_response(message)

    def extract_group_from_text(self, text: str) -> Optional[str]:
        try:
            patterns = [
                r'[А-Яа-я]{2,4}-\d{2}-\d{3}-\d{2}',
                r'[А-Яа-я]{2,4}\d{2}-\d{3}-\d{2}',
                r'\d{2}-\d{3}-\d{2}',
            ]

            for pattern in patterns:
                matches = re.findall(pattern, text)
                if matches:
                    return matches[0]

            return None

        except Exception as e:
            logger.error(f"Ошибка извлечения группы: {e}")
            return None

    def extract_date_from_text(self, text: str) -> Optional[str]:
        try:
            patterns = [
                r'\d{2}\.\d{2}\.\d{4}',
                r'\d{4}-\d{2}-\d{2}',
                r'\d{1,2}\s+\w+\s+\d{4}',
            ]

            for pattern in patterns:
                matches = re.findall(pattern, text)
                if matches:
                    return matches[0]

            days = {
                'понедельник': 'monday',
                'вторник': 'tuesday',
                'среда': 'wednesday',
                'четверг': 'thursday',
                'пятница': 'friday',
                'суббота': 'saturday',
                'воскресенье': 'sunday',
                'сегодня': 'today',
                'завтра': 'tomorrow',
                'послезавтра': 'day_after_tomorrow'
            }

            text_lower = text.lower()
            for day_ru, day_en in days.items():
                if day_ru in text_lower:
                    return day_en

            return None

        except Exception as e:
            logger.error(f"Ошибка извлечения даты: {e}")
            return None