import telebot
bot = telebot.TeleBot('8436786454:AAFZPl-QJDAi6yfh6oIF-qBg56uuxg3Arj8')
from telebot import types

@bot.message_handler(commands=['start'])
def start(message):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    btn1 = types.KeyboardButton("Начать")
    markup.add(btn1)
    bot.send_message(message.from_user.id, "Скоро тут будет история, пока воть", reply_markup=markup)

@bot.message_handler(content_types=['text'])
def get_text_messages(message):
    #первые кнопки, ознакомление с правилами и начало игры
    if message.text == 'Начать':
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True) #создание новых кнопок
        btn1 = types.KeyboardButton('Помощь')
        btn2 = types.KeyboardButton('Правила пользования')
        btn3 = types.KeyboardButton('Начать приключение')
        markup.add(btn1, btn2, btn3)
        bot.send_message(message.from_user.id, 'Задайте интересующий вопрос', reply_markup=markup) #ответ бота
    elif message.text == 'Помощь':
        bot.send_message(message.from_user.id, 'Здесь будет пара кнопок перехода в инфо канал', parse_mode='Markdown')
    elif message.text == 'Правила пользования':
        bot.send_message(message.from_user.id, 'Подробно вы можете ознакомиться с правилами ' + '[тут](https://telegra.ph/Pravila-polzovaniya-bota-11-11)', parse_mode='Markdown')
    #вторая кнопка, даём персонажу имя
    if message.text == 'Начать приключение':
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True) #создание новых кнопок
        btn1 = types.KeyboardButton('Назвать персонажа')
        markup.add(btn1)
        bot.send_message(message.from_user.id, 'Дайте своему герою имя', reply_markup=markup) #ответ бота
#Начиная с этого момента код не работает, пока разбираюсь как дать ему текст, чтобы он его запомнил и не забывал пользователя
    if message.text == 'Дайте своему герою имя':
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True) #создание новых кнопок
        btn1 = types.KeyboardButton('Username')
        markup.add(btn1)
    elif message.text == 'Username':
        bot.send_message(message.chat.id, 'Ваше имя будет: ' + message.text, parse_mode='Markdown')
    
    if message.text == 'Ваше имя будет: ':
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True) #создание новых кнопок
        btn1 = types.KeyboardButton('Все верно')
        btn1 = types.KeyboardButton('Переделаем')
        markup.add(btn1, btn2)
    elif message.text == 'Переделаем':
        bot.send_message(message.chat.id, 'Ваше имя будет: ' + message.text, parse_mode='Markdown') #ответ бота
    
    if message.text == 'Все верно':
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True) #создание новых кнопок
        btn1 = types.KeyboardButton('Начнем игру')

bot.polling(none_stop=True, interval=0) #обязательная для работы бота часть




