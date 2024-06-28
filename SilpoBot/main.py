import telebot
from telebot import types
import moderator
import config
import db_handler
import client
bot = telebot.TeleBot(config.TOKEN)
vacancies = db_handler.fetch_data()

@bot.message_handler(commands=['start'])
def start(message):
    keyboard = types.ReplyKeyboardMarkup(row_width=1, resize_keyboard=True)
    button_phone = types.KeyboardButton(text="Надіслати телефон", request_contact=True)
    keyboard.add(button_phone)
    bot.send_message(message.chat.id, 'Будь ласка, надішліть Ваш номер телефону.', reply_markup=keyboard)

@bot.message_handler(content_types=['contact'])
def contact(message):
    if message.contact is not None:
        user_phone = '+' + message.contact.phone_number
        if user_phone == '+380972289375':
            moderator.admin(message, bot)
        else:
            client.user(message, user_phone, bot)

@bot.message_handler(func=lambda message: True)
def handle_all_messages(message):
    if message.text == 'Моя анкета':
        client.handle_profile(message, bot)
    elif message.text == 'Головне меню':
        client.handle_back(message, bot)
    elif message.text == 'Актуальні вакансії':
        client.send_vacancies(message, bot)
    elif message.text == 'Створити':
        client.handle_cprofile(message, bot)
    elif message.text == 'Переглянути кандидатів':
        moderator.look_candidates(message, bot)
    elif message.text == 'Редагувати вакансії':
        moderator.edit_vacancies(message, bot)
    elif message.text == 'Створити вакансію':
        moderator.handle_cvacancy(message, bot)
    elif message.text == 'Назад':
        moderator.back(message, bot)
    else:
        bot.send_message(message.chat.id, "Не розумію вашого повідомлення.")


@bot.callback_query_handler(func=lambda call: call.data.startswith('select_'))
def handle_select_callback(call):
    job_id = call.data.split('_')[1]
    user_phone = client.user_data.get(call.message.chat.username)['phone']
    print(user_phone)
    if user_phone:
        profile = db_handler.fetch_profile(user_phone)
        if profile:
            profile_id = profile['id']
            client.register_candidate(profile_id, job_id)
            bot.send_message(call.message.chat.id, "Менеджер згодом зв'яжеться з Вами!")
        else:
            bot.send_message(call.message.chat.id, "Ваш профіль не знайдено.")
    else:
        bot.send_message(call.message.chat.id, "Не вдалося знайти номер телефону для цього профілю.")

@bot.callback_query_handler(func=lambda call: call.data.startswith('delete_'))
def handle_delete_callback(call):
    profile_id = call.data.split('_')[1]
    db_handler.del_candidate(profile_id)
    bot.answer_callback_query(call.id, "Профіль видалено")
    bot.delete_message(call.message.chat.id, call.message.message_id)

@bot.callback_query_handler(func=lambda call: call.data.startswith('edit_'))
def handle_edit_callback(call):
    vacancy_id = call.data.split('_')[1]
    message = call.message
    moderator.edit_vac(vacancy_id, bot, message)

@bot.callback_query_handler(func=lambda call: call.data.startswith('deleteV_'))
def handle_delete_vacancy(call):
    vacancy_id = call.data.split('_')[1]
    print(vacancy_id)
    db_handler.del_vacancy(vacancy_id)
    bot.delete_message(call.message.chat.id, call.message.message_id)

bot.polling()

