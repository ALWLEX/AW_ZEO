# AW_ZEO/services/__init__.py

from .moodle_service import MoodleService
from .schedule_service import ScheduleService
from .admission_service import AdmissionService
from .ai_service import AIService

__all__ = [
    'MoodleService',
    'ScheduleService',
    'AdmissionService',
    'AIService'
]