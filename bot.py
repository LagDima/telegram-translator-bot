import os
import asyncio
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, MessageHandler, filters, ContextTypes
from deep_translator import GoogleTranslator

# ========== НАСТРОЙКИ ==========
TOKEN = "8858772185:AAGRTCwpkqzMdnqfBZhdch3wAUPWmeEnT8Y"  # Замените на токен от @BotFather
DEFAULT_LANG = "ru"            # Язык по умолчанию

# Словарь с кнопками: код языка -> название на кнопке
LANGUAGES = {
    "ru": "🇷🇺 Русский",
    "en": "🇬🇧 English",
    "de": "🇩🇪 Deutsch",
    "fr": "🇫🇷 Français",
    "es": "🇪🇸 Español",
    "zh": "🇨🇳 中文",
    "ja": "🇯🇵 日本語",
    "ko": "🇰🇷 한국어",
    "it": "🇮🇹 Italiano",
    "tr": "🇹🇷 Türkçe",
    "pl": "🇵🇱 Polski",
}

# Хранилище выбранных языков (в реальном боте лучше использовать базу данных)
user_languages = {}

# ========== ФУНКЦИИ ==========
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработчик команды /start"""
    user_id = update.effective_user.id
    user_languages[user_id] = DEFAULT_LANG
    
    keyboard = [[InlineKeyboardButton("🌐 Выбрать язык", callback_data="choose_lang")]]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await update.message.reply_text(
        "✍️ *Привет! Я переводчик для иностранных статей.*\n\n"
        "📌 *Как пользоваться:*\n"
        "1️⃣ Отправь мне текст на любом языке\n"
        "2️⃣ Нажми на кнопку выбора языка внизу\n"
        "3️⃣ Получи готовый перевод!\n\n"
        f"🌍 *Текущий язык перевода:* {LANGUAGES.get(DEFAULT_LANG, DEFAULT_LANG)}",
        reply_markup=reply_markup,
        parse_mode="Markdown"
    )

async def choose_language(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Показать кнопки выбора языка"""
    query = update.callback_query
    await query.answer()
    
    keyboard = []
    row = []
    for i, (code, name) in enumerate(LANGUAGES.items()):
        row.append(InlineKeyboardButton(name, callback_data=f"set_lang_{code}"))
        if (i + 1) % 2 == 0:  # по 2 кнопки в ряд
            keyboard.append(row)
            row = []
    if row:
        keyboard.append(row)
    
    keyboard.append([InlineKeyboardButton("🔙 Назад", callback_data="back")])
    await query.edit_message_text(
        "🌐 *Выберите язык для перевода:*",
        reply_markup=InlineKeyboardMarkup(keyboard),
        parse_mode="Markdown"
    )

async def set_language(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Установить язык перевода"""
    query = update.callback_query
    await query.answer()
    
    lang_code = query.data.replace("set_lang_", "")
    user_id = update.effective_user.id
    user_languages[user_id] = lang_code
    
    keyboard = [[InlineKeyboardButton("🌐 Сменить язык", callback_data="choose_lang")]]
    
    await query.edit_message_text(
        f"✅ *Язык перевода изменён на:* {LANGUAGES.get(lang_code, lang_code)}\n\n"
        "✍️ Теперь отправь мне текст для перевода!",
        reply_markup=InlineKeyboardMarkup(keyboard),
        parse_mode="Markdown"
    )

async def back_to_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Вернуться в главное меню"""
    query = update.callback_query
    await query.answer()
    
    user_id = update.effective_user.id
    current_lang = user_languages.get(user_id, DEFAULT_LANG)
    
    keyboard = [[InlineKeyboardButton("🌐 Выбрать язык", callback_data="choose_lang")]]
    await query.edit_message_text(
        f"🏠 *Главное меню*\n\n"
        f"🌍 Текущий язык перевода: {LANGUAGES.get(current_lang, current_lang)}\n\n"
        f"📤 Отправь мне текст, и я переведу его на выбранный язык!",
        reply_markup=InlineKeyboardMarkup(keyboard),
        parse_mode="Markdown"
    )

async def translate_text(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    target_lang = user_languages.get(user_id, DEFAULT_LANG)
    original_text = update.message.text
    
    await update.message.chat.send_action(action="typing")
    
    try:
        # Убираем detect - используем source='auto'
        translator = GoogleTranslator(source='auto', target=target_lang)
        translated = translator.translate(original_text)
        
        keyboard = [[InlineKeyboardButton("🌐 Сменить язык", callback_data="choose_lang")]]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        response = (
            f"🔹 *Исходный язык:* автоматически\n"
            f"🔸 *Перевод на:* {LANGUAGES.get(target_lang, target_lang)}\n\n"
            f"📝 *Результат:*\n{translated}"
        )
        
        await update.message.reply_text(response, reply_markup=reply_markup, parse_mode="Markdown")
        
    except Exception as e:
        await update.message.reply_text(
            f"❌ *Ошибка перевода:* {str(e)[:100]}\n\nПроверьте VPN и попробуйте снова.",
            parse_mode="Markdown"
        )
        print(f"Translation error: {e}")
# ========== ЗАПУСК ==========
def main():
    app = Application.builder().token(TOKEN).build()
    
    # Команды
    app.add_handler(CommandHandler("start", start))
    
    # Callback'и кнопок
    app.add_handler(CallbackQueryHandler(choose_language, pattern="^choose_lang$"))
    app.add_handler(CallbackQueryHandler(set_language, pattern="^set_lang_"))
    app.add_handler(CallbackQueryHandler(back_to_menu, pattern="^back$"))
    
    # Перевод текста
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, translate_text))
    
    print("🤖 Бот запущен...")
    app.run_polling(allowed_updates=["message", "callback_query"])

if __name__ == "__main__":
    main()