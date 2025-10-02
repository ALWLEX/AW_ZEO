# AW_ZEO/services/moodle_service.py


import pandas as pd
import logging
import re
import os
from typing import Dict, Optional, Any, List

from config import REG_FILE

logger = logging.getLogger(__name__)


class MoodleService:
    def __init__(self):
        self.data = self.load_data()

    def load_data(self) -> pd.DataFrame:
        try:
            reg_file_path = str(REG_FILE)

            if not os.path.exists(reg_file_path):
                logger.error(f"ФАЙЛ НЕ НАЙДЕН: {reg_file_path}")
                raise FileNotFoundError(f"Файл с данными Moodle не найден: {reg_file_path}")

            df = pd.read_excel(reg_file_path)
            logger.info(f"Данные Moodle загружены: {len(df)} записей")
            logger.info(f"Колонки: {list(df.columns)}")

            if 'username' in df.columns and 'password' in df.columns:
                logger.info("Обнаружен формат 1 (с username/password)")
                df = self._process_format1(df)
            elif 'ФИО' in df.columns and 'Группа' in df.columns:
                logger.info("Обнаружен формат 2 (с ФИО/Группа)")
                df = self._process_format2(df)
            else:
                logger.warning("Неизвестный формат, пробуем автоматическую обработку")
                df = self._process_auto(df)

            return df

        except Exception as e:
            logger.error(f"Ошибка загрузки данных Moodle: {e}")
            raise

    def _process_format1(self, df: pd.DataFrame) -> pd.DataFrame:
        column_mapping = {
            'cohort1': 'group',
            'lastname': 'last_name',
            'firstname': 'first_name',
            'username': 'login',
            'password': 'password',
            'email': 'email',
            'Телефон': 'phone',
            'ИИН': 'iin'
        }

        for old_col, new_col in column_mapping.items():
            if old_col in df.columns and new_col not in df.columns:
                df[new_col] = df[old_col]

        if 'full_name' not in df.columns:
            if 'lastname' in df.columns and 'firstname' in df.columns:
                df['full_name'] = df['lastname'] + ' ' + df['firstname']
            elif 'lastname' in df.columns:
                df['full_name'] = df['lastname']

        return df

    def _process_format2(self, df: pd.DataFrame) -> pd.DataFrame:
        column_mapping = {
            'ФИО': 'full_name',
            'Группа': 'group',
            'Сотовый телефон': 'phone',
            'ОП / Специальность': 'specialty'
        }

        for old_col, new_col in column_mapping.items():
            if old_col in df.columns and new_col not in df.columns:
                df[new_col] = df[old_col]

        df = self._generate_logins_passwords(df)

        return df

    def _process_auto(self, df: pd.DataFrame) -> pd.DataFrame:
        logger.info("Автоматическая обработка данных")

        name_columns = [col for col in df.columns if any(word in str(col).lower() for word in ['фио', 'name', 'full'])]
        group_columns = [col for col in df.columns if any(word in str(col).lower() for word in ['group', 'групп'])]
        phone_columns = [col for col in df.columns if
                         any(word in str(col).lower() for word in ['phone', 'телефон', 'тел'])]
        login_columns = [col for col in df.columns if any(word in str(col).lower() for word in ['login', 'username'])]
        password_columns = [col for col in df.columns if
                            any(word in str(col).lower() for word in ['password', 'пароль'])]
        email_columns = [col for col in df.columns if any(word in str(col).lower() for word in ['email', 'почта'])]
        iin_columns = [col for col in df.columns if any(word in str(col).lower() for word in ['iin', 'иин'])]

        if name_columns and 'full_name' not in df.columns:
            df['full_name'] = df[name_columns[0]]

        if group_columns and 'group' not in df.columns:
            df['group'] = df[group_columns[0]]

        if phone_columns and 'phone' not in df.columns:
            df['phone'] = df[phone_columns[0]]

        if login_columns and 'login' not in df.columns:
            df['login'] = df[login_columns[0]]

        if password_columns and 'password' not in df.columns:
            df['password'] = df[password_columns[0]]

        if email_columns and 'email' not in df.columns:
            df['email'] = df[email_columns[0]]

        if iin_columns and 'iin' not in df.columns:
            df['iin'] = df[iin_columns[0]]

        if 'login' not in df.columns:
            df = self._generate_logins(df)

        if 'password' not in df.columns:
            df = self._generate_passwords(df)

        if 'email' not in df.columns:
            df = self._generate_emails(df)

        return df

    def _generate_logins(self, df: pd.DataFrame) -> pd.DataFrame:
        df['login'] = ''

        for idx, row in df.iterrows():
            if 'login' in df.columns and row['login'] and pd.notna(row['login']):
                continue

            login_candidates = []

            if 'full_name' in df.columns and pd.notna(row.get('full_name')):
                name_parts = str(row['full_name']).split()
                if name_parts:
                    login_candidates.append(name_parts[0].lower())

            if 'group' in df.columns and pd.notna(row.get('group')):
                group = str(row['group']).replace(' ', '').replace('-', '_')
                login_candidates.append(group)

            if login_candidates:
                df.at[idx, 'login'] = '_'.join(login_candidates) + f"_{idx + 1:03d}"
            else:
                df.at[idx, 'login'] = f"user_{idx + 1:05d}"

        return df

    def _generate_passwords(self, df: pd.DataFrame) -> pd.DataFrame:
        df['password'] = ''

        for idx, row in df.iterrows():
            if 'password' in df.columns and row['password'] and pd.notna(row['password']):
                continue

            if 'group' in df.columns and pd.notna(row.get('group')):
                group = str(row['group']).replace(' ', '')
                df.at[idx, 'password'] = f"{group}_{idx + 1:04d}"
            else:
                df.at[idx, 'password'] = f"pass_{idx + 1:05d}"

        return df

    def _generate_emails(self, df: pd.DataFrame) -> pd.DataFrame:
        df['email'] = ''

        for idx, row in df.iterrows():
            if 'email' in df.columns and row['email'] and pd.notna(row['email']):
                continue

            if 'login' in df.columns and pd.notna(row.get('login')):
                login = str(row['login'])
                df.at[idx, 'email'] = f"{login}@kru.edu.kz"
            else:
                df.at[idx, 'email'] = f"user_{idx + 1:05d}@kru.edu.kz"

        return df

    def _generate_logins_passwords(self, df: pd.DataFrame) -> pd.DataFrame:
        df = self._generate_logins(df)
        df = self._generate_passwords(df)
        df = self._generate_emails(df)
        return df

    def _clean_iin(self, iin: Any) -> str:
        if iin is None:
            return ''

        if isinstance(iin, str):
            return re.sub(r'[^\d]', '', iin)
        elif isinstance(iin, (int, float)):
            return str(int(iin))
        return ''

    def get_credentials_by_iin(self, iin: str) -> Dict[str, Any]:
        try:
            if self.data.empty:
                return {
                    'success': False,
                    'error': 'База данных недоступна'
                }

            cleaned_iin = self._clean_iin(iin)
            if not cleaned_iin or len(cleaned_iin) != 12:
                return {
                    'success': False,
                    'error': 'Неверный формат ИИН. Должно быть 12 цифр.'
                }

            iin_column = None
            for col in self.data.columns:
                if any(word in str(col).lower() for word in ['iin', 'иин']):
                    iin_column = col
                    break

            if not iin_column:
                return {
                    'success': False,
                    'error': 'В данных отсутствует колонка с ИИН'
                }

            for index, row in self.data.iterrows():
                current_iin = self._clean_iin(row[iin_column])
                if current_iin == cleaned_iin:
                    credentials = {
                        'success': True,
                        'login': str(row.get('login', '')),
                        'password': str(row.get('password', '')),
                        'email': str(row.get('email', '')),
                        'group': str(row.get('group', '')),
                        'full_name': str(row.get('full_name', '')),
                        'iin': cleaned_iin
                    }

                    if not credentials['login'] or not credentials['password']:
                        return {
                            'success': False,
                            'error': 'В данных студента отсутствует логин или пароль'
                        }

                    logger.info(f"Найдены данные для: {credentials['full_name']}")
                    return credentials

            return {
                'success': False,
                'error': 'Студент с указанным ИИН не найден'
            }

        except Exception as e:
            logger.error(f"Ошибка поиска по ИИН: {e}")
            return {
                'success': False,
                'error': f'Внутренняя ошибка: {str(e)}'
            }

    def search_students(self, search_term: str, limit: int = 10) -> List[Dict[str, Any]]:
        try:
            if self.data.empty:
                return []

            results = []
            search_term_lower = search_term.lower()

            for index, row in self.data.iterrows():
                if len(results) >= limit:
                    break

                search_fields = ['full_name', 'group', 'iin', 'login']
                match_found = False

                for field in search_fields:
                    if field in row and pd.notna(row[field]):
                        value = str(row[field]).lower()
                        if search_term_lower in value:
                            match_found = True
                            break

                if match_found:
                    student_data = {
                        'full_name': str(row.get('full_name', 'Не указано')),
                        'group': str(row.get('group', 'Не указана')),
                        'iin': str(row.get('iin', 'Не указан')),
                        'login': str(row.get('login', 'Не указан'))
                    }
                    results.append(student_data)

            return results

        except Exception as e:
            logger.error(f"Ошибка поиска: {e}")
            return []

    def get_all_groups(self) -> List[str]:
        try:
            if self.data.empty:
                return []

            group_column = None
            for col in self.data.columns:
                if any(word in str(col).lower() for word in ['group', 'групп']):
                    group_column = col
                    break

            if not group_column:
                return []

            groups = self.data[group_column].dropna().unique()
            return sorted([str(g) for g in groups if str(g).strip()])

        except Exception as e:
            logger.error(f"Ошибка получения групп: {e}")
            return []

    def get_statistics(self) -> Dict[str, Any]:

        try:
            if self.data.empty:
                return {
                    'success': False,
                    'error': 'База данных пуста'
                }

            total_groups = len(self.get_all_groups())

            return {
                'success': True,
                'total_students': len(self.data),
                'total_groups': total_groups,
                'columns_available': list(self.data.columns),
                'sample_data': self._get_sample_data()
            }

        except Exception as e:
            logger.error(f"Ошибка статистики: {e}")
            return {
                'success': False,
                'error': str(e)
            }

    def _get_sample_data(self) -> List[Dict]:

        sample = []
        for i in range(min(3, len(self.data))):
            row = self.data.iloc[i]
            sample.append({
                'full_name': str(row.get('full_name', '')),
                'group': str(row.get('group', '')),
                'login': str(row.get('login', ''))
            })
        return sample

    def get_credentials_by_phone_and_name(self, phone: str, full_name: str) -> Dict[str, Any]:

        try:
            if self.data.empty:
                return {
                    'success': False,
                    'error': 'База данных недоступна'
                }


            phone_column = None
            for col in self.data.columns:
                if any(word in str(col).lower() for word in ['phone', 'телефон', 'тел']):
                    phone_column = col
                    break

            if not phone_column:
                return {
                    'success': False,
                    'error': 'Не найдена колонка с телефонами'
                }


            cleaned_phone = re.sub(r'[^\d+]', '', phone)

            for index, row in self.data.iterrows():
                student_phone = self._clean_phone_number(str(row[phone_column])) if pd.notna(row[phone_column]) else ''
                student_name = str(row.get('full_name', '')).lower()

                if student_phone == cleaned_phone and full_name.lower() in student_name:
                    return {
                        'success': True,
                        'login': str(row.get('login', '')),
                        'password': str(row.get('password', '')),
                        'email': str(row.get('email', '')),
                        'group': str(row.get('group', '')),
                        'full_name': str(row.get('full_name', ''))
                    }

            return {
                'success': False,
                'error': 'Данные не найдены'
            }

        except Exception as e:
            logger.error(f"Ошибка поиска по телефону: {e}")
            return {
                'success': False,
                'error': 'Внутренняя ошибка'
            }

    def _clean_phone_number(self, phone: str) -> str:

        cleaned = re.sub(r'[^\d+]', '', phone)

        if cleaned.startswith('87') and len(cleaned) == 11:
            return '+7' + cleaned[2:]
        elif cleaned.startswith('7') and len(cleaned) == 11:
            return '+' + cleaned
        elif cleaned.startswith('8') and len(cleaned) == 11:
            return '+7' + cleaned[1:]
        elif cleaned.startswith('+7') and len(cleaned) == 12:
            return cleaned

        return cleaned