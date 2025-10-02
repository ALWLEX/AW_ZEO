# AW_ZEO/utils/helpers.py
"""
Вспомогательные функции для проекта AW_ZEO
Утилиты и общие функции
"""

import re
import logging
from datetime import datetime, timedelta
from typing import Optional, Dict, Any

logger = logging.getLogger(__name__)


def validate_phone_number(phone: str) -> bool:
    """Валидация номера телефона"""
    try:
        # Очистка номера от лишних символов
        cleaned_phone = re.sub(r'[^\d+]', '', phone)

        # Проверка формата
        patterns = [
            r'^\+7\d{10}$',  # +77001234567
            r'^87\d{9}$',  # 87001234567
            r'^7\d{10}$',  # 77001234567
            r'^8\d{10}$',  # 87001234567 (альтернативный)
        ]

        return any(re.match(pattern, cleaned_phone) for pattern in patterns)

    except Exception as e:
        logger.error(f"Ошибка валидации телефона: {e}")
        return False


def format_phone_number(phone: str) -> str:
    """Форматирование номера телефона в единый формат"""
    try:
        cleaned = re.sub(r'[^\d+]', '', phone)

        if cleaned.startswith('87') and len(cleaned) == 11:
            return '+7' + cleaned[2:]
        elif cleaned.startswith('7') and len(cleaned) == 11:
            return '+' + cleaned
        elif cleaned.startswith('8') and len(cleaned) == 11:
            return '+7' + cleaned[1:]
        elif cleaned.startswith('+7') and len(cleaned) == 12:
            return cleaned
        else:
            return phone  # Возвращаем как есть если формат не распознан

    except Exception as e:
        logger.error(f"Ошибка форматирования телефона: {e}")
        return phone


def parse_date_input(date_str: str) -> Optional[datetime]:
    """Парсинг даты из текстового ввода"""
    try:
        date_str = date_str.lower().strip()

        # Сегодня/завтра/послезавтра
        if date_str == 'сегодня':
            return datetime.now()
        elif date_str == 'завтра':
            return datetime.now() + timedelta(days=1)
        elif date_str == 'послезавтра':
            return datetime.now() + timedelta(days=2)

        # Дни недели
        days_mapping = {
            'понедельник': 0,
            'вторник': 1,
            'среда': 2,
            'четверг': 3,
            'пятница': 4,
            'суббота': 5,
            'воскресенье': 6
        }

        if date_str in days_mapping:
            today = datetime.now()
            target_day = days_mapping[date_str]
            current_day = today.weekday()

            days_ahead = target_day - current_day
            if days_ahead <= 0:
                days_ahead += 7

            return today + timedelta(days=days_ahead)

        # Форматы дат
        date_formats = [
            '%d.%m.%Y',  # 25.12.2024
            '%Y-%m-%d',  # 2024-12-25
            '%d/%m/%Y',  # 25/12/2024
        ]

        for fmt in date_formats:
            try:
                return datetime.strptime(date_str, fmt)
            except ValueError:
                continue

        return None

    except Exception as e:
        logger.error(f"Ошибка парсинга даты: {e}")
        return None


def format_schedule_response(schedule_data: Dict[str, Any]) -> str:
    """Форматирование ответа с расписанием"""
    try:
        if not schedule_data.get('schedule'):
            return "📅 На выбранную дату пар нет 🎉"

        response = f"📅 Расписание для группы {schedule_data['group']}\n"
        response += f"📅 {schedule_data['day_of_week']}\n\n"

        for lesson in schedule_data['schedule']:
            response += f"🕒 {lesson['time']} - {lesson['subject']}\n"

        return response

    except Exception as e:
        logger.error(f"Ошибка форматирования расписания: {e}")
        return "❌ Произошла ошибка при получении расписания"


def format_moodle_credentials(credentials: Dict[str, Any]) -> str:
    """Форматирование ответа с учетными данными"""
    try:
        response = "🎓 Ваши учетные данные для Moodle:\n\n"
        response += f"👤 ФИО: {credentials['full_name']}\n"
        response += f"📚 Группа: {credentials['group']}\n"
        response += f"🔑 Логин: {credentials['login']}\n"
        response += f"🔒 Пароль: {credentials['password']}\n"
        response += f"📧 Email: {credentials['email']}\n\n"
        response += "💡 Сохраните эти данные в надежном месте!"

        return response

    except Exception as e:
        logger.error(f"Ошибка форматирования учетных данных: {e}")
        return "❌ Произошла ошибка при получении учетных данных"


def sanitize_input(text: str) -> str:

    try:

        sanitized = re.sub(r'[<>&"\'\\]', '', text)
        return sanitized.strip()
    except Exception as e:
        logger.error(f"Ошибка очистки ввода: {e}")
        return text


def calculate_ent_chance(score: int, program_min_score: int) -> str:
    try:
        difference = score - program_min_score

        if difference >= 20:
            return "Высокий шанс 🎯"
        elif difference >= 10:
            return "Хороший шанс ✅"
        elif difference >= 0:
            return "Средний шанс ⚠️"
        else:
            return "Низкий шанс ❌"

    except Exception as e:
        logger.error(f"Ошибка расчета шансов: {e}")
        return "Неизвестно"