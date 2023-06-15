import requests
import telebot
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont


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

def generate_pdf(company_info):
    pdf_file_path = "company_info.pdf"
    c = canvas.Canvas(pdf_file_path, pagesize=letter)

    # Настройки для текста
    text_x = 50
    text_y = 700
    line_height = 20
    pdfmetrics.registerFont(TTFont('Arial', 'arial.ttf'))
    # Записываем данные из company_info в PDF
    c.setFont("Arial", 12)
    lines = company_info.split("\n")
    for line in lines:
        c.drawString(text_x, text_y, line)
        text_y -= line_height

    c.save()
    return pdf_file_path


bot = telebot.TeleBot('6074017992:AAFOhnU5cQfKaGpzF7ZK32bZKqTB9BBf9_o')


@bot.message_handler(commands=['start'])
def send_welcome(message):
    bot.reply_to(message,
                 "Привет! Я бот, который может отправить справку о компании по ИНН. Просто отправь мне ИНН компании.")


@bot.message_handler(func=lambda message: True)
def send_company_info(message):
    INN = message.text
    company_info = get_api(INN)

    if company_info.startswith("Компания с таким ИНН не найдена"):
        bot.reply_to(message, company_info)
    else:
        pdf_file_path = generate_pdf(company_info)
        with open(pdf_file_path, 'rb') as f:
            bot.send_document(message.chat.id, f)

        # Удалите PDF-файл
        # os.remove(pdf_file_path)


bot.polling()