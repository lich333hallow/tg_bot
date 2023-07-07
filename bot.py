from time import sleep
import telebot
from mailing import SendEmailToFor, bot
from utils import utils, save, load
from delete import delete_files
from threading import Thread


def photos(mess: telebot.types.Message) -> None:
    utils["photo"].append(mess.photo)
    utils["add"] += f"{mess.caption if mess.caption is not None else utils['mel']}" + \
                    "\n" if mess.caption is not None else utils['mel']


def documents(mess: telebot.types.Message) -> None:
    utils["document"].append(mess.document)
    utils["add"] += f"{mess.caption if mess.caption is not None else utils['mel']}" + \
                    "\n" if mess.caption is not None else utils['mel']


def videos(mess: telebot.types.Message) -> None:
    utils["videos"].append(mess.video)
    utils["add"] += f"{mess.caption if mess.caption is not None else utils['mel']}" + \
                    "\n" if mess.caption is not None else utils["mel"]


def check(mess: telebot.types.Message):
    if mess.document:
        documents(mess)
    elif mess.photo:
        photos(mess)
    elif mess.video:
        videos(mess)


@bot.message_handler(commands=["start"])
def start(mess: telebot.types.Message):
    if mess.chat.id not in utils["receiver"].keys() and mess.chat.type == "private":
        s = bot.send_message(mess.chat.id, "Перед использованием бота, введите почту")
        bot.register_next_step_handler(s, reg)


def reg(mess: telebot.types.Message):
    try:
        if "@" in mess.text:
            utils["receiver"][mess.chat.id] = mess.text
            save()
    except TypeError as err:
        print(err)


@bot.message_handler(content_types=["text", "photo", "document", "video"])
def sending(mess: telebot.types.Message):
    load()
    if mess.chat.id in utils["receiver"].keys() and mess.chat.type == "private":
        if not utils["db"]:
            utils["db"] = True
            utils["add"] += f"{mess.text if mess.text is not None else utils['mel']}" + \
                            "\n" if mess.text is not None else utils['mel']
            check(mess=mess)
            work(mess=mess)
        else:
            check(mess=mess)
            utils["add"] += f"{mess.text if mess.text is not None else utils['mel']}" + \
                            "\n" if mess.text is not None else utils['mel']
        sleep(1)
    elif mess.chat.type == "private":
        bot.send_message(mess.chat.id, "Введите команду /start для настройки бота!")


def work(mess: telebot.types.Message):
    print("work start")
    sleep(10)
    SendEmailToFor(photos=utils["photo"], documents=utils["document"], videos=utils["videos"],
                   adds=utils["add"], receiver=utils["receiver"][mess.chat.id]).parse(mess=mess)
    utils["db"], utils["add"], utils["document"], utils["photo"] = False, "", [], []
    print("work end")
    bot.send_message(mess.chat.id, "Сообщение отправлено (файлы будут удалены через 7 дней)")
    pr = Thread(target=delete_files())
    pr.start()


print("Bot is ready!")
while True:
    try:
        bot.polling(none_stop=True)
    except Exception as e:
        print(e)
        sleep(15)
