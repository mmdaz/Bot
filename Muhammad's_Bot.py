from time import sleep

import requests

url = "https://api.telegram.org/bot699267489:AAFNulySbda5Ik9FKtHzLGpaUzwOim6Ut3k/"

def get_updates_json(request):
    response = requests.get(request + 'getUpdates')
    return response.json()

def last_update(data):
    results = data['result']
    total_updates = len(results) - 1
    return results[total_updates]

print(last_update(get_updates_json(url)))

def get_chat_id(update):
    chat_id = update['message']['chat']['id']
    return chat_id

def send_mess(chat, text):
    params = {'chat_id': chat, 'text': text}
    response = requests.post(url + 'sendMessage', data=params)
    return response

def get_user_name(update):
    user_specifications = update['message']['from']['username']
    return user_specifications


def main():

    update_id = last_update(get_updates_json(url))['update_id']

    while True:

        print(update_id)
        print(last_update(get_updates_json(url))['update_id'])
        print(get_user_name(last_update(get_updates_json(url))))
        if get_user_name(last_update(get_updates_json(url))) == 'mhmd_azhdari' and update_id == last_update(get_updates_json(url))['update_id']:
            send_mess(get_chat_id(last_update(get_updates_json(url))), 'hello muhammad')
            print("salam")
            update_id = str(int(update_id) + 1)
        elif get_user_name(last_update(get_updates_json(url))) == 'Maryamsf19' and update_id == last_update(get_updates_json(url))['update_id']:
            send_mess(get_chat_id(last_update(get_updates_json(url))), 'Developer of this bot loves you')
            update_id = str(int(update_id) + 1)
        elif update_id == last_update(get_updates_json(url))['update_id']:
            send_mess(get_chat_id(last_update(get_updates_json(url))), 'Hello')
            update_id = str(int(update_id) + 1)

        sleep(3)

if __name__ == '__main__':
    main()