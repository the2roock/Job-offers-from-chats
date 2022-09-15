import pymysql
from config import Config



def db_connection():
    return pymysql.Connection(host=Config.database['host'], user=Config.database['user'], database=Config.database['name'], password=Config.database['password'])

def db_cursor():
    return db_connection().cursor()


def register_user(chat_id, username, first_name, last_name):
    with db_connection() as connection:
        with connection.cursor() as cursor:
            sql_query = f'SELECT id FROM user WHERE chat_id={chat_id}'
            if cursor.execute(sql_query):
                return True
            sql_query = f'INSERT INTO user(chat_id, username, first_name, last_name) VALUES("{chat_id}", "{username}", "{first_name}", "{last_name}")'
            cursor.execute(sql_query)
            connection.commit()
    return False


def set_status_on(user_id):
    with db_connection() as connection:
        with connection.cursor() as cursor:
            sql_query = f'update user set status=1 where id={user_id}'
            cursor.execute(sql_query)
            connection.commit()

def set_status_off(user_id):
    with db_connection() as connection:
        with connection.cursor() as cursor:
            sql_query = f'update user set status=0 where id={user_id}'
            cursor.execute(sql_query)
        connection.commit()


def get_keywords(user_id=None):
    with db_cursor() as cursor:
        if user_id is None:
            sql_query = 'select * from keyword where user_id in (select id from user where status=1)'
        else:
            sql_query = f'select * from keyword where user_id = {user_id}'
        if not cursor.execute(sql_query):
            return
        keywords = [{'id': element[2], 'user_id': element[3], 'title': element[0], 'title_lowercase': element[1]} for element in cursor.fetchall()]
        return keywords


def add_keyword(user_id, value):
    with db_connection() as connection:
        with connection.cursor() as cursor:
            sql_query = f'select exists(select * from keyword where title_lowercase=\'{value.lower()}\' and user_id={user_id})'
            cursor.execute(sql_query)
            if cursor.fetchone()[0] == 1:
                return
            sql_query = f'insert into keyword(user_id, title, title_lowercase) values ({user_id}, \'{value}\', \'{value.lower()}\')'
            cursor.execute(sql_query)
        connection.commit()


def remove_keyword(user_id, value):
    with db_connection() as connection:
        with connection.cursor() as cursor:
            sql_query = f'delete from keyword where user_id={user_id} and title_lowercase=\'{value.lower()}\''
            cursor.execute(sql_query)
        connection.commit()


def get_un_keywords(user_id=None):
    with db_cursor() as cursor:
        if user_id is None:
            sql_query = 'select * from unkeyword where user_id in (select id from user where status=1)'
        else:
            sql_query = f'select * from unkeyword where user_id = {user_id}'
        if not cursor.execute(sql_query):
            return
        keywords = [{'id': element[2], 'user_id': element[3], 'title': element[0], 'title_lowercase': element[1]} for element in cursor.fetchall()]
        return keywords


def add_un_keyword(user_id, value):
    with db_connection() as connection:
        with connection.cursor() as cursor:
            sql_query = f'select exists(select * from unkeyword where title_lowercase=\'{value.lower()}\' and user_id={user_id})'
            cursor.execute(sql_query)
            if cursor.fetchone()[0] == 1:
                return
            sql_query = f'insert into unkeyword(user_id, title, title_lowercase) values ({user_id}, \'{value}\', \'{value.lower()}\')'
            cursor.execute(sql_query)
        connection.commit()


def remove_un_keyword(user_id, value):
    with db_connection() as connection:
        with connection.cursor() as cursor:
            sql_query = f'delete from unkeyword where user_id={user_id} and title_lowercase=\'{value.lower()}\''
            cursor.execute(sql_query)
        connection.commit()


def add_filter(name, chat_id):
    with db_connection() as connection:
        with connection.cursor() as cursor:
            sql_query = f'select exists(select * from filter where name=\'{name}\' and user_id={get_user_id(chat_id)})'
            cursor.execute(sql_query)
            if cursor.fetchone()[0] == 1:
                return
            sql_query = f'insert into filter(name, user_id) values(\'{name}\', {get_user_id(chat_id)})'
            cursor.execute(sql_query)
        connection.commit()


def remove_filter(name, chat_id):
    with db_connection() as connection:
        with connection.cursor() as cursor:
            sql_query = f'select id from filter where name=\'{name}\' and user_id={get_user_id(chat_id)}'
            cursor.execute(sql_query)
            filter_id = cursor.fetchone()[0]
            sql_query = f'delete from filter where id={filter_id}'
            cursor.execute(sql_query)
            sql_query = f'delete from filter_keyword where filter_id={filter_id}'
            cursor.execute(sql_query)
        connection.commit()


def get_user_id(chat_id):
    with db_cursor() as cursor:
        sql_query = f'select id from user where chat_id={chat_id}'
        cursor.execute(sql_query)
        return cursor.fetchone()[0]


def get_chat_id(user_id):
    with db_cursor() as cursor:
        sql_query = f'select chat_id from user where id={user_id}'
        cursor.execute(sql_query)
        return cursor.fetchone()[0]


def get_all_filters():
    with db_cursor() as cursor:
        sql_query = f'select * from filter'
        cursor.execute(sql_query)
        filters = [{'id': element[2], 'user_id': element[0], 'name': element[1]} for element in cursor.fetchall()]
        for filter in filters:
            sql_query = f'select * from filter_keyword where filter_id={filter["id"]}'
            cursor.execute(sql_query)
            filter['keywords'] = [{'id': element[0], 'filter_id': element[1], 'title': element[2], 'title_lowercase': element[3]} for element in cursor.fetchall()]
        return filters


def get_chats():
    with db_cursor() as cursor:
        sql_query = 'select link from chat'
        cursor.execute(sql_query)
        return cursor.fetchall()


def add_chat(link):
    with db_connection() as connection:
        with connection.cursor() as cursor:
            sql_query = f'insert into chat(link) values(\'{link}\')'
            cursor.execute(sql_query)
            connection.commit()


def get_users():
    with db_cursor() as cursor:
        sql_query='select * from user where status=1'
        cursor.execute(sql_query)
        users = [{'id': element[4], 'chat_id': element[0], 'username':element[1], 'first_name':element[2], 'last_name':element[3]} for element in cursor.fetchall()]
        return users
