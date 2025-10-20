import telebot
bot = telebot.TeleBot('Тут будет айпишка')
from telebot import types

@bot.message_handler(commands=['start'])
def start(message):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    btn1 = types.KeyboardButton("Начать")
    markup.add(btn1)
    bot.send_message(message.from_user.id, "Скоро тут будет история, пока воть", reply_markup=markup)

@bot.message_handler(content_types=['text'])
def get_text_messages(message):
    if message.text == 'Начать':
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True) #создание новых кнопок
        btn1 = types.KeyboardButton('Помощь')
        btn2 = types.KeyboardButton('Правила пользования')
        markup.add(btn1, btn2)
        bot.send_message(message.from_user.id, 'Задайте интересующий вопрос', reply_markup=markup) #ответ бота
    elif message.text == 'Помощь':
        bot.send_message(message.from_user.id, 'Здесь будет пара кнопок перехода в инфо канал', parse_mode='Markdown')
    elif message.text == 'Правила пользования':
        bot.send_message(message.from_user.id, 'Правил пока нет', parse_mode='Markdown')
        


