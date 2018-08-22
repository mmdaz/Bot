"""
This is simple telegram bot and is my personal practice project to learn bot and network development .
"""

from time import sleep
import requests

# The token of the bot :
url = "https://api.telegram.org/bot699267489:AAFNulySbda5Ik9FKtHzLGpaUzwOim6Ut3k/"

"""
Send request to telegram and get updates by getUpdate method .

"""
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

def get_firstname(update):
    first_name = update['message']['form']['first_name']
    return first_name

def main():

    update_id = last_update(get_updates_json(url))['update_id']

    while True:

        if  get_user_name(last_update(get_updates_json(url))) == 'mhmd_azhdari' and int(update_id) == int(last_update(get_updates_json(url))['update_id']):
            send_mess(get_chat_id(last_update(get_updates_json(url))), 'hello muhammad')
            print("salam")
            update_id = str(int(update_id) + 1)
        elif int(update_id) == int(last_update(get_updates_json(url))['update_id']):
            send_mess(get_chat_id(last_update(get_updates_json(url))), 'Hello' + get_firstname(last_update(get_updates_json(url))) )
            print("salam")
            update_id = str(int(update_id) + 1)
        sleep(1)

if __name__ == '__main__':
    main()