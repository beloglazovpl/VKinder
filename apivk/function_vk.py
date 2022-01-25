import math
import requests
from config import token_user


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

    # определяем страну пользователя
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

    # определяем регион пользователя
    def get_region(self, country, region_user):
        region_url = self.url + 'database.getRegions'
        region_params = {
            'access_token': token_user,
            'country_id': country,
            'count': 1000,
        }
        res = requests.get(url=region_url, params={**self.params, **region_params}).json()
        region_list = res['response']['items']
        for region in region_list:
            if region['title'] == region_user:
                return region['id']

    # получаем список городов (в стране и регионе)
    def get_cities_list(self, country, region, offset):
        city_url = self.url + 'database.getCities'
        city_params = {
            'access_token': token_user,
            'country_id': country,
            'region_id': region,
            'need_all': 0,
            'count': 1000,
            'offset': 1000 * offset
        }
        res = requests.get(url=city_url, params={**self.params, **city_params}).json()
        return res


vkinder = ApiVK()


# определяем город пользователя
def get_city(country, region, user_city):
    offset = 0
    res = vkinder.get_cities_list(country, region, offset)
    count = res['response']['count']
    offset = math.ceil(count / 1000)
    for i in range(offset + 1):
        cities = vkinder.get_cities_list(country, region, i)['response']['items']
        for city in cities:
            if city['title'] == user_city:
                return city['id']
