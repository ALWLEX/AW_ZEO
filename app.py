# AW_ZEO/app.py


import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, WebAppInfo
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes, CallbackQueryHandler

from config import BOT_TOKEN, WEBAPP_URL
from database.db_handler import DatabaseHandler
from services.moodle_service import MoodleService
from services.schedule_service import ScheduleService
from services.ai_service import AIService

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)


class AWZeoBot:
    def __init__(self):
        logger.info(" Создание приложения бота...")
        self.application = Application.builder().token(BOT_TOKEN).build()

        try:
            self.db = DatabaseHandler()
            self.moodle_service = MoodleService()
            self.schedule_service = ScheduleService()
            self.ai_service = AIService()
            logger.info("✅ Все сервисы инициализированы успешно")
        except Exception as e:
            logger.error(f"❌ Ошибка инициализации сервисов: {e}")
            raise

        logger.info("🔧 Настройка обработчиков...")
        self.setup_handlers()
        logger.info("✅ Бот инициализирован!")

    def setup_handlers(self):

        self.application.add_handler(CommandHandler("start", self.start))
        self.application.add_handler(CommandHandler("help", self.help))
        self.application.add_handler(CommandHandler("app", self.open_app))
        self.application.add_handler(CommandHandler("moodle", self.moodle_info))
        self.application.add_handler(CommandHandler("schedule", self.schedule_info))
        self.application.add_handler(CommandHandler("admission", self.admission_info))
        self.application.add_handler(CallbackQueryHandler(self.button_handler))
        self.application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, self.handle_message))
        self.application.add_handler(MessageHandler(filters.CONTACT, self.handle_contact))

    async def start(self, update: Update, context: ContextTypes.DEFAULT_TYPE):

        user = update.effective_user

        welcome_text = f"""
🎓 *Добро пожаловать в AW_ZEO, {user.first_name}!*

🤖 *Ваш умный помощник в КРУ им. А. Байтурсынова*

✨ *Что умеет AW_ZEO:*
• 📅 *Расписание пар* - актуальное расписание для вашей группы
• 🎓 *Доступ к Moodle* - логины и пароли для системы обучения  
• 🧩 *Профориентация* - тест Климова для выбора профессии
• 🎯 *Поступление* - вся информация для абитуриентов
• 🤖 *AI помощник* - ответы на любые вопросы

📱 *Для начала работы предоставьте ваш номер телефона:*
        """

        keyboard = [
            [InlineKeyboardButton("📞 Предоставить номер телефона", request_contact=True)],
            [InlineKeyboardButton("📱 Открыть приложение", web_app=WebAppInfo(url=WEBAPP_URL))]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)

        await update.message.reply_text(
            welcome_text,
            reply_markup=reply_markup,
            parse_mode='Markdown'
        )

    async def handle_contact(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        user = update.effective_user
        contact = update.message.contact


        self.db.save_user(
            user_id=user.id,
            username=user.username,
            first_name=user.first_name,
            last_name=user.last_name,
            phone_number=contact.phone_number
        )

        await update.message.reply_text(
            "✅ *Спасибо! Номер телефона сохранен.*\n\n"
            "Теперь вы можете получить доступ к вашим данным Moodle. "
            "Для этого отправьте мне ваше ФИО или ИИН.",
            parse_mode='Markdown'
        )

    async def handle_message(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        user = update.effective_user
        text = update.message.text


        user_data = self.db.get_user(user.id)

        if not user_data or not user_data.phone_number:

            await update.message.reply_text(
                "📞 *Для доступа к функциям бота необходимо предоставить номер телефона.*\n\n"
                "Нажмите кнопку ниже или используйте команду /start",
                reply_markup=InlineKeyboardMarkup([[
                    InlineKeyboardButton("📞 Предоставить номер", request_contact=True)
                ]]),
                parse_mode='Markdown'
            )
            return


        if any(keyword in text.lower() for keyword in ['логин', 'пароль', 'moodle', 'данные', 'учетные']):
            await self.handle_moodle_request(update, user_data, text)

        elif any(keyword in text.lower() for keyword in ['расписание', 'пары', 'когда учиться', 'распис']):
            await self.handle_schedule_request(update, text)
        else:

            response = await self.ai_service.process_natural_language(text, user.id)
            await update.message.reply_text(response)

    async def handle_moodle_request(self, update: Update, user_data, text: str):

        credentials = self.moodle_service.get_credentials_by_phone_and_name(
            user_data.phone_number,
            text
        )

        if credentials.get('success'):
            response = f"""
🎓 *Ваши учетные данные для Moodle:*

👤 *ФИО:* {credentials['full_name']}
📚 *Группа:* {credentials['group']}
🔑 *Логин:* `{credentials['login']}`
🔒 *Пароль:* `{credentials['password']}`
📧 *Email:* {credentials['email']}

💡 *Сохраните эти данные в надежном месте!*
            """
        else:
            response = f"""
❌ *Не удалось найти ваши данные.*

*Возможные причины:*
• Проверьте правильность ФИО или ИИН
• Убедитесь, что вы учитесь в КРУ
• Обратитесь в техническую поддержку

*Попробуйте отправить:*
• Ваше полное ФИО (как в документах)
• Или ваш ИИН
            """

        await update.message.reply_text(response, parse_mode='Markdown')

    async def handle_schedule_request(self, update: Update, text: str):


        response = """
📅 *Для просмотра расписания:*

1. Откройте приложение AW_ZEO
2. Перейдите в раздел "Расписание"
3. Выберите вашу группу
4. Выберите нужный день

🚀 *Открыть приложение:*
        """

        keyboard = [[InlineKeyboardButton("📱 Открыть AW_ZEO", web_app=WebAppInfo(url=WEBAPP_URL))]]
        reply_markup = InlineKeyboardMarkup(keyboard)

        await update.message.reply_text(response, reply_markup=reply_markup, parse_mode='Markdown')

    async def moodle_info(self, update: Update, context: ContextTypes.DEFAULT_TYPE):

        moodle_text = """
 *Доступ к системе Moodle*

*Для получения ваших учетных данных:*
1. Предоставьте номер телефона (если еще не сделали)
2. Отправьте боту ваше ФИО или ИИН
3. Получите логин и пароль


 *Важные данные:*
• Логин и пароль индивидуальны для каждого студента
• После первого входа рекомендуется сменить пароль
• При проблемах обращайтесь в техническую поддержку

        """

        keyboard = [
            [InlineKeyboardButton("📞 Предоставить номер", request_contact=True)],
            [InlineKeyboardButton("📱 Открыть приложение", web_app=WebAppInfo(url=WEBAPP_URL))]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)

        await update.message.reply_text(
            moodle_text,
            reply_markup=reply_markup,
            parse_mode='Markdown'
        )

    async def schedule_info(self, update: Update, context: ContextTypes.DEFAULT_TYPE):

        schedule_text = """
📅 *Расписание занятий*

*В приложении AW_ZEO вы можете:*
• Просматривать расписание для вашей группы
• Видеть пары на сегодня, завтра или любую дату
• Узнавать время, аудитории и преподавателей

*Как посмотреть расписание:*
1. Откройте приложение AW_ZEO
2. Перейдите в раздел "Расписание"
3. Выберите вашу группу
4. Выберите нужную дату

🔄 *Расписание обновляется ежедневно*
        """

        keyboard = [[InlineKeyboardButton("📱 Открыть приложение", web_app=WebAppInfo(url=WEBAPP_URL))]]
        reply_markup = InlineKeyboardMarkup(keyboard)

        await update.message.reply_text(
            schedule_text,
            reply_markup=reply_markup,
            parse_mode='Markdown'
        )

    async def admission_info(self, update: Update, context: ContextTypes.DEFAULT_TYPE):

        admission_text = """
🎯 *Поступление в КРУ*

*Для абитуриентов доступно:*
• 🧩 *Тест Климова* - профориентация и выбор профессии
• 📊 *Образовательные программы* - полный список специальностей
• 🎓 *Проходные баллы* - информация по конкурсу

*Как воспользоваться:*
1. Откройте приложение AW_ZEO
2. Перейдите в раздел "Поступление"
3. Выберите нужную вкладку

🎓 *Уровни образования:*
• Бакалавриат
• Магистратура  
• Докторантура
        """

        keyboard = [[InlineKeyboardButton("📱 Открыть приложение", web_app=WebAppInfo(url=WEBAPP_URL))]]
        reply_markup = InlineKeyboardMarkup(keyboard)

        await update.message.reply_text(
            admission_text,
            reply_markup=reply_markup,
            parse_mode='Markdown'
        )

    async def open_app(self, update: Update, context: ContextTypes.DEFAULT_TYPE):

        app_text = f"""
🚀 *Открытие AW_ZEO приложения*

🌐 *Ссылка для доступа:*
{WEBAPP_URL}

💡 *Два способа открыть:*
1. *В Telegram* - нажмите кнопку ниже (откроется как приложение)
2. *В браузере* - скопируйте ссылку выше

📱 *Доступные разделы:*
• *Главная* - быстрый доступ ко всем функциям
• *Расписание* - ваше актуальное расписание пар
• *Moodle* - учетные данные для входа
• *Поступление* - информация для абитуриентов
        """

        keyboard = [
            [InlineKeyboardButton("📱 Открыть в Telegram", web_app=WebAppInfo(url=WEBAPP_URL))],
            [InlineKeyboardButton("🔗 Открыть в браузере", url=WEBAPP_URL)]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)

        await update.message.reply_text(
            app_text,
            reply_markup=reply_markup,
            parse_mode='Markdown',
            disable_web_page_preview=True
        )

    async def help(self, update: Update, context: ContextTypes.DEFAULT_TYPE):

        help_text = """
📖 *Помощь по AW_ZEO*

*Основные команды:*
/start - главное меню
/app - открыть Web приложение
/schedule - информация о расписании
/moodle - доступ к системе Moodle
/admission - информация о поступлении
/help - эта справка

*Как получить данные Moodle:*
1. Нажмите /start и предоставьте номер телефона
2. Отправьте боту ваше ФИО или ИИН
3. Получите логин и пароль

*Поддержка:*
При технических проблемах обращайтесь в поддержку университета.
        """

        keyboard = [
            [InlineKeyboardButton("📱 Открыть приложение", web_app=WebAppInfo(url=WEBAPP_URL))],
            [InlineKeyboardButton("📞 Поддержка", callback_data="support")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)

        await update.message.reply_text(
            help_text,
            reply_markup=reply_markup,
            parse_mode='Markdown'
        )

    async def button_handler(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Обработка нажатий кнопок"""
        query = update.callback_query
        await query.answer()

        if query.data == "support":
            text = "📞 *Техническая поддержка*\n\nТелефон: +7 (7142) 51-11-57\nEmail: support@kru.edu.kz"
        else:
            text = "🚀 *Открытие приложения*"

        keyboard = [[InlineKeyboardButton("📱 Открыть AW_ZEO", web_app=WebAppInfo(url=WEBAPP_URL))]]
        reply_markup = InlineKeyboardMarkup(keyboard)

        await query.edit_message_text(
            text=text,
            reply_markup=reply_markup,
            parse_mode='Markdown'
        )