from smtplib import SMTP
from ssl import create_default_context
from settings import settings
from email import encoders
from email.mime.application import MIMEApplication
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from telebot.types import Message, PhotoSize, Document
from typing import Union
from telebot import TeleBot

bot = TeleBot(settings["TOKEN"])


def coding_and_attach(type: str, obj: Union[PhotoSize, Document], mime: str = None) -> MIMEApplication:
    if type == "photo":
        file_info = bot.get_file(obj[len(obj) - 1].file_id)
        downloaded_file = bot.download_file(file_info.file_path)
        part = MIMEApplication(
            downloaded_file,
            file_info.file_path[-3:],
            Name=file_info.file_path[len("photos/"):]
        )
        encoders.encode_base64(part)
        return part
    elif type == "document":
        file_info = bot.get_file(obj.file_id)
        downloaded_file = bot.download_file(file_info.file_path)
        part = MIMEApplication(
            downloaded_file,
            obj.mime_type,
            Name=obj.file_name
        )
        encoders.encode_base64(part)
        return part


def check(forwarded: bool, adds: str, mess: Message) -> MIMEText:
    if forwarded:
        message = f"{adds}\n--------------\nОт: " \
                  f"{mess.forward_from.first_name if mess.forward_from.first_name is not None else mess.forward_from.username}"
        text = MIMEText(message, "plain")
        return text
    else:
        message = f"{adds}\n-------\nОт: " \
                  f"{mess.from_user.first_name if mess.from_user.first_name is not None else mess.from_user.username}"
        text = MIMEText(message, "plain")
        return text


class MailSender:
    def __init__(self, msg: MIMEMultipart, receiver: str) -> None:
        self.sender = settings["LOGIN"]
        self.server = settings["SERVER"]
        self.msg = msg
        self.receiver = receiver

    def enter_to_send(self) -> None:
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
        finally:
            server.quit()


class SendEmailToFor:
    def __init__(self, photos: list, documents: list, adds: str, receiver: str) -> None:
        self.photos = photos
        self.documents = documents
        self.adds = adds
        self.receiver = receiver
        self.msg = MIMEMultipart()

    def fors(self, mess: Message, forwarded: bool) -> None:
        if self.photos or self.documents:
            for ph in self.photos:
                self.msg.attach(coding_and_attach(type="photo", obj=ph))
            for doc in self.documents:
                self.msg.attach(coding_and_attach(type="document", obj=doc))
            text = check(forwarded=forwarded, adds=self.adds, mess=mess)
            self.msg.attach(text)
        else:
            text = check(forwarded=forwarded, adds=self.adds, mess=mess)
            self.msg.attach(text)

        MailSender(msg=self.msg, receiver=self.receiver).enter_to_send()

    def parse(self, mess: Message) -> None:
        if mess.forward_from:
            self.fors(mess=mess, forwarded=True)
        else:
            self.fors(mess=mess, forwarded=False)