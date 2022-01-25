from apivk.function_vk import vkinder
from datetime import date
from database.script_bd import check_users_vk, check_search_results, save_users_vk, save_search_results
from botvk.function_botvk import write_msg, send_photo


# определение статуса отношений
def find_relation(search_user_id):
    res = vkinder.about_user(search_user_id)['response']
    for item in res:
        if 'relation' not in item:
            relation = None
        elif 'relation' in item:
            relation = item['relation']
        return relation


# определение пола
def find_sex(search_user_id):
    res = vkinder.about_user(search_user_id)['response']
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


# определение города
def find_city(search_user_id):
    res = vkinder.about_user(search_user_id)['response']
    for item in res:
        if 'city' not in item:
            city = None
        elif 'city' in item:
            city = item['city']['id']
        return city


# определение возраста
def find_age(search_user_id):
    res = vkinder.about_user(search_user_id)['response']
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
def choose_photo(age_from, age_to, relation, sex, city, search_user_id, user_id):
    try:
        search = vkinder.users_search(age_from, age_to, relation, sex, city)
        people_id = search['response']['items']
        for people in people_id:
            try:
                id_people = int(people['id'])
                first_name = people['first_name']
                last_name = people['last_name']
                status = people['is_closed']
                city_ = people['city']['id']
            except KeyError:
                pass
            if status is False and city_ == city:
                if city_ == city:
                    if check_users_vk(id_people) is None:
                        save_users_vk(id_people, first_name, last_name)
                    if check_search_results(search_user_id, id_people) is None:
                        save_search_results(search_user_id, id_people)
                        write_msg(user_id, f'Зацени {first_name} {last_name} https://vk.com/id{id_people}')
                        for i in vkinder.photo_user(id_people):
                            owner_id = i[1][2]
                            photo_id = i[1][3]
                            photo = f'photo{owner_id}_{photo_id}'
                            send_photo(user_id, photo)
                        write_msg(user_id, 'Для продолжения поиска повторно введите команду "поиск"')
                        break
    except TypeError:
        write_msg(user_id, 'Не хватает данных для поиска')


# проверка полноты информации о пользователе
def check(age, city, sex, relation, user_id):
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
        write_msg(user_id, 'Отлично! Для начала поиска введите команду "поиск"')
