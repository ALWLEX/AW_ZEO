# AW_ZEO/services/schedule_service.py


import pandas as pd
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any

from config import TIMETABLE_FILE

logger = logging.getLogger(__name__)


class ScheduleService:
    def __init__(self):
        self.schedule_data = self.load_schedule_data()

    def load_schedule_data(self) -> Dict[str, pd.DataFrame]:
        try:
            excel_file = pd.ExcelFile(TIMETABLE_FILE)
            sheets_data = {}

            for sheet_name in excel_file.sheet_names:
                df = pd.read_excel(TIMETABLE_FILE, sheet_name=sheet_name)
                sheets_data[sheet_name] = df
                logger.info(f"Загружен лист '{sheet_name}': {len(df)} строк")

            return sheets_data

        except Exception as e:
            logger.error(f"Ошибка загрузки расписания: {e}")
            return {}

    def get_schedule(self, group: str, date: str) -> Dict[str, Any]:
        try:
            target_date = datetime.strptime(date, '%Y-%m-%d')
            day_of_week = target_date.strftime('%A')

            day_mapping = {
                'Monday': 'Дүйсенбі / Понедельник',
                'Tuesday': 'Сейсенбі / Вторник',
                'Wednesday': 'Сәрсенбі / Среда',
                'Thursday': 'Бейсенбі / Четверг',
                'Friday': 'Жұма / Пятница',
                'Saturday': 'Сенбі / Суббота',
                'Sunday': 'Жексенбі / Воскресенье'
            }

            russian_day = day_mapping.get(day_of_week, '')

            schedule = self.find_group_schedule(group, russian_day)

            return {
                'group': group,
                'date': date,
                'day_of_week': russian_day,
                'schedule': schedule,
                'status': 'success'
            }

        except Exception as e:
            logger.error(f"Ошибка получения расписания: {e}")
            return {
                'group': group,
                'date': date,
                'schedule': [],
                'status': 'error',
                'error': str(e)
            }

    def find_group_schedule(self, group: str, day: str) -> List[Dict[str, str]]:
        schedule_lessons = []

        try:
            for sheet_name, df in self.schedule_data.items():
                day_rows = df[df.iloc[:, 0].astype(str).str.contains(day, na=False)]

                if not day_rows.empty:
                    for col_idx, col_name in enumerate(df.columns):
                        if group in str(col_name):
                            lessons = self.extract_lessons_for_group(df, day_rows.index[0], col_idx)
                            schedule_lessons.extend(lessons)

            schedule_lessons.sort(key=lambda x: x.get('time_order', 0))

            return schedule_lessons

        except Exception as e:
            logger.error(f"Ошибка поиска расписания группы: {e}")
            return []

    def extract_lessons_for_group(self, df: pd.DataFrame, start_row: int, group_col: int) -> List[Dict[str, str]]:
        lessons = []

        try:
            for i in range(start_row + 1, len(df)):
                row = df.iloc[i]

                if pd.notna(row.iloc[1]) and pd.notna(row.iloc[2]):
                    lesson_number = str(row.iloc[1])
                    time_range = str(row.iloc[2])
                    subject = str(row.iloc[group_col]) if pd.notna(row.iloc[group_col]) else ""

                    if subject and subject.strip() and "nan" not in subject:
                        lessons.append({
                            'lesson_number': lesson_number,
                            'time': time_range,
                            'subject': subject.strip(),
                            'time_order': int(float(lesson_number)) if lesson_number.replace('.', '').isdigit() else 0
                        })
                else:
                    break

            return lessons

        except Exception as e:
            logger.error(f"Ошибка извлечения пар: {e}")
            return []



    def get_week_schedule(self, group: str, start_date: str) -> Dict[str, Any]:
        try:
            start_dt = datetime.strptime(start_date, '%Y-%m-%d')
            week_schedule = {}

            for i in range(7):
                current_date = start_dt + timedelta(days=i)
                date_str = current_date.strftime('%Y-%m-%d')

                day_schedule = self.get_schedule(group, date_str)
                week_schedule[date_str] = day_schedule

            return {
                'group': group,
                'week_start': start_date,
                'schedule': week_schedule,
                'status': 'success'
            }

        except Exception as e:
            logger.error(f"Ошибка получения недельного расписания: {e}")
            return {
                'group': group,
                'week_start': start_date,
                'schedule': {},
                'status': 'error',
                'error': str(e)
            }