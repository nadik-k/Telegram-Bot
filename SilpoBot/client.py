from telebot import types
import db_handler

user_data = {}
titles = ["Ім'я", "Прізвище", "Дата народження(dd.mm.yyyy)", "Адреса", "Пошта"]
current_title_index = {}

def user(message, user_phone, bot):
    bot.send_message(message.chat.id, f"Вітаю, {message.contact.first_name}! :)", reply_markup=types.ReplyKeyboardRemove())
    bot.send_message(message.chat.id, f"Раді бачити Вас тут! Сподіваюсь, у нас Ви знайдете роботу своєї мрії!💖")
    markup = types.ReplyKeyboardMarkup(row_width=2, resize_keyboard=True)
    btn1 = types.KeyboardButton('Актуальні вакансії')
    btn2 = types.KeyboardButton('Моя анкета')
    markup.add(btn1, btn2)
    bot.send_message(message.chat.id, "Оберіть наступну команду зі списку:", reply_markup=markup)
    user_data[message.chat.username] = {'phone': user_phone}

def handle_profile(message, bot):
    phone_number = user_data.get(message.chat.username, {}).get('phone')
    if phone_number:
        profile = db_handler.fetch_profile(phone_number)
        if profile:
            profile_message = f"Ваш профіль:\n\n"
            profile_message += f"Ім'я: {profile['first_name']}\n"
            profile_message += f"Прізвище: {profile['last_name']}\n"
            profile_message += f"Дата народження: {profile['date']}\n"
            profile_message += f"Телефон: {profile['phone']}\n"
            profile_message += f"Адреса: {profile['address']}\n"
            profile_message += f"Пошта: {profile['email']}\n"
            bot.send_message(message.chat.id, profile_message)
        else:
            markup = types.ReplyKeyboardMarkup(row_width=2, resize_keyboard=True)
            itembtn1 = types.KeyboardButton('Створити')
            itembtn2 = types.KeyboardButton('Головне меню')
            markup.add(itembtn1, itembtn2)
            bot.send_message(message.chat.id, "Ваш профіль не знайдено.", reply_markup=markup)
    else:
        bot.send_message(message.chat.id, "Не вдалося знайти номер телефону для цього профілю.")

def handle_cprofile(message, bot):
    global current_title_index
    current_title_index[message.chat.id] = 0
    bot.send_message(message.chat.id, f"{titles[current_title_index[message.chat.id]]}:")
    bot.register_next_step_handler(message, handle_user_input)

def handle_user_input(message, bot):
    global current_title_index
    idx = current_title_index.get(message.chat.id, 0)
    if message.chat.username not in user_data:
        user_data[message.chat.username] = {}
    user_data[message.chat.username][titles[idx]] = message.text
    bot.send_message(message.chat.id, f"Ви ввели: {message.text}")
    idx += 1
    if idx < len(titles):
        current_title_index[message.chat.id] = idx
        bot.send_message(message.chat.id, f"{titles[idx]}:")
        bot.register_next_step_handler(message, handle_user_input)
    else:
        bot.send_message(message.chat.id, "Всі дані введено. Дякую!")
        phone_number = user_data[message.chat.username].get('phone')
        if phone_number:
            cursor = db_handler.conn.cursor()
            add_message = (
                "INSERT INTO `profiles` (`first_name`, `last_name`, `date`, `phone`, `address`, `email`) "
                "VALUES (%s, %s, %s, %s, %s, %s)"
            )
            data_message = (
                user_data[message.chat.username]["Ім'я"],
                user_data[message.chat.username]["Прізвище"],
                user_data[message.chat.username]["Дата народження(dd.mm.yyyy)"],
                phone_number,
                user_data[message.chat.username]["Адреса"],
                user_data[message.chat.username]["Пошта"]
            )
            cursor.execute(add_message, data_message)
            db_handler.conn.commit()
            cursor.close()
        current_title_index.pop(message.chat.id, None)
        user_data.pop(message.chat.username, None)

def handle_back(message, bot):
    markup = types.ReplyKeyboardMarkup(row_width=2, resize_keyboard=True)
    itembtn1 = types.KeyboardButton('Актуальні вакансії')
    itembtn2 = types.KeyboardButton('Моя анкета')
    markup.add(itembtn1, itembtn2)
    bot.send_message(message.chat.id, "Оберіть наступну команду зі списку:", reply_markup=markup)

def send_vacancies(message, bot):
    vacancies = db_handler.fetch_data()
    if vacancies:
        for vacancy in vacancies:
            name = vacancy['name']
            price = vacancy['price']
            employment = vacancy['employment']
            experience = vacancy['experience']
            requirements = vacancy['requirements']
            message_text = (
                f"📝 _Назва_: *{name}*\n\n"
                f"💰 _Зарплата_: *{price}*\n\n"
                f"🕒 _Зайнятість_: *{employment}*\n\n"
                f"📈 _Досвід_: *{experience}*\n\n"
                f"📋 _Обов'язки_: *{requirements}*"
            )
            reply_markup = types.InlineKeyboardMarkup()
            reply_markup.row(types.InlineKeyboardButton(text='Обрати', callback_data=f'select_{vacancy["id"]}'))
            bot.send_message(
                message.chat.id,
                text=message_text,
                parse_mode='Markdown',
                reply_markup=reply_markup
            )
    else:
        bot.send_message(message.chat.id, "Наразі немає доступних вакансій.")

def register_candidate(profile_id, job_id):
    cursor = db_handler.conn.cursor()
    add_candidate = "INSERT INTO candidates (profile_id, job_id) VALUES (%s, %s)"
    data_candidate = (profile_id, job_id)
    cursor.execute(add_candidate, data_candidate)
    db_handler.conn.commit()
    cursor.close()