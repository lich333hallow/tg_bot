import os
from smtplib import SMTP
from ssl import create_default_context
from settings import settings
from os import remove
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from telebot.types import Message, PhotoSize, Document, Video
from telebot import TeleBot
from datetime import datetime, timezone, timedelta
from webdav3.client import Client

bot = TeleBot(settings["TOKEN"])
data = {
    'webdav_hostname': "https://webdav.cloud.mail.ru",
    'webdav_login': settings["LOGIN"],
    'webdav_password': settings["PASSWORD"]
}
client = Client(data)


def writing_file(filename: str, data: bytes) -> None:
    with open(f"{filename}", "wb+") as file:
        file.write(data)
    file.close()


def coding_and_attach(types: str, obj: PhotoSize | Document | Video) -> bool:
    if types == "photo":
        file_info = bot.get_file(obj[len(obj) - 1].file_id)
        downloaded_file = bot.download_file(file_info.file_path)
        writing_file(f"{file_info.file_unique_id}.{file_info.file_path[-3:]}", downloaded_file)
        client.upload_sync(remote_path=f"/sending/Фото/{file_info.file_unique_id}.{file_info.file_path[-3:]}",
                           local_path=f"{file_info.file_unique_id}.{file_info.file_path[-3:]}")
        remove(f"{file_info.file_unique_id}.{file_info.file_path[-3:]}")
    else:
        file_info = bot.get_file(obj.file_id)
        downloaded_file = bot.download_file(file_info.file_path)
        writing_file(f"{file_info.file_unique_id}.{file_info.file_path[-3:]}", downloaded_file)
        if types == "video":
            client.upload_sync(remote_path=f"/sending/Видео/{file_info.file_unique_id}.{file_info.file_path[-3:]}",
                               local_path=f"{file_info.file_unique_id}.{file_info.file_path[-3:]}")
        elif types == "document":
            client.upload_sync(remote_path=f"/sending/Документы/{file_info.file_unique_id}.{file_info.file_path[-3:]}",
                               local_path=f"{file_info.file_unique_id}.{file_info.file_path[-3:]}")
        remove(f"{file_info.file_unique_id}.{file_info.file_path[-3:]}")
    return True


def check(forwarded: bool, adds: str, mess: Message) -> MIMEText:
    tz = timezone(+timedelta(hours=6))
    if forwarded:
        message = f"{adds}\n--------------\nОт: " \
                  f"{mess.forward_from.first_name if mess.forward_from.first_name is not None else mess.forward_from.username}" \
                  f" ({datetime.fromtimestamp(mess.date, tz).strftime('%H:%M:%S %d-%m-%Y')})"
        text = MIMEText(message, "plain")
    else:
        message = f"{adds}\n-------\nОт: " \
                  f"{mess.from_user.first_name if mess.from_user.first_name is not None else mess.from_user.username}" \
                  f" ({datetime.fromtimestamp(mess.date, tz).strftime('%H:%M:%S %d-%m-%Y')})"
        text = MIMEText(message, "plain")
    return text


class MailSender:
    def __init__(self, msg: MIMEMultipart, receiver: str) -> None:
        self.sender = settings["LOGIN"]
        self.server = settings["SERVER"]
        self.msg = msg
        self.msg["To"] = receiver
        self.msg["From"] = self.sender
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
    def __init__(self, photos: list, documents: list, videos: list,
                 adds: str, receiver: str) -> None:
        self.photos = photos
        self.documents = documents
        self.adds = adds
        self.receiver = receiver
        self.msg = MIMEMultipart()
        self.videos = videos
        self.a = False

    def fors(self, mess: Message, forwarded: bool) -> None:
        if self.photos or self.documents or self.videos:
            for ph in self.photos:
                self.a = coding_and_attach(types="photo", obj=ph)
                print(self.a)
            for doc in self.documents:
                self.a = coding_and_attach(types="document", obj=doc)
            for video in self.videos:
                self.a = coding_and_attach(types="video", obj=video)
            text = check(forwarded=forwarded, adds=self.adds, mess=mess)
            try:
                self.msg["Subject"] = f"Из приватного чата" if mess.chat.type == "private" else \
                    f"Из {mess.forward_from_chat.title}"
            except Exception as e:
                print(e)
        else:
            text = check(forwarded=forwarded, adds=self.adds, mess=mess)
            try:
                self.msg["Subject"] = f"Из приватного чата" if mess.chat.type == "private" else \
                    f"Из {mess.forward_from_chat.title}"
            except Exception as e:
                pass
        if self.a:
            message = "Ссылка на файлы: https://cloud.mail.ru/public/tttb/VwVtiUxL5\n"
            text1 = MIMEText(message, "plain")
            print("attached")
            self.msg.attach(text1)
        self.msg.attach(text)
        MailSender(msg=self.msg, receiver=self.receiver).enter_to_send()

    def parse(self, mess: Message) -> None:
        if mess.forward_from:
            self.fors(mess=mess, forwarded=True)
        else:
            self.fors(mess=mess, forwarded=False)
