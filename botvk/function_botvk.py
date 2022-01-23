import vk_api
from vk_api.longpoll import VkLongPoll
from random import randrange
from config import token


vk = vk_api.VkApi(token=token)
longpoll = VkLongPoll(vk)


# написать сообщение
def write_msg(user_id, message):
    vk.method('messages.send', {'user_id': user_id, 'message': message, 'random_id': randrange(10 ** 7)})


# написать сообщение с вызовом клавиатуры
def write_msg_keyboard(user_id, message, keyboard):
    vk.method('messages.send', {'user_id': user_id, 'message': message, 'random_id': randrange(10 ** 7), 'keyboard': keyboard})


# отправить фото
def send_photo(user_id, attachment):
    vk.method('messages.send', {'user_id': user_id, 'random_id': randrange(10 ** 7), 'attachment': attachment})
