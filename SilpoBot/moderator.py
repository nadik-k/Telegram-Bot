from telebot import types
import db_handler

titles_vac = ["Назва", "Зарплата", "Зайнятість", "Досвід", "Обов'язки"]
user_data = {}
titles = ["Ім'я", "Прізвище", "Дата народження(dd.mm.yyyy)", "Адреса", "Пошта"]

def admin(message, bot):
    bot.send_message(message.chat.id, f"Вітаю, {message.contact.first_name}! :)", reply_markup=types.ReplyKeyboardRemove())
    markup = types.ReplyKeyboardMarkup(row_width=2, resize_keyboard=True)
    btn1 = types.KeyboardButton('Переглянути кандидатів')
    btn2 = types.KeyboardButton('Редагувати вакансії')
    markup.add(btn1, btn2)
    bot.send_message(message.chat.id, "Оберіть наступну команду зі списку:", reply_markup=markup)

def look_candidates(message, bot):
    candidates = db_handler.read_candidates()
    if candidates:
        profiles_jobs = {}
        for candidate in candidates:
            profile_id = candidate['profile_id']
            job_id = candidate['job_id']
            if profile_id not in profiles_jobs:
                profiles_jobs[profile_id] = []
            profiles_jobs[profile_id].append(db_handler.read_vacancy(job_id)['name'])

        for profile_id, job_ids in profiles_jobs.items():
            jobs_text = ', '.join(map(str, job_ids))
            profile = db_handler.read_profile(profile_id)
            message_text = (f"Профіль\n"
                            f"Ім'я: {profile['first_name']}\n"
                            f"Прізвище: {profile['last_name']}\n"
                            f"Дата народження: {profile['date']}\n"
                            f"Телефон: {profile['phone']}\n"
                            f"Адреса: {profile['address']}\n"
                            f"Пошта: {profile['email']}\n\n"
                            f"Вакансії: {jobs_text}")
            bot.send_message(message.chat.id, message_text, reply_markup=get_delete_markup(profile_id))
    else:
        bot.send_message(message.chat.id, "Кандидатів не знайдено.")

def get_delete_markup(profile_id):
    markup = types.InlineKeyboardMarkup()
    delete_button = types.InlineKeyboardButton(text="Видалити", callback_data=f"delete_{profile_id}")
    markup.add(delete_button)
    return markup

def edit_vacancies(message, bot):
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
            reply_markup.row(types.InlineKeyboardButton(text='Редагувати', callback_data=f'edit_{vacancy["id"]}'))
            reply_markup.row(types.InlineKeyboardButton(text='Видалити', callback_data=f'deleteV_{vacancy["id"]}'))
            keyboard = types.ReplyKeyboardMarkup(row_width=1, resize_keyboard=True)
            button1 = types.KeyboardButton(text="Створити вакансію")
            button2 = types.KeyboardButton(text="Назад")
            keyboard.add(button1, button2)
            bot.send_message(
                message.chat.id,
                text=message_text,
                parse_mode='Markdown',
                reply_markup=reply_markup
            )
    else:
        bot.send_message(message.chat.id, "Наразі немає вакансій.")
    bot.send_message(message.chat.id, "Або створіть нову.", reply_markup=keyboard)

def edit_vac(vacancy_id, bot, message):
    markup = types.ReplyKeyboardMarkup(row_width=2, resize_keyboard=True)
    btn1 = types.KeyboardButton('Назва')
    btn2 = types.KeyboardButton('Зарплата')
    btn3 = types.KeyboardButton('Зайнятість')
    btn4 = types.KeyboardButton('Досвід')
    btn5 = types.KeyboardButton("Обов'язки")
    btn6 = types.KeyboardButton("Назад")
    markup.add(btn1, btn2, btn3, btn4, btn5, btn6)
    msg = bot.send_message(message.chat.id, "Оберіть що змінити:", reply_markup=markup)
    bot.register_next_step_handler(msg, process_edit_choice, vacancy_id, bot)

def process_edit_choice(message, vacancy_id, bot):
    if message.text == 'Назва':
        msg = bot.send_message(message.chat.id, "Введіть нову назву:")
        bot.register_next_step_handler(msg, edit_name, vacancy_id, bot)
    elif message.text == 'Зарплата':
        msg = bot.send_message(message.chat.id, "Введіть нову зарплату:")
        bot.register_next_step_handler(msg, edit_price, vacancy_id, bot)
    elif message.text == 'Зайнятість':
        msg = bot.send_message(message.chat.id, "Введіть нову зайнятість:")
        bot.register_next_step_handler(msg, edit_employment, vacancy_id, bot)
    elif message.text == 'Досвід':
        msg = bot.send_message(message.chat.id, "Введіть новий досвід:")
        bot.register_next_step_handler(msg, edit_experience, vacancy_id, bot)
    elif message.text == "Обов'язки":
        msg = bot.send_message(message.chat.id, "Введіть нові обов'язки:")
        bot.register_next_step_handler(msg, edit_responsibilities, vacancy_id, bot)
    elif message.text == "Назад":
        edit_vacancies(message, bot)
    else:
        bot.send_message(message.chat.id, "Невірний вибір. Спробуйте ще раз.")
        edit_vac(vacancy_id, message)

