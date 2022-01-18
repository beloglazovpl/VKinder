from random import randrange
import requests, vk_api, time
from vk_api.longpoll import VkLongPoll, VkEventType
from config import token_user
from datetime import date
from script_bd import save_search_results, save_users_vk, metadata, engine, check_search_results, check_users_vk

token = 'c772478adf7bfa28d36de7f2f90e1121999e2ca4726a8bac91b21a41005cbe26141aff6915bedcc1459a1'


vk = vk_api.VkApi(token=token)
longpoll = VkLongPoll(vk)


class ApiVK:
    url = 'https://api.vk.com/method/'

    def __init__(self):
        self.params = {
            'v': '5.131'
        }

    # получаем информацию о пользователе
    def about_user(self, user_id):
        info_url = self.url + 'users.get'
        info_params = {
            'access_token': token_user,
            'user_id': user_id,
            'fields': 'bdate, city, sex, relation'
        }
        res = requests.get(url=info_url, params={**self.params, **info_params}).json()
        return res

    # получаем информацию о пользователе которого ищем по заданым параметрам
    def users_search(self, age_from, age_to, relation, sex, city):
        search_url = self.url + 'users.search'
        search_params = {
            'access_token': token_user,
            'fields': 'sex, relation, bdate, city',
            'age_from': age_from,
            'age_to': age_to,
            'status': relation,
            'sex': sex,
            'city': city,
            'count': 1000
        }
        res = requests.get(url=search_url, params={**self.params, **search_params}).json()
        return res

    # получаем фото пользователя
    def photo_user(self, user_id):
        photo_user_url = self.url + 'photos.get'
        photo_params = {
            'access_token': token_user,
            'extended': 1,
            'photo_sizes': 1,
            'album_id': 'profile',
            'owner_id': user_id
        }
        res = requests.get(url=photo_user_url, params={**self.params, **photo_params}).json()
        all_photo = {}
        for item in res['response']['items']:
            likes = item['likes']['count']
            photo = item['sizes'][-1]['url']
            comments = item['comments']['count']
            owner_id = item['owner_id']
            photo_id = item['id']
            all_photo[photo] = [likes, comments, owner_id, photo_id]
        all_photo_list = []
        for i in sorted(all_photo.items(), key=lambda para: (para[1][0], para[1][1])):
            all_photo_list.append(i)
        if len(all_photo_list) > 3:
            top_photo = all_photo_list[-3:]
            return top_photo
        else:
            return all_photo_list

    # читаем сообщение от пользователя(не используется)
    def read_msg(self, user_id):
        read_msg_url = self.url + 'messages.getHistory'
        read_msg_params = {
            'access_token': token,
            'user_id': user_id,
            'offset': 0,
            'count': 1
        }
        res = requests.get(url=read_msg_url, params={**self.params, **read_msg_params}).json()
        items = res['response']['items']
        for item in items:
            return item['text']

# прочитать сообщение от пользователя(не используется)
def read_msg(user_id):
    vk.method('messages.getConversations', {'peer_ids': user_id, 'offset': 0, 'filter': 'unanswered'})

# написать сообщение
def write_msg(user_id, message):
    vk.method('messages.send', {'user_id': user_id, 'message': message, 'random_id': randrange(10 ** 7)})

# написать сообщение с вызовом клавиатуры (не используется)
def write_msg_keyboard(user_id, message, keyboard):
    vk.method('messages.send', {'user_id': user_id, 'message': message, 'random_id': randrange(10 ** 7), 'keyboard': keyboard})

# отправить фото
def send_photo(user_id, attachment):
    vk.method('messages.send', {'user_id': user_id, 'random_id': randrange(10 ** 7), 'attachment': attachment})

# поиск статуса отношений
def find_relation(user_id):
    res = vkinder.about_user(user_id)['response']
    for item in res:
        if 'relation' not in item:
            relation = 0
        elif 'relation' in item:
            relation = item['relation']
        return relation

# поиск пола
def find_sex(user_id):
    res = vkinder.about_user(user_id)['response']
    for item in res:
        if 'sex' not in item:
            any_sex = None
            while any_sex is None:
                write_msg(event.user_id, 'Укажите пол пользователя: М/Ж')
                time.sleep(5)
                if request == 'М':
                    any_sex = 1
                elif request == 'Ж':
                    any_sex = 2
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
            while city is None:
                write_msg(event.user_id, 'Укажите город пользователя')
                time.sleep(5)
                city = int(request)
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
        if age is None:
            while age is None:
                write_msg(event.user_id, 'Введите возраст пользователя')
                time.sleep(5)
                age = int(request)
        age_from = age - 2
        age_to = age + 2
        age_list = [age_from, age_to]
        return age_list

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
            if check_users_vk(id_people) is None:
                save_users_vk(id_people, first_name, last_name)
            if check_search_results(search_user_id, id_people) is None:
                save_search_results(search_user_id, id_people)
                write_msg(event.user_id, f'Зацени {first_name} {last_name} https://vk.com/id{id_people}')
                if status is True:
                    write_msg(event.user_id, 'Профиль закрыт')
                    write_msg(event.user_id, 'Для продолжения поиска введите ID')
                    break
                elif status is False:
                    for i in vkinder.photo_user(id_people):
                        owner_id = i[1][2]
                        photo_id = i[1][3]
                        photo = f'photo{owner_id}_{photo_id}'
                        send_photo(event.user_id, photo)
                    write_msg(event.user_id, 'Для продолжения поиска введите ID')
                    break
    except TypeError:
        write_msg(event.user_id, 'Не хватает данных для поиска')


if __name__ == '__main__':
    metadata.create_all(engine)
    vkinder = ApiVK()

    for event in longpoll.listen():
        if event.type == VkEventType.MESSAGE_NEW:

            if event.to_me:
                request = event.text.lower()

                if request == 'привет':
                    first_name = str([i['first_name'] for i in vkinder.about_user(event.user_id)['response']])[2:-2]
                    write_msg(event.user_id, f'Хай, {first_name}! Введите ID кому будем искать пару')

                elif request == 'пока':
                    write_msg(event.user_id, 'Пока((')

                else:
                    try:
                        search_user_id = int(request)
                        first_name = str([i['first_name'] for i in vkinder.about_user(search_user_id)['response']])[2:-2]
                        last_name = str([i['last_name'] for i in vkinder.about_user(search_user_id)['response']])[2:-2]
                        if check_users_vk(search_user_id) is None:
                            save_users_vk(search_user_id, first_name, last_name)
                        age = find_age(search_user_id)
                        relation = find_relation(search_user_id)
                        sex = find_sex(search_user_id)
                        city = find_city(search_user_id)
                        choose_photo(age[0], age[1], relation, sex, city, search_user_id)
                    except KeyError:
                        write_msg(event.user_id, 'Такого профиля в ВК нет, введите корректный ID')
                    except ValueError:
                        write_msg(event.user_id, 'Для поиска пары введите корректный ID состоящий из цифр')
