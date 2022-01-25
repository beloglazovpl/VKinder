from vk_api.longpoll import VkEventType
from database.script_bd import check_users_vk, save_users_vk, metadata, engine
from botvk.keyboard_file import keyboard
from apivk.function_vk import vkinder, get_city
from botvk.function_botvk import write_msg, write_msg_keyboard, longpoll
from function_find.func import find_relation, find_age, find_sex, find_city, check, choose_photo


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
                    if len(vkinder.about_user(search_user_id)['response']) == 1:
                        try:
                            age = find_age(search_user_id)
                            if age is None:
                                write_msg(event.user_id, 'Не удалось определить возраст пользователя! '
                                                         'Уточните возраст указав вначале символ "?" '
                                                         '(например: ?30')
                            city = find_city(search_user_id)
                            if city is None:
                                write_msg(event.user_id, 'Не удалось определить город пользователя! '
                                                         'Требуется уточнение в формате "Страна|Регион|Город" '
                                                         '(например: Россия|Хабаровский край|Хабаровск) .'
                                                         'Если город федерального значения, то введите в формате '
                                                         '"Страна|Город" (например: Россия|Москва),')
                            sex = find_sex(search_user_id)
                            if sex is None:
                                write_msg(event.user_id, 'Не удалось определить пол пользователя! Требуется уточнение. '
                                                         'Введите "М" если пользователь парень, "Ж" если девушка.')
                            relation = find_relation(search_user_id)
                            if relation is None:
                                write_msg_keyboard(event.user_id, 'Не удалось определить статус отношений пользователя! '
                                                                  'Выберите подходящий статус из выпадающей клавитуры.', keyboard)
                            check(age, city, sex, relation, event.user_id)
                        except NameError:
                            pass
                    else:
                        write_msg(event.user_id, f'Пользователя с ID {search_user_id} не существует')

                elif '?' in request:
                    try:
                        age = int(request[1:])
                        if 13 < age < 120:
                            write_msg(event.user_id, 'Возраст уточнен')
                            try:
                                check(age, city, sex, relation, event.user_id)
                            except NameError:
                                write_msg(event.user_id, 'Не хватает первычных данных, введите ID пользователя')
                        else:
                            write_msg(event.user_id, 'Недопустимый возраст')
                    except ValueError:
                        write_msg(event.user_id, 'Некорректно введен возраст')

                elif request == 'м' or request == 'ж':
                    if request == 'м':
                        sex = 1
                    if request == 'ж':
                        sex = 2
                    write_msg(event.user_id, 'Пол уточнен')
                    try:
                        check(age, city, sex, relation, event.user_id)
                    except NameError:
                        write_msg(event.user_id, 'Не хватает первычных данных, введите ID пользователя')

                elif '+' in request:
                    relation = int(request[1:2])
                    write_msg(event.user_id, 'Статус отношений уточнен')
                    try:
                        check(age, city, sex, relation, event.user_id)
                    except NameError:
                        write_msg(event.user_id, 'Не хватает первычных данных, введите ID пользователя')

                elif '|' in request:
                    info = request.split('|')
                    try:
                        country_, region_, city_ = info[0], info[1], info[2]
                        contry_id = vkinder.get_country(country_)
                        if contry_id is not None:
                            region_id = vkinder.get_region(contry_id, region_)
                            if region_id is not None:
                                city = get_city(contry_id, region_id, city_)
                            else:
                                write_msg(event.user_id, f'Регион {region_} не найден(а)')
                                city = None
                        else:
                            write_msg(event.user_id, f'Страна {country_} не найдена(а)')
                            city = None
                    except IndexError:
                        country_, city_ = info[0], info[1]
                        contry_id = vkinder.get_country(country_)
                        if contry_id is not None:
                            region_id = None
                            city = get_city(contry_id, region_id, city_)
                        else:
                            write_msg(event.user_id, f'Страна {country_} не найдена')
                    if city is None:
                        write_msg(event.user_id, 'Город пользователя не определен, повторите ввод')
                    elif city is not None:
                        write_msg(event.user_id, 'Город уточнен')
                        try:
                            check(age, city, sex, relation, event.user_id)
                        except NameError:
                            write_msg(event.user_id, 'Не хватает первычных данных, введите ID пользователя')

                elif request == 'поиск':
                    try:
                        first_name = str([i['first_name'] for i in vkinder.about_user(search_user_id)['response']])[2:-2]
                        last_name = str([i['last_name'] for i in vkinder.about_user(search_user_id)['response']])[2:-2]
                        if check_users_vk(search_user_id) is None:
                            save_users_vk(search_user_id, first_name, last_name)
                        choose_photo(age - 2, age + 2, relation, sex, city, search_user_id, event.user_id)
                    except KeyError:
                        write_msg(event.user_id, 'Такого профиля в ВК нет, введите корректный ID')
                    except ValueError:
                        write_msg(event.user_id, 'Для поиска пары введите корректный ID состоящий из цифр')
                    except NameError:
                        write_msg(event.user_id, 'Для поиска пары введите корректный ID состоящий из цифр')

                elif request == 'помощь':
                    write_msg(event.user_id, '''
                    Список команд:
                    1. "привет" (приветсвенное сообщение)
                    2. "/" для ввода ID пользователя для которого ишем пару (Например: /1)
                    3. "?" для ввода возраста (Например: ?30)
                    4. для уточнения статуса отношений выберите подходящий статус из выпадающей клавитуры
                    5. для уточнения города вводите в формате "Страна|Регион|Город"
                    (Например: Россия|Хабаровский край|Хабаровск)
                    6. "поиск" (осуществить поиск)
                    ''')

                else:
                    write_msg(event.user_id, 'Неизвестная команда. Для вызова справки введите "помощь"')
