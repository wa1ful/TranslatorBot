import telebot
from googletrans import Translator

bot = telebot.TeleBot("8102994026:AAFImRPgtDOkXYQ1qrN04xIkp9j003nzQtA")
translator = Translator()

@bot.message_handler(commands=['start'])
def send_welcome(message):
    bot.reply_to(message, "Привет! Отправь мне текст для перевода")

@bot.message_handler(func=lambda message: True)
def handle_text(message):
    try:
        text = message.text
        
        detected = translator.detect(text)
        lang = detected.lang
        
        if lang == 'ru':
            translation = translator.translate(text, dest='en')
            response = f"🇷🇺 Русский: {text}\n\n🇺🇸 Английский: {translation.text}"
        else:
            translation = translator.translate(text, dest='ru')
            response = f"🇺🇸 English: {text}\n\n🇷🇺 Russian: {translation.text}"
        
        bot.reply_to(message, response)
        
    except Exception as e:
        bot.reply_to(message, "Ошибка перевода")

bot.infinity_polling()