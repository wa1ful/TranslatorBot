import telebot
from googletrans import Translator, LANGUAGES

bot = telebot.TeleBot("8102994026:AAFImRPgtDOkXYQ1qrN04xIkp9j003nzQtA")
translator = Translator()

user_states = {}

@bot.message_handler(commands=['start'])
def send_welcome(message):
    markup = telebot.types.ReplyKeyboardMarkup(resize_keyboard=True)
    markup.add('Перевести текст', 'Изменить язык перевода')
    bot.send_message(message.chat.id, 
                    "Привет! Я бот-переводчик.\n\n"
                    "Перевести текст - перевести текст\n"
                    "Изменить язык перевода - выбрать язык перевода\n\n"
                    "По умолчанию: русский ↔ английский", 
                    reply_markup=markup)

@bot.message_handler(commands=['language'])
def change_language(message):
    show_language_selection(message.chat.id)

@bot.message_handler(func=lambda message: message.text == 'Изменить язык перевода')
def handle_change_language(message):
    show_language_selection(message.chat.id)

@bot.message_handler(func=lambda message: message.text == 'Перевести текст')
def handle_translate_request(message):
    user_states[message.chat.id] = 'waiting_for_text'
    bot.send_message(message.chat.id, "Отправьте текст для перевода:", reply_markup=telebot.types.ReplyKeyboardRemove())

def show_language_selection(chat_id):
    markup = telebot.types.InlineKeyboardMarkup(row_width=2)
    
    popular_languages = [
        ('Английский', 'en'),
        ('Русский', 'ru'),
        ('Испанский', 'es'),
        ('Французский', 'fr'),
        ('Немецкий', 'de'),
        ('Китайский', 'zh-cn'),
        ('Японский', 'ja'),
        ('Корейский', 'ko'),
        ('Арабский', 'ar'),
        ('Итальянский', 'it')
    ]
    
    buttons = []
    for name, code in popular_languages:
        buttons.append(telebot.types.InlineKeyboardButton(name, callback_data=f"lang_{code}"))
    
    for i in range(0, len(buttons), 2):
        if i + 1 < len(buttons):
            markup.add(buttons[i], buttons[i+1])
        else:
            markup.add(buttons[i])
    
    bot.send_message(chat_id, "Выберите язык перевода:", reply_markup=markup)

@bot.callback_query_handler(func=lambda call: call.data.startswith('lang_'))
def handle_language_selection(call):
    lang_code = call.data[5:]
    
    if isinstance(user_states.get(call.message.chat.id), dict):
        user_states[call.message.chat.id]['target_lang'] = lang_code
    else:
        user_states[call.message.chat.id] = {'target_lang': lang_code}
    
    lang_name = LANGUAGES.get(lang_code, lang_code).title()
    bot.edit_message_text(
        f"Язык перевода установлен: {lang_name}",
        call.message.chat.id,
        call.message.message_id
    )
    
    markup = telebot.types.ReplyKeyboardMarkup(resize_keyboard=True)
    markup.add('Перевести текст', 'Изменить язык перевода')
    bot.send_message(call.message.chat.id, 
                    f"Теперь текст будет переводиться на {lang_name}.\n"
                    "Нажмите Перевести текст чтобы начать перевод.", 
                    reply_markup=markup)

@bot.message_handler(func=lambda message: True)
def handle_text(message):
    chat_id = message.chat.id
    current_state = user_states.get(chat_id)
    
    if current_state == 'waiting_for_text':
        text = message.text
        
        if isinstance(user_states.get(chat_id), dict):
            target_lang = user_states[chat_id].get('target_lang', 'en')
        else:
            target_lang = 'en'
        
        detected = translator.detect(text)
        source_lang = detected.lang
        translation = translator.translate(text, dest=target_lang)
        
        source_lang_name = LANGUAGES.get(source_lang, source_lang).title()
        target_lang_name = LANGUAGES.get(target_lang, target_lang).title()
        
        response = (f"Исходный текст ({source_lang_name}):\n{text}\n\n"
                    f"Перевод ({target_lang_name}):\n{translation.text}")
        
        bot.reply_to(message, response)
        
        markup = telebot.types.ReplyKeyboardMarkup(resize_keyboard=True)
        markup.add('Перевести текст', 'Изменить язык перевода')
        bot.send_message(chat_id, "Выберите действие:", reply_markup=markup)
        
        user_states[chat_id] = {'target_lang': target_lang}
        
    elif isinstance(current_state, dict) and 'target_lang' in current_state:
        text = message.text
        target_lang = current_state['target_lang']
        
        detected = translator.detect(text)
        source_lang = detected.lang
        translation = translator.translate(text, dest=target_lang)
        
        source_lang_name = LANGUAGES.get(source_lang, source_lang).title()
        target_lang_name = LANGUAGES.get(target_lang, target_lang).title()
        
        response = (f"Исходный текст ({source_lang_name}):\n{text}\n\n"
                    f"Перевод ({target_lang_name}):\n{translation.text}")
        
        bot.reply_to(message, response)
        
    else:
        text = message.text
        detected = translator.detect(text)
        lang = detected.lang
        
        if lang == 'ru':
            translation = translator.translate(text, dest='en')
            response = f"Русский: {text}\n\nАнглийский: {translation.text}"
        else:
            translation = translator.translate(text, dest='ru')
            response = f"English: {text}\n\nRussian: {translation.text}"
        
        bot.reply_to(message, response)
        
        markup = telebot.types.ReplyKeyboardMarkup(resize_keyboard=True)
        markup.add('Перевести текст', 'Изменить язык перевода')
        bot.send_message(chat_id, 
                        "Хотите переводить на другие языки? "
                        "Используйте кнопки ниже:", 
                        reply_markup=markup)

if __name__ == "__main__":
    bot.infinity_polling()
