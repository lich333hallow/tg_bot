from smtplib import SMTP
from ssl import create_default_context
from settings import settings
from email.mime.application import MIMEApplication
from email import encoders
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from telebot.types import Message, PhotoSize, Document
from typing import Union
from telebot import TeleBot
from os import remove

bot = TeleBot(settings["TOKEN"])


def write_file(src: str, data: bytes) -> None:
    with open(src, "wb+") as file:
        file.write(data)
    file.close()


class SendEmailToFor:
    def __init__(self, photos: list, documents: list, adds: str) -> None:
        self.photos = photos
        self.documents = documents
        self.adds = adds
        self.sender = settings["LOGIN"]
        self.receiver = "maksimka.prokhorov.03@mail.ru"
        self.server = "smtp.mail.ru"
        self.msg = MIMEMultipart()
        self.msg["To"] = self.receiver
        self.msg["From"] = self.sender

    def enter_to_send(self) -> bool:
        server = SMTP(self.server, port=587)
        server.ehlo()
        try:
            context = create_default_context()
            server.starttls(context=context)
            server.ehlo()
            server.login(settings["LOGIN"], settings["PASSWORD"])
            server.sendmail(self.sender, self.receiver, self.msg.as_string())
        except Exception as err:
            print(err)
            return False
        finally:
            server.quit()
            return True

    def coding_and_attach(self, type: str, obj: Union[PhotoSize, Document], mime: str = None):
        if type == "photo":
            file_info = bot.get_file(obj[len(obj) - 1].file_id)
            downloaded_file = bot.download_file(file_info.file_path)
            src = "./files/" + obj[1].file_id + ".jpg"
            write_file(src=src, data=downloaded_file)
            part = MIMEApplication(
                open(src, "rb").read(),
                ".jpg",
                # ./files/name.jpg
                Name=src[len("./files/"):]
            )
            encoders.encode_base64(part)
            self.msg.attach(part)
            remove(src)
        elif type == "document":
            file_info = bot.get_file(obj.file_id)
            downloaded_file = bot.download_file(file_info.file_path)
            src = "./files/" + obj.file_name
            write_file(src=src, data=downloaded_file)
            part = MIMEApplication(
                open(src, "rb").read(),
                mime,
                Name=src[len("./files/"):]
            )
            encoders.encode_base64(part)
            self.msg.attach(part)
            remove(src)

    def fors(self, mess: Message, forwarded: bool) -> None:
        if self.photos and self.documents:
            for ph in self.photos:
                self.coding_and_attach(type="photo", obj=ph)
            for doc in self.documents:
                self.coding_and_attach(type="document", obj=doc)
        elif self.documents:
            for doc in self.documents:
                self.coding_and_attach(type="document", obj=doc)
        elif self.photos:
            for ph in self.photos:
                self.coding_and_attach(type="photo", obj=ph)
        elif not self.photos and not self.documents:
            if forwarded:
                message = f"{self.adds}\n--------------\nОт: {mess.forward_from.first_name if mess.forward_from.first_name is not None else mess.forward_from.username}"
                text = MIMEText(message, "plain")
                self.msg.attach(text)
            else:
                message = f"{self.adds}\n-------\nОт: {mess.from_user.first_name if mess.from_user.first_name is not None else mess.from_user.username}"
                text = MIMEText(message, "plain")
                self.msg.attach(text)
        self.enter_to_send()

    def parse(self, mess: Message):
        if mess.forward_from:
            self.fors(mess=mess, forwarded=True)
        else:
            self.fors(mess=mess, forwarded=False)