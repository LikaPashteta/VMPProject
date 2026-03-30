import telebot
import sqlite3
import time
from apscheduler.schedulers.background import BackgroundScheduler

#Пока что все команды вписаны и почти никак друг с другом не работают, лишь сосуществуют в одном файле

bot = telebot.TeleBot('...')
from telebot import types

def init_db():
    conn = sqlite3.connect('game.db')
    cur = conn.cursor()
    cur.execute('''
        CREATE TABLE IF NOT EXISTS players (
            user_id INTEGER PRIMARY KEY,
            name Noname,
            level INTEGER DEFAULT 1,
            health INTEGER DEFAULT 100,
            max_health INTEGER DEFAULT 100,    
            energy INTEGER DEFAULT 100,
            location TEXT DEFAULT 'Спавн',
            last_energy_update REAL DEFAULT 0,
            last_health_update REAL DEFAULT 0
        )
    ''')
    conn.commit()
    conn.close()

init_db()

def get_player(user_id):
    conn = sqlite3.connect('game.db')
    cur = conn.cursor()
    cur.execute('SELECT * FROM players WHERE user_id = ?', (user_id,))
    row = cur.fetchone()
    conn.close()
    if row:
        return {
            'user_id': row[0],
            'name': row[1],
            'level': row[2],
            'health': row[3],
            'energy': row[4],
            'location': row[5],
            'last_energy_update': row[6],
            'last_health_update': row[7]
        }
    else:
        return None

def create_player(user_id, name):
    conn = sqlite3.connect('game.db')
    cur = conn.cursor()
    cur.execute('''
        INSERT INTO players (user_id, name, last_energy_update, last_health_update)
        VALUES (?, ?, ?, ?)
    ''', (user_id, name, time.time(), time.time()))
    conn.commit()
    conn.close()

def update_res(player):
    now = time.time()
    energy_regen_per_sec = 0.05 
    health_regen_per_sec = 0.01 

    energy_delta = now - player['last_energy_update']
    energy_gain = energy_delta * energy_regen_per_sec
    new_energy = min(100, player['energy'] + energy_gain)

    health_delta = now - player['last_health_update']
    health_gain = health_delta * health_regen_per_sec
    new_health = min(100, player['health'] + health_gain)
    
    conn = sqlite3.connect('game.db')
    cur = conn.cursor()
    cur.execute('''
        UPDATE players
        SET energy = ?, health = ?, last_energy_update = ?, last_health_update = ?
        WHERE user_id = ?
    ''', (new_energy, new_health, now, now, player['user_id']))
    conn.commit()
    conn.close()

    player['energy'] = new_energy
    player['health'] = new_health
    player['last_energy_update'] = now
    player['last_health_update'] = now
    return player

@bot.message_handler(commands=['start'])
def start(message):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    btn1 = types.KeyboardButton("Начать")
    markup.add(btn1)
    bot.send_message(message.from_user.id, "Скоро тут будет история, пока воть", reply_markup=markup)

@bot.message_handler(commands=['action'])
def action(message):
    user_id = message.from_user.id
    player = get_player(user_id)
    if not player:
        bot.send_message(message.chat.id, "Сначала зарегистрируйтесь через /start")
        return

    player = update_res(player)
    if player['energy'] < 10:
        bot.send_message(message.chat.id, "Недостаточно энергии. Подождите немного.")
        return

    new_energy = player['energy'] - 10
    conn = sqlite3.connect('game.db')
    cur = conn.cursor()
    cur.execute('UPDATE players SET energy = ? WHERE user_id = ?', (new_energy, user_id))
    conn.commit()
    conn.close()
    player['energy'] = new_energy

