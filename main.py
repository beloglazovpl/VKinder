from datetime import date
from vk_api.longpoll import VkEventType
from database.script_bd import check_users_vk, check_search_results, save_users_vk, save_search_results, metadata, engine
from botvk.keyboard_file import keyboard
from apivk.function_vk import vkinder
from botvk.function_botvk import write_msg, write_msg_keyboard, longpoll, send_photo


# поиск статуса отношений
def find_relation(user_id):
    res = vkinder.about_user(user_id)['response']
    for item in res:
        if 'relation' not in item:
            relation = None
        elif 'relation' in item:
            relation = item['relation']
        return relation


# поиск пола
def find_sex(user_id):
    res = vkinder.about_user(user_id)['response']
    for item in res:
        if 'sex' not in item:
            any_sex = None
        elif 'sex' in item:
            sex = item['sex']
            if sex == 2:
                any_sex = 1
            elif sex == 1:
                any_sex = 2
            else:
                any_sex = 0
        return any_sex


# поиск города
def find_city(user_id):
    res = vkinder.about_user(user_id)['response']
    for item in res:
        if 'city' not in item:
            city = None
        elif 'city' in item:
            city = item['city']['id']
        return city


# поиск возраста
def find_age(user_id):
    res = vkinder.about_user(user_id)['response']
    for item in res:
        if 'bdate' not in item:
            age = None
        elif 'bdate' in item:
            bdate = item['bdate']
            if len(bdate) >= 8:
                day, mon, year = bdate.split('.')
                day = int(day)
                mon = int(mon)
                year = int(year)
                today = date.today()
                age = today.year - year - ((today.month, today.day) < (mon, day))
            else:
                age = None
        return age


# отправить ссылку на человека и топ-3 фото
def choose_photo(age_from, age_to, relation, sex, city, search_user_id):
    try:
        search = vkinder.users_search(age_from, age_to, relation, sex, city)
        people_id = search['response']['items']
        for people in people_id:
            id_people = int(people['id'])
            first_name = people['first_name']
            last_name = people['last_name']
            status = people['is_closed']
            if status is False:
                if check_users_vk(id_people) is None:
                    save_users_vk(id_people, first_name, last_name)
                if check_search_results(search_user_id, id_people) is None:
                    save_search_results(search_user_id, id_people)
                    write_msg(event.user_id, f'Зацени {first_name} {last_name} https://vk.com/id{id_people}')
                    for i in vkinder.photo_user(id_people):
                        owner_id = i[1][2]
                        photo_id = i[1][3]
                        photo = f'photo{owner_id}_{photo_id}'
                        send_photo(event.user_id, photo)
                    write_msg(event.user_id, 'Для продолжения поиска повторно введите команду "поиск"')
                    break
    except TypeError:
        write_msg(event.user_id, 'Не хватает данных для поиска')


# проверка полноты информации о пользователе
def check(age, city, sex, relation):
    count = 0
    if age is not None:
        count += 1
    if city is not None:
        count += 1
    if sex is not None:
        count += 1
    if relation is not None:
        count += 1
    if count == 4:
        write_msg(event.user_id, 'Отлично! Для начала поиска введите команду "поиск"')

