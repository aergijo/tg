import telebot
from telebot import types
import sqlalchemy as db
from sqlalchemy.orm import declarative_base, sessionmaker

API_TOKEN = '7664412881:AAE3xS26zNgpN4fUHyzunomuj-zqarTkkvA'  # Замените на токен вашего бота
bot = telebot.TeleBot(API_TOKEN)

# Создаем базовый класс для моделей
Base = declarative_base()

# Определяем модель для таблицы films
class Film(Base):
    __tablename__ = 'films'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, nullable=False)

# Список фильмов
movies = []
adminLIST = ["Добавить фильм", "Удалить фильм"]
time = ["Понедельник 14:00", "Вторник 18:00", "Среда 15:00", "Четверг 16:00", "Пятница 17:00", "Суббота 20:00"]
admins = [1885787868, 895319273]
user_states = {}

# Обработчик команды /start
@bot.message_handler(commands=['start'])
def start(message):
    # Создаем inline-клавиатуру
    keyboard = types.InlineKeyboardMarkup()
    engine = db.create_engine("mysql+pymysql://is61-1:pf2j8m8c@192.168.3.111/sigma_boy")
    conn = engine.connect()
    query = db.text("SELECT * FROM films")
    films = conn.execute(query).fetchall()
    
    # Добавляем фильмы в список
    for film in films:
        film_name = film.name
        movies.append(film_name)
    
    for movie in movies:
        # Добавляем кнопку для каждого фильма
        button = types.InlineKeyboardButton(text=movie, callback_data=movie)
        keyboard.add(button)
    
    bot.send_message(message.chat.id, "Выберите фильм:", reply_markup=keyboard)

@bot.message_handler(commands=['admin'])
def admin(message):
    if message.chat.id in admins:
        keyboard = types.InlineKeyboardMarkup()
        for buttonADM in adminLIST:
            button = types.InlineKeyboardButton(text=buttonADM, callback_data=buttonADM)
            keyboard.add(button)
        bot.send_message(message.chat.id, "Привет, вы попали в меню администратора:", reply_markup=keyboard)
    else:
        bot.send_message(message.chat.id, "Вам сюда нельзя!")

@bot.message_handler(func=lambda message: True)
def echo_all(message):
    if message.chat.id in user_states and user_states[message.chat.id] == "waiting_for_movie":
        movie_title = message.text
        
        # Подключаемся к базе данных
        engine = db.create_engine("mysql+pymysql://is61-1:pf2j8m8c@192.168.3.111/sigma_boy")
        Session = sessionmaker(bind=engine)
        session = Session()
        
        # Создаем новый экземпляр фильма
        new_film = Film(name=movie_title)
        session.add(new_film)
        session.commit()
        session.close()
        
        bot.send_message(message.chat.id, f"Фильм '{movie_title}' добавлен!")
        
        # Удаляем состояние пользователя
        del user_states[message.chat.id]
        

# Обработчик нажатий на кнопки
@bot.callback_query_handler(func=lambda call: True)
def handle_query(call):
    if call.data in movies:
        selected_movie = call.data  # Получаем название выбранного фильма
        bot.answer_callback_query(call.id)  # Убираем "крутилку" у кнопки
        bot.send_message(call.message.chat.id, f"Вы выбрали: {selected_movie}. ")
        TimeChoose(call.message.chat.id)
    if call.data in time:
        selected_time = call.data  # Получаем название выбранного фильма
        bot.answer_callback_query(call.id)  # Убираем "крутилку" у кнопки
        bot.send_message(call.message.chat.id, f"Вы забронировали место на сеанс фильма: {selected_time}. Хорошего просмотра!")
    if call.data in adminLIST:
        selected_button = call.data 
        bot.answer_callback_query(call.id)
        AdminChoose(call.message.chat.id, selected_button)

def AdminChoose(id, button):
    if button == "Добавить фильм":
        bot.send_message(id, "Напишите название фильма:")
        user_states[id] = 'waiting_for_movie'  
    if button == "Удалить фильм":
        bot.send_message(id, "Напишите название фильма:")
        user_states[id] = 'remove_for_movie'  

def TimeChoose(chat_id):
    keyboard = types.InlineKeyboardMarkup()
    for timen in time:
        # Добавляем кнопку для каждого времени
        button = types.InlineKeyboardButton(text=timen, callback_data=timen)
        keyboard.add(button)
    
    bot.send_message(chat_id, "Выберите время:", reply_markup=keyboard)

# Запуск бота
if __name__ == '__main__':
    bot.polling(none_stop=True)