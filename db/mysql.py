import pymysql


def get_connection():
    return pymysql.connect(
        host="localhost",
        user="root",
        password="",
        database="chatbot_ppu",
        charset="utf8mb4",
        cursorclass=pymysql.cursors.DictCursor
    )
