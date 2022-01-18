from sqlalchemy import create_engine, MetaData, Table, Integer, String, Column, ForeignKey


URL = 'postgresql://vkinder:beloglazov@localhost:5432/vkinder_base'
engine = create_engine(URL)
metadata = MetaData()
connection = engine.connect()

# таблица пользователей
users_vk = Table(
    'users_vk', metadata,
    Column('user_id', Integer(), primary_key=True),
    Column('user_first_name', String(100)),
    Column('user_last_name', String(100))
)

# таблица результата поиска
search_results = Table(
    'search_results', metadata,
    Column('id', Integer(), nullable=False, autoincrement=True, primary_key=True),
    Column('user_id_search', Integer(), ForeignKey('users_vk.user_id')),
    Column('user_id_found', Integer(), ForeignKey('users_vk.user_id'))
)

# поиск пользователя в таблице пользователей
def check_users_vk(user_id):
    search = users_vk.select()
    result = connection.execute(search)
    for row in result:
        if user_id == row[0]:
            return row


# поиск результата поиска в БД
def check_search_results(user_1, user_2):
    search = search_results.select()
    result = connection.execute(search)
    for row in result:
        if user_1 == row[1] and user_2 == row[2]:
            return row


# записывать данные в таблицу пользователей
def save_users_vk(user_id, user_first_name, user_last_name):
    insert = users_vk.insert().values(user_id=user_id, user_first_name=user_first_name, user_last_name=user_last_name)
    result = connection.execute(insert)
    return result


# записывать данные в таблицу результата поиска
def save_search_results(user_id_search, user_id_found):
    insert = search_results.insert().values(user_id_search=user_id_search, user_id_found=user_id_found)
    result = connection.execute(insert)
    return result