@bot.message_handler(commands=['status'])
def status(message):
    user_id = message.from_user.id
    player = get_player(user_id)
    if not player:
        bot.send_message(message.chat.id, "Сначала /start")
        return
    player = update_res(player)
    bot.send_message(message.chat.id,
                     f"{player['name']} (уровень {player['level']})\n"
                     f"Здоровье: {int(player['health'])}/100\n"
                     f"Энергия: {int(player['energy'])}/100\n"
                     f"Локация: {player['location']}")

scheduler = BackgroundScheduler()

def check_and_notify():
    pass

scheduler.add_job(check_and_notify, 'interval', seconds=30)
scheduler.start()

@bot.message_handler(commands=['cool'])
def cool(message):
    user_id = message.from_user.id
    player = get_player(user_id)
    if not player:
        bot.send_message(message.chat.id, "Сначала зарегистрируйтесь через /start")
        return

    player = update_res(player)

    if player['energy'] < 30:
        bot.send_message(message.chat.id, f"Недостаточно энергии! Нужно 30, у вас {int(player['energy'])}.")
        return

    new_energy = player['energy'] - 30
    new_max_health = player.get('max_health', 100) + 10
    current_health = player['health']
    conn = sqlite3.connect('game.db')
    cur = conn.cursor()
    cur.execute('''
        UPDATE players
        SET energy = 100, max_health = 110, health = 100, last_energy_update = ?
        WHERE user_id = ?
    ''', (new_energy, new_max_health, current_health, time.time(), user_id))
    conn.commit()
    conn.close()

    bot.send_message(message.chat.id,
                     f"Вы сделали крутость и у героя увеличилось максимальное хп!\n"
                     f"Максимальное здоровье увеличено до {new_max_health}.\n"
                     f"Энергия: {int(new_energy)} | Здоровье: {current_health}/{new_max_health}")

@bot.message_handler(commands=['dirt'])
def dirt(message):
    user_id = message.from_user.id
    player = get_player(user_id)
    if not player:
        bot.send_message(message.chat.id, "Сначала зарегистрируйтесь через /start")
        return

    player = update_res(player)

    if player['energy'] < 30:
        bot.send_message(message.chat.id, f"Недостаточно энергии! Нужно 30, у вас {int(player['energy'])}.")
        return
    
    new_energy = player['energy'] - 30
    new_health = max(0, player['health'] - 20)
    max_health = player.get('max_health', 100)
    conn = sqlite3.connect('game.db')
    cur = conn.cursor()
    cur.execute('''
        UPDATE players
        SET energy = ?, health = ?, last_energy_update = ?
        WHERE user_id = ?
    ''', (new_energy, new_health, time.time(), user_id))
    conn.commit()
    conn.close()
    bot.send_message(message.chat.id,
                     f"Вы сделали гадость герою и он потерял 20 здоровья!\n"
                     f"Энергия: {int(new_energy)} | Здоровье: {new_health}/{max_health}")

@bot.message_handler(content_types=['text'])
def get_text_messages(message):
    user_id = message.from_user.id 

    if message.text == 'Начать':
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True) 
        btn1 = types.KeyboardButton('Помощь')
        btn2 = types.KeyboardButton('Правила пользования')
        btn3 = types.KeyboardButton('Начать приключение')
        markup.add(btn1, btn2, btn3)
        bot.send_message(message.from_user.id, 'Задайте интересующий вопрос', reply_markup=markup)

    elif message.text == 'Помощь':
        bot.send_message(message.from_user.id, 'Здесь будет пара кнопок перехода в инфо канал', parse_mode='Markdown')

    elif message.text == 'Правила пользования':
        bot.send_message(message.from_user.id, 'Подробно вы можете ознакомиться с правилами ' + '[тут](https://telegra.ph/Pravila-polzovaniya-botom-03-09)', parse_mode='Markdown')

    elif message.text == 'Начать приключение':
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
        btn1 = types.KeyboardButton('Выбрать расу')
        markup.add(btn1)
        bot.send_message(message.from_user.id, f'Игра началась! Ваше имя: Noname', reply_markup=markup)

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
