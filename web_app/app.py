# AW_ZEO/web_app/app.py


from flask import Flask, render_template, request, jsonify, session
import logging
from datetime import datetime

from config import FLASK_HOST, FLASK_PORT, FLASK_DEBUG
from database.db_handler import DatabaseHandler
from services.moodle_service import MoodleService
from services.schedule_service import ScheduleService
from services.admission_service import AdmissionService
from services.ai_service import AIService


logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


app = Flask(__name__)
app.secret_key = 'aw_zeo_secret_key_2024'


try:
    db = DatabaseHandler()
    logger.info("✅ DatabaseHandler инициализирован успешно")
except Exception as e:
    logger.error(f"❌ Ошибка инициализации DatabaseHandler: {e}")
    raise

try:
    from services.moodle_service import MoodleService
    moodle_service = MoodleService()
    logger.info("✅ MoodleService инициализирован успешно")
except Exception as e:
    logger.error(f"❌ Ошибка инициализации MoodleService: {e}")
    class FallbackMoodleService:
        def get_statistics(self):
            return {'success': False, 'error': 'Сервис недоступен'}
        def search_students(self, *args, **kwargs):
            return []
        def get_credentials_by_iin(self, iin):
            return {'success': False, 'error': 'Сервис недоступен'}
        def get_all_groups(self):
            return []
        def verify_credentials(self, *args, **kwargs):
            return {'success': False, 'error': 'Сервис недоступен'}
        def get_credentials_by_phone_and_name(self, *args, **kwargs):
            return {'success': False, 'error': 'Сервис недоступен'}
    moodle_service = FallbackMoodleService()

try:
    schedule_service = ScheduleService()
    logger.info("✅ ScheduleService инициализирован успешно")
except Exception as e:
    logger.error(f"❌ Ошибка инициализации ScheduleService: {e}")
    raise

try:
    admission_service = AdmissionService()
    logger.info("✅ AdmissionService инициализирован успешно")
except Exception as e:
    logger.error(f"❌ Ошибка инициализации AdmissionService: {e}")
    raise

try:
    ai_service = AIService()
    logger.info("✅ AIService инициализирован успешно")
except Exception as e:
    logger.error(f"❌ Ошибка инициализации AIService: {e}")
    raise


@app.route('/')
def index():
    return render_template('index.html')



@app.route('/api/schedule')
def get_schedule():
    try:
        group = request.args.get('group')
        day = request.args.get('day')

        if not group or not day:
            return jsonify({'success': False, 'error': 'Не указана группа или день'})

        schedule_data = {
            'group': group,
            'day_of_week': day,
            'schedule': schedule_service.find_group_schedule(group, day),
            'status': 'success'
        }

        return jsonify({'success': True, 'data': schedule_data})

    except Exception as e:
        logger.error(f"Ошибка получения расписания: {e}")
        return jsonify({'success': False, 'error': str(e)})


@app.route('/api/moodle/credentials')
def get_moodle_credentials():
    try:
        iin = request.args.get('iin')

        if not iin:
            return jsonify({'success': False, 'error': 'Не указан ИИН'})

        credentials = moodle_service.get_credentials_by_iin(iin)

        if credentials.get('success', False):
            return jsonify({'success': True, 'data': credentials})
        else:
            return jsonify({'success': False, 'error': credentials.get('error', 'Данные не найдены')})

    except Exception as e:
        logger.error(f"Ошибка получения данных Moodle: {e}")
        return jsonify({'success': False, 'error': str(e)})


@app.route('/api/moodle/search')
def search_students():
    try:
        search_term = request.args.get('q', '')
        limit = request.args.get('limit', 10, type=int)

        if not search_term or len(search_term) < 2:
            return jsonify({'success': False, 'error': 'Слишком короткий поисковый запрос'})

        results = moodle_service.search_students(search_term, limit)
        return jsonify({'success': True, 'data': results})

    except Exception as e:
        logger.error(f"Ошибка поиска студентов: {e}")
        return jsonify({'success': False, 'error': str(e)})


@app.route('/api/moodle/groups')
def get_groups():
    try:
        groups = moodle_service.get_all_groups()
        return jsonify({'success': True, 'data': groups})
    except Exception as e:
        logger.error(f"Ошибка получения списка групп: {e}")
        return jsonify({'success': False, 'error': str(e)})


