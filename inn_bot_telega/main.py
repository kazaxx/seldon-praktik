import requests
import json
import telebot

def get_api(INN):
    client = requests.session()
    login_url = "https://basis.myseldon.com/api/rest/login"
    api_url = f"https://basis.myseldon.com/api/rest/find_company?Inn={INN}"
    logout_url = "https://basis.myseldon.com/api/rest/logout"

    login_data = {
        "UserName": "test00590736@test.ru",
        "Password": "YeVgM61u"
    }

    response = client.post(login_url, data=login_data)

    session_guid = None
    login_myseldon = None
    if "Set-Cookie" in response.headers:
        cookies = response.headers["Set-Cookie"].split(", ")
        for cookie in cookies:
            if cookie.startswith("SessionGuid"):
                session_guid = cookie.split("=")[1]
            elif cookie.startswith("LoginMyseldon"):
                login_myseldon = cookie.split("=")[1]

    headers = {}
    if session_guid:
        headers["SessionGuid"] = session_guid
    if login_myseldon:
        headers["LoginMyseldon"] = login_myseldon

    response = client.get(api_url, headers=headers)
    json_data = response.json()

    if json_data["status"]["itemsFound"] == 0:
        return "Компания с таким ИНН не найдена"

    msg = ""
    company = json_data["companies_list"][0]

    msg += "Коды \n \n"
    msg += f"   ОГРН - {company['basic']['ogrn']} \n"
    msg += f"   ИНН - {company['basic']['ogrn']} \n"
    msg += "Наименовение  \n"
    msg += f"   Полное - {company['basic']['fullName']} \n"
    msg += f"   Сокращенное - {company['basic']['shortName']}\n"
    msg += f"Тел - {company['phoneFormattedList'][0]['number']}\n"
    msg += f"Адрес - {company['address']}\n"

    print(msg)
    return msg


bot = telebot.TeleBot('6074017992:AAFOhnU5cQfKaGpzF7ZK32bZKqTB9BBf9_o')

@bot.message_handler(commands=['start'])
def send_welcome(message):
    bot.reply_to(message, "Привет! Я бот, который может отправить справку о компании по ИНН. Просто отправь мне ИНН компании.")

@bot.message_handler(func=lambda message: True)
def send_company_info(message):
    INN = message.text
    company_info = get_api(INN)
    bot.reply_to(message, company_info)

bot.polling()