if __name__ == '__main__':
    metadata.create_all(engine)

    for event in longpoll.listen():
        if event.type == VkEventType.MESSAGE_NEW:

            if event.to_me:
                request = event.text

                if request == 'привет' or request == 'ПРИВЕТ' or request == 'Привет':
                    first_name = str([i['first_name'] for i in vkinder.about_user(event.user_id)['response']])[2:-2]
                    write_msg(event.user_id, f'Хай, {first_name}! Введите ID пользователя кому будем искать пару'
                                             f' (указав вначале символ "/")')

                elif '/' in request:
                    try:
                        search_user_id = int(request[1:])
                    except ValueError:
                        write_msg(event.user_id, 'Некорректно введен ID')
                    try:
                        age = find_age(search_user_id)
                        if age is None:
                            write_msg(event.user_id, 'Не удалось определить возраст пользователя. Уточните возраст '
                                                 '(указав вначале символ "?")')
                        city = find_city(search_user_id)
                        if city is None:
                            write_msg(event.user_id, 'Не удалось определить город пользователя. '
                                                     'Требуется уточнение в формате Страна|Город (Например: Россия|Хабаровск)')
                        sex = find_sex(search_user_id)
                        if sex is None:
                            write_msg(event.user_id, 'Не удалось определить пол пользователя. Требуется уточнение '
                                                     '(введите "м" или "ж")')
                        relation = find_relation(search_user_id)
                        if relation is None:
                            write_msg_keyboard(event.user_id, 'Не удалось определить статус отношений пользователя. '
                                                              'Выберите подходящий статус из выпадающей клавитуры.', keyboard)
                        check(age, city, sex, relation)
                    except NameError:
                        pass

                elif '?' in request:
                    try:
                        age = int(request[1:])
                        write_msg(event.user_id, 'Возраст уточнен')
                        try:
                            check(age, city, sex, relation)
                        except NameError:
                            write_msg(event.user_id, 'Не хватает первычных данных, введите ID пользователя')
                    except ValueError:
                        write_msg(event.user_id, 'Некорректно введен возраст')

                elif request == 'м':
                    sex = 1
                    write_msg(event.user_id, 'Пол уточнен')
                    try:
                        check(age, city, sex, relation)
                    except NameError:
                        write_msg(event.user_id, 'Не хватает первычных данных, введите ID пользователя')
                elif request == 'ж':
                    sex = 2
                    write_msg(event.user_id, 'Пол уточнен')
                    check(age, city, sex, relation)

                elif '+' in request:
                    relation = int(request[1:2])
                    write_msg(event.user_id, 'Статус отношений уточнен')
                    try:
                        check(age, city, sex, relation)
                    except NameError:
                        write_msg(event.user_id, 'Не хватает первычных данных, введите ID пользователя')

                elif '|' in request:
                    write_msg(event.user_id, 'Подождите... идет поиск по базе городов')
                    info = request.split('|')
                    country_, city_ = info[0], info[1]
                    contry_id = vkinder.get_country(country_)
                    city = vkinder.get_city(contry_id, city_)
                    if city is None:
                        write_msg(event.user_id, 'Город не найден, повторите запрос в формате Страна|Город')
                    else:
                        write_msg(event.user_id, 'Город уточнен')
                        try:
                            check(age, city, sex, relation)
                        except NameError:
                            write_msg(event.user_id, 'Не хватает первычных данных, введите ID пользователя')

                elif request == 'поиск':
                    try:
                        first_name = str([i['first_name'] for i in vkinder.about_user(search_user_id)['response']])[2:-2]
                        last_name = str([i['last_name'] for i in vkinder.about_user(search_user_id)['response']])[2:-2]
                        if check_users_vk(search_user_id) is None:
                            save_users_vk(search_user_id, first_name, last_name)
                        choose_photo(age - 2, age + 2, relation, sex, city, search_user_id)
                    except KeyError:
                        write_msg(event.user_id, 'Такого профиля в ВК нет, введите корректный ID')
                    except ValueError:
                        write_msg(event.user_id, 'Для поиска пары введите корректный ID состоящий из цифр')
                    except NameError:
                        write_msg(event.user_id, 'Для поиска пары введите корректный ID состоящий из цифр')

                elif request == 'помощь':
                    write_msg(event.user_id, '''
                    Список команд:
                    1. привет (приветсвенное сообщение)
                    2. / для ввода ID пользователя для которого ишем пару (Например: /1)
                    3. + для ввода статуса отношений (Например: +5 — все сложно)
                    4. для уточнения города вводите в формате Страна|Город (Например: Россия|Хабаровск)
                    5. ? для ввода возраста (Например: ?30)
                    6. поиск (осуществить поиск)
                    ''')

                else:
                    write_msg(event.user_id, 'Неизвестная команда. Для вызова справки введите "помощь"')