@app.route('/api/moodle/verify', methods=['POST'])
def verify_credentials():
    try:
        data = request.json
        login = data.get('login')
        password = data.get('password')

        if not login or not password:
            return jsonify({'success': False, 'error': 'Не указан логин или пароль'})

        result = moodle_service.verify_credentials(login, password)
        return jsonify(result)

    except Exception as e:
        logger.error(f"Ошибка проверки учетных данных: {e}")
        return jsonify({'success': False, 'error': str(e)})


@app.route('/api/moodle/statistics')
def get_moodle_statistics():
    try:
        stats = moodle_service.get_statistics()
        return jsonify(stats)
    except Exception as e:
        logger.error(f"Ошибка получения статистики: {e}")
        return jsonify({'success': False, 'error': str(e)})


@app.route('/api/moodle/credentials-by-phone', methods=['POST'])
def get_credentials_by_phone():
    try:
        data = request.json
        phone = data.get('phone')
        full_name = data.get('full_name')

        if not phone or not full_name:
            return jsonify({'success': False, 'error': 'Не указан номер телефона или ФИО'})

        result = moodle_service.get_credentials_by_phone_and_name(phone, full_name)
        return jsonify(result)

    except Exception as e:
        logger.error(f"Ошибка получения данных по телефону: {e}")
        return jsonify({'success': False, 'error': str(e)})


@app.route('/api/admission/programs')
def get_programs():
    try:
        program_type = request.args.get('type', 'bachelor')
        programs = admission_service.get_programs(program_type)
        return jsonify({'success': True, 'data': programs})
    except Exception as e:
        logger.error(f"Ошибка получения программ: {e}")
        return jsonify({'success': False, 'error': str(e)})


@app.route('/api/admission/klimov-test')
def get_klimov_test():
    try:
        test_data = admission_service.get_klimov_test()
        return jsonify({'success': True, 'data': test_data})
    except Exception as e:
        logger.error(f"Ошибка получения теста: {e}")
        return jsonify({'success': False, 'error': str(e)})


@app.route('/api/admission/recommendations', methods=['POST'])
def get_recommendations():
    try:
        answers = request.json.get('answers', [])
        recommendations = admission_service.get_recommendations(answers)
        return jsonify({'success': True, 'data': recommendations})
    except Exception as e:
        logger.error(f"Ошибка получения рекомендаций: {e}")
        return jsonify({'success': False, 'error': str(e)})


@app.route('/api/admission/search-programs')
def search_programs_by_subjects():
    try:
        subject1 = request.args.get('subject1')
        subject2 = request.args.get('subject2')

        if not subject1 or not subject2:
            return jsonify({'success': False, 'error': 'Не указаны предметы'})

        results = admission_service.search_programs_by_subjects(subject1, subject2)
        return jsonify({'success': True, 'data': results})

    except Exception as e:
        logger.error(f"Ошибка поиска программ: {e}")
        return jsonify({'success': False, 'error': str(e)})


@app.route('/api/ai/chat', methods=['POST'])
def ai_chat():
    try:
        message = request.json.get('message', '')
        user_id = request.json.get('user_id', 'guest')

        response = ai_service.process_message(message, user_id)
        return jsonify({'success': True, 'response': response})
    except Exception as e:
        logger.error(f"Ошибка AI чата: {e}")
        return jsonify({'success': False, 'error': str(e)})


@app.route('/api/system/health')
def health_check():
    try:
        services_status = {
            'moodle': moodle_service.get_statistics(),
            'schedule': 'active',
            'admission': 'active',
            'ai': 'active'
        }

        return jsonify({
            'success': True,
            'status': 'healthy',
            'timestamp': datetime.now().isoformat(),
            'services': services_status
        })
    except Exception as e:
        logger.error(f"Ошибка health check: {e}")
        return jsonify({
            'success': False,
            'status': 'unhealthy',
            'error': str(e)
        })


if __name__ == '__main__':
    logger.info(f"Запуск Web App на {FLASK_HOST}:{FLASK_PORT}")
    app.run(
        host=FLASK_HOST,
        port=FLASK_PORT,
        debug=FLASK_DEBUG
    )