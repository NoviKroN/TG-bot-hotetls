import sqlite3
from telebot.types import Message
from loguru import logger
from config_data import config


def create_table(connection: sqlite3.Connection, create_table_sql: str) -> None:
    """
    Создает таблицу в базе данных SQLite.
    :param connection: объект соединения SQLite
    :param create_table_sql: SQL-запрос для создания таблицы
    :return: None
    """
    try:
        cursor = connection.cursor()
        cursor.execute(create_table_sql)
    except sqlite3.Error as e:
        logger.error(f"Ошибка при создании таблицы: {e}")


def add_user(message: Message) -> None:
    """
    Создает базу данных, если она еще не существует, и таблицу с данными пользователей.
    Добавляет данные в эту таблицу, если бота запускает новый пользователь.
    :param message: объект сообщения Telegram
    :return: None
    """
    create_table_sql = """CREATE TABLE IF NOT EXISTS user(
        id INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL, 
        chat_id INTEGER UNIQUE,
        username STRING,
        full_name TEXT
    );"""

    with sqlite3.connect(config.DB_NAME) as connection:
        create_table(connection, create_table_sql)
        cursor = connection.cursor()
        try:
            cursor.execute(
                "INSERT INTO user (chat_id, username, full_name) VALUES (?, ?, ?)", (
                    message.chat.id,
                    message.from_user.username,
                    message.from_user.full_name
                )
            )
            logger.info(f'Добавлен новый пользователь. User_id: {message.chat.id}')
        except sqlite3.IntegrityError:
            logger.info(f'Данный пользователь уже существует. User_id: {message.chat.id}')


def add_query(query_data: dict) -> None:
    """
    Создает таблицу, если она еще не создавалась, и добавляет в нее данные, которые ввел пользователь для поиска.
    :param query_data: словарь с данными запроса
    :return: None
    """
    create_table_sql = """CREATE TABLE IF NOT EXISTS query(
        id INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,
        user_id INTEGER,
        date_time STRING, 
        input_city STRING,
        destination_id STRING,
        photo_need STRING,
        response_id INTEGER,
        FOREIGN KEY (response_id) REFERENCES response(id) ON DELETE CASCADE ON UPDATE CASCADE
    );"""

    with sqlite3.connect(config.DB_NAME) as connection:
        create_table(connection, create_table_sql)
        cursor = connection.cursor()
        try:
            cursor.execute(
                "INSERT INTO query(user_id, input_city, photo_need, destination_id, date_time) VALUES (?, ?, ?, ?, ?)",
                (
                    query_data['chat_id'],
                    query_data['input_city'],
                    query_data['photo_need'],
                    query_data['destination_id'],
                    query_data['date_time']
                )
            )
            logger.info(f'В БД добавлен новый запрос. User_id: {query_data["chat_id"]}')

            cursor.execute(f"""
                    DELETE FROM query WHERE query.[date_time]=
                    (SELECT MIN([date_time]) FROM query WHERE `user_id` = '{query_data["chat_id"]}' )
                    AND
                    ((SELECT COUNT(*) FROM query WHERE `user_id` = '{query_data["chat_id"]}' ) > 5 ) 
                """
                           )
        except sqlite3.IntegrityError:
            logger.info(f'Запрос с такой датой и временем уже существует. User_id: {query_data["chat_id"]}')


def add_response(search_result: dict) -> None:
    """
    Создает таблицу, если она еще не создавалась, и добавляет в нее данные, которые бот получил в результате запросов к серверу.
    :param search_result: словарь с результатами поиска
    :return: None
    """
    create_table_sql = """CREATE TABLE IF NOT EXISTS response(
            id INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL, 
            query_id INTEGER,
            hotel_id STRING,
            name STRING,
            address STRING, 
            price REAL,
            distance REAL,
            FOREIGN KEY (hotel_id) REFERENCES images(hotel_id) ON DELETE CASCADE ON UPDATE CASCADE
        );"""

    with sqlite3.connect(config.DB_NAME) as connection:
        create_table(connection, create_table_sql)
        cursor = connection.cursor()
        for item in search_result.items():
            cursor.execute(f"SELECT `id` FROM query WHERE `date_time` = ?", (item[1]['date_time'],))
            query_id = cursor.fetchone()[0]
            cursor.execute(
                "INSERT INTO response(query_id, hotel_id, name, address, price, distance) VALUES (?, ?, ?, ?, ?, ?)",
                (
                    query_id,
                    item[0],
                    item[1]['name'],
                    item[1]['address'],
                    item[1]['price'],
                    item[1]['distance']
                )
            )
            logger.info(f'В БД добавлены данные отеля. User_id: {item[1]["user_id"]}')
            for link in item[1]['images']:
                cursor.execute("""CREATE TABLE IF NOT EXISTS images(
                id INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,
                hotel_id INTEGER REFERENCES response (id),
                link TEXT     
                );""")
                cursor.execute("INSERT INTO images (hotel_id, link) VALUES (?, ?)", (item[0], link))
            logger.info(f'В БД добавлены ссылки на фотографии отеля. User_id: {item[1]["user_id"]}')
