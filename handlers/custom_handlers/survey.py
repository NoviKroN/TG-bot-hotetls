from loader import bot
from states.contact_information import UserInfoState
from telebot.types import Message


def ask_for_next_info(message: Message, next_state: str, next_question: str) -> None:
    bot.set_state(message.from_user.id, next_state, message.chat.id)
    bot.send_message(message.from_user.id, next_question)


def save_info_and_ask_for_next(message: Message, next_state: str, next_question: str, info_key: str) -> None:
    with bot.retrieve_data(message.from_user.id, message.chat.id) as data:
        data[info_key] = message.text
    ask_for_next_info(message, next_state, next_question)


@bot.message_handler(commands=['survey'])
def survey(message: Message) -> None:
    ask_for_next_info(message, UserInfoState.name, 'Привет, введи свое имя')


@bot.message_handler(state=UserInfoState.name)
def get_name(message: Message) -> None:
    if message.text.isalpha():
        save_info_and_ask_for_next(message, UserInfoState.age, 'Спасибо, имя записал! Теперь введи свой возраст',
                                   'name')
    else:
        bot.send_message(message.from_user.id, 'Имя должно состоять только из букв!')


@bot.message_handler(state=UserInfoState.age)
def get_age(message: Message) -> None:
    if message.text.isdigit():
        save_info_and_ask_for_next(message, UserInfoState.country,
                                   'Спасибо, возраст записал! Теперь введи свою страну проживания', 'age')
    else:
        bot.send_message(message.from_user.id, 'Возраст должен состоять только из цифр!')


@bot.message_handler(state=UserInfoState.country)
def get_country(message: Message) -> None:
    if message.text.isalpha():
        save_info_and_ask_for_next(message, UserInfoState.city, 'Спасибо, страну записал! Теперь введи свой город',
                                   'country')


@bot.message_handler(state=UserInfoState.city)
def get_city(message: Message) -> None:
    with bot.retrieve_data(message.from_user.id, message.chat.id) as data:
        data['city'] = message.text
        text = f'Спасибо за предоставленную информацию. Ваши данные:\n' \
               f'Имя - {data["name"]}\nВозраст - {data["age"]}\nСтрана - {data["country"]}\n' \
               f'Город - {data["city"]}'
        bot.send_message(message.from_user.id, text)
