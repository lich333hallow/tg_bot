import telebot
from settings import settings
from mailing import SendEmailToFor, bot
from time import sleep


smtp_server = "smtp.mail.ru"
receiver = "maksimka.prokhorov.03@mail.ru"
sender_email = settings["LOGIN"]
add = ""
db = False
mel = ""
photo = []
document = []


def photos(mess: telebot.types.Message):
    global photo, add
    photo.append(mess.photo)
    add += f"{mess.caption if mess.caption is not None else mel}" + "\n" if mess.caption is not None else mel


def documents(mess: telebot.types.Message):
    global document, add
    document.append(mess.document)
    add += f"{mess.caption if mess.caption is not None else mel}" + "\n" if mess.caption is not None else mel


@bot.message_handler(commands=["start"])
def start(mess: telebot.types.Message):
    pass


@bot.message_handler(content_types=["text", "photo", "document"])
def sending(mess: telebot.types.Message):
    global db, add
    if not db:
        db = True
        add += f"{mess.text if mess.text is not None else mel}" + "\n" if mess.text is not None else mel
        if mess.document:
            documents(mess)
        elif mess.photo:
            photos(mess)
        das(mess=mess)
    elif mess.photo:
        photos(mess)
    elif mess.document:
        documents(mess)
    else:
        add += f"{mess.text if mess.text is not None else mel}" + "\n" if mess.text is not None else mel
    sleep(1)


def das(mess: telebot.types.Message):
    global db, add, photo, document
    print("das works")
    print(photo, document)
    sleep(10)
    SendEmailToFor(photos=photo, documents=document, adds=add).parse(mess=mess)
    print("das ended works")
    db = False
    add = ""
    photo = []
    document = []


bot.polling(none_stop=True)