import telebot
bot = telebot.TeleBot('8436786454:AAFZPl-QJDAi6yfh6oIF-qBg56uuxg3Arj8')
from telebot import types

@bot.message_handler(commands=['start'])
def start(message):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    btn1 = types.KeyboardButton("Начать")
    markup.add(btn1)
    bot.send_message(message.from_user.id, "Скоро тут будет история, пока воть", reply_markup=markup)

user_names = {}  # словарь для имён

@bot.message_handler(content_types=['text'])
def get_text_messages(message):
    user_id = message.from_user.id  # Получаем ID пользователя

    # Первые кнопки, ознакомление с правилами и начало игры
    if message.text == 'Начать':
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True)  # Создание новых кнопок
        btn1 = types.KeyboardButton('Помощь')
        btn2 = types.KeyboardButton('Правила пользования')
        btn3 = types.KeyboardButton('Начать приключение')
        markup.add(btn1, btn2, btn3)
        bot.send_message(message.from_user.id, 'Задайте интересующий вопрос', reply_markup=markup)  # Ответ бота

    elif message.text == 'Помощь':
        bot.send_message(message.from_user.id, 'Здесь будет пара кнопок перехода в инфо канал', parse_mode='Markdown')

    elif message.text == 'Правила пользования':
        bot.send_message(message.from_user.id, 'Подробно вы можете ознакомиться с правилами ' + '[тут](https://telegra.ph/Pravila-polzovaniya-botom-03-09)', parse_mode='Markdown')

    # Вторая кнопка, даём персонажу имя
    elif message.text == 'Начать приключение':
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True)  # Создание новых кнопок
        btn1 = types.KeyboardButton('Назвать персонажа')
        markup.add(btn1)
        bot.send_message(message.from_user.id, 'Дайте своему герою имя', reply_markup=markup)  # Ответ бота

    elif message.text == 'Назвать персонажа':
        bot.send_message(message.from_user.id, 'Введите имя вашего персонажа')

    # Сохраняем введенное имя в словарь
    elif user_id not in user_names:
        user_names[user_id] = message.text  # Сохраняем имя пользователя
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True)  # Создание новых кнопок
        btn1 = types.KeyboardButton('Все верно')
        markup.add(btn1)
        bot.send_message(message.from_user.id, f'Ваше имя будет: {user_names[user_id]}', reply_markup=markup)

    elif message.text == 'Все верно':
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True)  # Создание новых кнопок
        btn1 = types.KeyboardButton('Начнем игру')
        markup.add(btn1)
        bot.send_message(message.from_user.id, 'Имя сохранено. Нажмите "Начнем игру", чтобы продолжить.', reply_markup=markup)

    elif message.text == 'Начнем игру':
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
        btn1 = types.KeyboardButton('Выбрать расу')
        markup.add(btn1)
        bot.send_message(message.from_user.id, f'Игра началась! Ваше имя: {user_names[user_id]}', reply_markup=markup)

    elif message.text == 'Выбрать расу':
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
        btn1 = types.KeyboardButton('Человек')
        btn2 = types.KeyboardButton('Эльф')
        btn3 = types.KeyboardButton('Гоблин')
        markup.add(btn1, btn2, btn3)
        
    elif message.text == 'Человек':
        bot.send_message(message.from_user.id, 'Отлично! Ваша раса: Человек', parse_mode='Markdown')
    elif message.text == 'Эльф':
        bot.send_message(message.from_user.id, 'Отлично! Ваша раса: Эльф', parse_mode='Markdown')
    elif message.text == 'Гоблин':
        bot.send_message(message.from_user.id, 'Отлично! Ваша раса: Гоблин', parse_mode='Markdown')

    elif message.text == 'Человек' or 'Эльф' or 'Гоблин':
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
        btn1 = types.KeyboardButton('2 часа')
        btn2 = types.KeyboardButton('6 часов')
        btn3 = types.KeyboardButton('12 часов')
        markup.add(btn1, btn2, btn3)
        bot.send_message(message.from_user.id, 'Выберите время отправки отчёта о вашем персонаже', reply_markup=markup)

    elif message.text == '2 часа' or '6 часов' or '12 часов':
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
        btn1 = types.KeyboardButton('ДА!')
        btn2 = types.KeyboardButton('Нет...')
        markup.add(btn1, btn2)
        bot.send_message(message.from_user.id, 'Отлично, время выбрано! Начинаем!', reply_markup=markup)

    elif message.text == 'Нет...':
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
        bot.send_message(message.from_user.id, 'Ну нет так нет, до встречи)', reply_markup=markup)
        
    elif message.text == 'ДА!':
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
        bot.send_message(message.from_user.id, 'Отлично, начинаем!', reply_markup=markup)
        
bot.polling(none_stop=True, interval=0) #чтобы бот работал бесконечно





