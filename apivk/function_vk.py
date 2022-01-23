import math
import requests
from config import token_user, token


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

    # получаем список стран
    def get_country(self, country_user):
        country_url = self.url + 'database.getCountries'
        country_params = {
            'access_token': token_user,
            'need_all': 1,
            'count': 300
        }
        res = requests.get(url=country_url, params={**self.params, **country_params}).json()
        countries_list = res['response']['items']
        for country in countries_list:
            if country['title'] == country_user:
                return country['id']

    # получаем список городов
    def get_cities_list(self, country, offset):
        city_url = self.url + 'database.getCities'
        city_params = {
            'access_token': token_user,
            'country_id': country,
            'need_all': 1,
            'count': 1000,
            'offset': offset*1000
        }
        res = requests.get(url=city_url, params={**self.params, **city_params}).json()
        return res

    # поиск id города введенного пользователем
    def get_city(self, country, user_city):
        offset = 0
        res = vkinder.get_cities_list(country, offset)
        count = res['response']['count']
        offset = math.ceil(count / 1000)
        for i in range(offset + 1):
            cities = vkinder.get_cities_list(country, i)['response']['items']
            for city in cities:
                if city['title'] == user_city:
                    return city['id']


vkinder = ApiVK()
