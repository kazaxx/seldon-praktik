import telebot
import requests
import re
from requests.cookies import RequestsCookieJar
import base64

bot_token = "6062411217:AAGTS69Lfg1mbjL3QPNMeC5_Mly6ehR2EyE"
bot = telebot.TeleBot(bot_token)

@bot.message_handler(commands=['start'])
def start_command(message):
    bot.send_message(message.chat.id, 'Привет, я бот для получения информации о компании по ИНН.')



@bot.message_handler(regexp=r'^\d{10,12}|\d{14,15}$')
def handle_inn(message):
    inn = re.sub(r'\s+', '', message.text)
    bot.send_message(message.chat.id, 'Поиск компании по ИНН...')
    bot.send_message(message.chat.id, check_inn(inn, message.chat.id))


def check_inn(inn, chat_id):
    session_guid = None
    login_myseldon = None
    login_payload = {
        'UserName': 'test00590736@test.ru',
        'Password': 'YeVgM61u'
    }

    login_url = 'https://basis.myseldon.com/api/rest/login'
    order_url = f'https://basis.myseldon.com/api/rest/order_excerpt_pdf?inn={inn}'

    client = requests.Session()
    login_response = client.post(login_url, data=login_payload)

    if login_response.status_code == 200:
        cookies = login_response.cookies
        session_guid = cookies.get('SessionGuid')
        login_myseldon = cookies.get('LoginMyseldon')

    if session_guid and login_myseldon:
        headers = {
            'SessionGuid': session_guid,
            'LoginMyseldon': login_myseldon
        }
        order_response = client.get(order_url, headers=headers)
        order_data = order_response.json()

        if 'status' in order_data and order_data['status']['methodStatus'] == 'Error':
            return f"Компания с таким ИНН не найдена. {order_data['status']['name']}"
        else:
            return get_api_pdf(inn, order_data, client, headers, chat_id)
    else:
        return "Ошибка входа в API."

def get_api_pdf(inn, order_data, client, headers, chat_id):
    file_name = "company.pdf"

    order_num = order_data['orderNum']

    while True:
        res = client.get(f'https://basis.myseldon.com/api/rest/get_excerpt_pdf?orderNum={order_num}', headers=headers)
        res_data = res.json()

        if 'excerpt_body' in res_data and res_data['excerpt_body'] is not None:
            break

        print("retry")

    file_name = "company.pdf"
    with open(file_name, 'wb') as file:
        file.write(base64.decodebytes(res_data['excerpt_body'].encode()))

    send_file(file_name, chat_id)

    return "Готово!"

def send_file(file_name, chat_id):
    with open(file_name, 'rb') as file:
        bot.send_document(chat_id, file)

@bot.message_handler(func=lambda message: True)
def handle_other(message):
    bot.send_message(message.chat.id, 'ИНН указан неверно.')


bot.polling()

