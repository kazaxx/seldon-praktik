import requests
import json
import telebot
from io import BytesIO
from reportlab.pdfgen import canvas
from reportlab.pdfbase import pdfmetrics
from reportlab.lib.pagesizes import letter
import os

def generate_pdf(company):
    buffer = BytesIO()
    p = canvas.Canvas(buffer, pagesize=letter)

    # Загрузка шрифта
    font_path = "DejaVuSans.ttf"
    pdfmetrics.registerFont(pdfmetrics.Font("DejaVuSans", font_path))

    p.setFont("DejaVuSans", 12)
    p.drawString(100, 700, '[Информация о компании]')

    full_name = company['basic']['fullName']
    short_name = company['basic']['shortName']
    ogrn = company['basic']['ogrn']
    inn = company['basic']['inn']
    phone = company['phoneFormattedList'][0]['number']
    address = company['address']

    p.drawString(100, 650, f"Полное название: {full_name}")
    p.drawString(100, 625, f"Краткое название: {short_name}")
    p.drawString(100, 600, f"ОГРН: {ogrn}")
    p.drawString(100, 575, f"ИНН: {inn}")
    p.drawString(100, 550, f"Телефон: {phone}")
    p.drawString(100, 525, f"Адрес: {address}")

    p.showPage()
    p.save()

    return buffer

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

    company = json_data["companies_list"][0]
    return company


bot = telebot.TeleBot('6062411217:AAGTS69Lfg1mbjL3QPNMeC5_Mly6ehR2EyE')


def send_welcome(message):
    bot.reply_to(message,
                 f"Привет, <b>{message.from_user.first_name}</b>! Я бот, который может отправить справку о компании по ИНН. Просто отправь мне ИНН компании.",
                 parse_mode="HTML")


@bot.message_handler(func=lambda message: True)
def send_company_info(message):
    INN = message.text
    company_info = get_api(INN)

    if isinstance(company_info, str):
        bot.reply_to(message, company_info)
    else:
        pdf_buffer = generate_pdf(company_info)
        pdf_buffer.seek(0)

        # Сохраняем PDF-файл в виде временного файла
        with open("company_info.pdf", "wb") as file:
            file.write(pdf_buffer.getvalue())

        # Отправляем сохраненный файл
        with open("company_info.pdf", "rb") as file:
            bot.send_document(message.chat.id, file, caption="Информация о компании")

        # Удаляем временный файл
        os.remove("company_info.pdf")

bot.polling()
