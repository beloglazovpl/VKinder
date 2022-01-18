import json


def get_but(text):
    return {
        "action": {
            "type": "text",
            "payload": "{\"button\": \"" + "1" + "\"}",
            "label": f"{text}"
        },
        "color": 'positive'
    }


keyboard = {
    "one_time": True,
    "buttons": [
        [get_but('1 — не женат (не замужем)'), get_but('2 — встречается')],
        [get_but('3 — помолвлен(-а)'), get_but('4 — женат (замужем)')],
        [get_but('5 — всё сложно'), get_but('6 — в активном поиске')],
        [get_but('7 — влюблен(-а)'), get_but('8 — в гражданском браке')]
    ]
}
keyboard = json.dumps(keyboard, ensure_ascii=False).encode('utf-8')
keyboard = str(keyboard.decode('utf-8'))