def edit_name(message, vacancy_id, bot):
    try:
        db_handler.edit_vacancy(vacancy_id, "name", message.text)
        bot.send_message(message.chat.id, "Назву змінено.")
        edit_vacancies(message, bot)
    except Exception as e:
        print(f"Error editing vacancy: {e}")
        bot.send_message(message.chat.id, "Сталася помилка при зміні назви.")

def edit_price(message, vacancy_id, bot):
    try:
        db_handler.edit_vacancy(vacancy_id, "price", message.text)
        bot.send_message(message.chat.id, "Зарплату змінено.")
        edit_vacancies(message, bot)
    except Exception as e:
        print(f"Error editing vacancy: {e}")
        bot.send_message(message.chat.id, "Сталася помилка при зміні зарплати.")

def edit_employment(message, vacancy_id, bot):
    try:
        db_handler.edit_vacancy(vacancy_id, "employment", message.text)
        bot.send_message(message.chat.id, "Зайнятість змінено.")
        edit_vacancies(message, bot)
    except Exception as e:
        print(f"Error editing vacancy: {e}")
        bot.send_message(message.chat.id, "Сталася помилка при зміні зайнятості.")

def edit_experience(message, vacancy_id, bot):
    try:
        db_handler.edit_vacancy(vacancy_id, "experience", message.text)
        bot.send_message(message.chat.id, "Досвід змінено.")
        edit_vacancies(message, bot)
    except Exception as e:
        print(f"Error editing vacancy: {e}")
        bot.send_message(message.chat.id, "Сталася помилка при зміні досвіду.")

def edit_responsibilities(message, vacancy_id, bot):
    try:
        db_handler.edit_vacancy(vacancy_id, "requirements", message.text)
        bot.send_message(message.chat.id, "Обов'язки змінено.")
        edit_vacancies(message, bot)
    except Exception as e:
        print(f"Error editing vacancy: {e}")
        bot.send_message(message.chat.id, "Сталася помилка при зміні обов'язків.")
def handle_cvacancy(message, bot):
    global current_title_index
    current_title_index[message.chat.id] = 0
    bot.send_message(message.chat.id, f"{titles_vac[current_title_index[message.chat.id]]}:")
    bot.register_next_step_handler(message, handle_vacancy_input, bot)


def handle_vacancy_input(message, bot):
    global current_title_index
    idx = current_title_index.get(message.chat.id, 0)
    if message.chat.username not in user_data:
        user_data[message.chat.username] = {}
    user_data[message.chat.username][titles_vac[idx]] = message.text
    bot.send_message(message.chat.id, f"Ви ввели: {message.text}")
    idx += 1
    if idx < len(titles):
        current_title_index[message.chat.id] = idx
        bot.send_message(message.chat.id, f"{titles_vac[idx]}:")
        bot.register_next_step_handler(message, handle_vacancy_input, bot)
    else:
        bot.send_message(message.chat.id, "Всі дані введено. Дякую!")
        cursor = db_handler.conn.cursor()
        add_message = (
            "INSERT INTO `vacancies` (`name`, `price`, `employment`, `experience`, `requirements`) "
            "VALUES (%s, %s, %s, %s, %s)"
        )
        data_message = (
            user_data[message.chat.username]["Назва"],
            user_data[message.chat.username]["Зарплата"],
            user_data[message.chat.username]["Зайнятість"],
            user_data[message.chat.username]["Досвід"],
            user_data[message.chat.username]["Обов'язки"]
        )
        cursor.execute(add_message, data_message)
        db_handler.conn.commit()
        cursor.close()
        current_title_index.pop(message.chat.id, None)
        user_data.pop(message.chat.username, None)
        edit_vacancies(message, bot)

def back(message, bot):
    markup = types.ReplyKeyboardMarkup(row_width=2, resize_keyboard=True)
    btn1 = types.KeyboardButton('Переглянути кандидатів')
    btn2 = types.KeyboardButton('Редагувати вакансії')
    markup.add(btn1, btn2)
    bot.send_message(message.chat.id, "Оберіть наступну команду зі списку:", reply_markup=markup)