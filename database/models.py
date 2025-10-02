# AW_ZEO/database/models.py
"""
Модели данных для базы данных AW_ZEO
Определяет структуры таблиц и отношения
"""

from dataclasses import dataclass
from datetime import datetime
from typing import Optional

@dataclass
class User:
    """Модель пользователя"""
    user_id: int
    username: Optional[str]
    first_name: str
    last_name: Optional[str]
    phone_number: str
    created_at: datetime
    last_active: datetime

@dataclass
class UserSession:
    """Модель сессии пользователя"""
    session_id: int
    user_id: int
    start_time: datetime
    end_time: Optional[datetime]
    actions_count: int

@dataclass
class MoodleCredentials:
    """Модель учетных данных Moodle"""
    user_id: int
    login: str
    password: str
    email: str
    group: str
    full_name: str

@dataclass
class KlimovTestResult:
    user_id: int
    test_date: datetime
    nature_score: int
    tech_score: int
    person_score: int
    sign_score: int
    art_score: int
    recommended_category: str