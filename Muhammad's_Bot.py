import requests

url = "https://api.telegram.org/bot699267489:AAFNulySbda5Ik9FKtHzLGpaUzwOim6Ut3k/"

def get_updates_json(request):
    response = requests.get(request + 'getUpdates')
    # print(response.json())
    # print("salam")
    return response.json()

def last_update(data):
    results = data['result']
    total_updates = len(results) - 1
    return results[total_updates]

# get_updates_json(url)

def get_chat_id(update):
    chat_id = update['message']['chat']['id']
    return chat_id

def send_mess(chat, text):
    params = {'chat_id': chat, 'text': text}
    response = requests.post(url + 'sendMessage', data=params)
    return response

chat_id = get_chat_id(last_update(get_updates_json(url)))

send_mess(chat_id, 'salam')