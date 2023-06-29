import telebot
from mailing import SendEmailToFor, bot
from time import sleep
from utils import utils


def photos(mess: telebot.types.Message) -> None:
    utils["photo"].append(mess.photo)
    utils["add"] += f"{mess.caption if mess.caption is not None else utils['mel']}" + \
                    "\n" if mess.caption is not None else utils['mel']


def documents(mess: telebot.types.Message) -> None:
    utils["document"].append(mess.document)
    utils["add"] += f"{mess.caption if mess.caption is not None else utils['mel']}" + \
                    "\n" if mess.caption is not None else utils['mel']


@bot.message_handler(commands=["start"])
def start(mess: telebot.types.Message):
    if not utils["receiver"]:
        s = bot.send_message(mess.chat.id, "Перед использованием бота, введите почту")
        bot.register_next_step_handler(s, reg)


def reg(mess):
    try:
        if "@" in mess.text:
            utils["receiver"] = mess.text
    except TypeError as err:
        print(err)


@bot.message_handler(content_types=["text", "photo", "document"])
def sending(mess: telebot.types.Message):
    if utils["receiver"]:
        if not utils["db"]:
            utils["db"] = True
            utils["add"] += f"{mess.text if mess.text is not None else utils['mel']}" + \
                            "\n" if mess.text is not None else utils['mel']
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
            utils["add"] += f"{mess.text if mess.text is not None else utils['mel']}" + \
                            "\n" if mess.text is not None else utils['mel']
        sleep(1)


def das(mess: telebot.types.Message):
    print("das works")
    sleep(10)
    SendEmailToFor(photos=utils["photo"], documents=utils["document"],
                   adds=utils["add"], receiver=utils["receiver"]).parse(mess=mess)
    print("das ended works")
    utils["db"], utils["add"], utils["document"], utils["photo"] = False, "", [], []


bot.polling(none_stop=True)
