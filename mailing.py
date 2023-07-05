import requests
from smtplib import SMTP
from ssl import create_default_context
from settings import settings, disk
from os import remove
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from telebot.types import Message, PhotoSize, Document, Video
from telebot import TeleBot
from datetime import datetime, timezone, timedelta

bot = TeleBot(settings["TOKEN"])
URL = disk["RESOURCES"]
headers = {
    'Content-Type': 'application/json',
    'Accept': 'application/json',
    'Authorization': f'OAuth {disk["TOKEN"]}'
}


def upload_file(loadfile: str, savefile: str, replace=False) -> None:
    """
        Загрузка файла.
        :param savefile: Путь к файлу на Диске
        :param loadfile: Путь к загружаемому файлу
        :param replace: true or false Замена файла на Диске
        :return None:
    """
    res = requests.get(f'{URL}/upload?path={savefile}&overwrite={replace}', headers=headers).json()
    with open(loadfile, 'rb') as f:
        try:
            requests.put(res['href'], files={'file':f})
        except KeyError:
            print(res)


def publish(path: str) -> str:
    """
    Получение ссылки на файл в Яндекс.Диск
    :param path: путь к файлу на Яндекс.Диск
    :return str:
    """
    res = requests.put(f"{URL}/publish?path={path}", headers=headers)
    res.raise_for_status()
    result = requests.get(res.json()["href"], headers=headers)
    url = result.json()["public_url"]
    return url


def writing_file(filename: str, data: bytes) -> None:
    """
    Записывает данные в файл
    :param filename: имя файла
    :param data: данные для записи
    :return None:
    """
    with open(f"{filename}", "wb+") as file:
        file.write(data)
    file.close()


def coding_and_attach(types: str, obj: PhotoSize | Document | Video) -> bool:
    """
    Отправка файлов на Яндекс.Диск
    :param types: тип файла
    :param obj: файл
    :return bool:
    """
    url = ""
    if types == "photo":
        file_info = bot.get_file(obj[len(obj) - 1].file_id)
        downloaded_file = bot.download_file(file_info.file_path)
        filename = f"{file_info.file_unique_id}.{file_info.file_path[-3:]}"
        writing_file(filename, downloaded_file)
        upload_file(savefile=f"disk:/files/Фото/{filename}", loadfile=filename, replace=True)
        url = publish(path=f"disk:/files/Фото/{filename}")
        print(url)
        remove(f"{file_info.file_unique_id}.{file_info.file_path[-3:]}")
    else:
        file_info = bot.get_file(obj.file_id)
        downloaded_file = bot.download_file(file_info.file_path)
        filename = f"{file_info.file_unique_id}.{file_info.file_path[-3:]}"
        writing_file(filename, downloaded_file)
        if types == "document":
            upload_file(savefile=f"disk:/files/Документы/{filename}", loadfile=filename, replace=True)
            url = publish(path=f"disk:/files/Документы/{filename}")
            print(url)
        elif types == "video":
            upload_file(savefile=f"disk:/files/Видео/{filename}", loadfile=filename, replace=True)
            url = publish(path=f"disk:/files/Видео/{filename}")
            print(url)
        remove(f"{file_info.file_unique_id}.{file_info.file_path[-3:]}")
    return url


def check(forwarded: bool, adds: str, mess: Message) -> MIMEText:
    """
    Создание сообщения для отправки
    :param forwarded: тип сообщения
    :param adds: комментарии к сообщению
    :param mess: сообщение
    :return MIMEText:
    """
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
        """
        Отправка сообщения на почту
        :return None:
        """
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
        """
        Подготовка письма к отправке
        :param mess: сообщение
        :param forwarded: тип сообщения
        :return None:
        """
        if self.photos or self.documents or self.videos:
            for ph in self.photos:
                self.a = coding_and_attach(types="photo", obj=ph)
                message = f"Ссылка на фото: {self.a}\n"
                text = MIMEText(message, "plain")
                self.msg.attach(text)
            for doc in self.documents:
                self.a = coding_and_attach(types="document", obj=doc)
                message = f"Ссылка на документ: {self.a}\n"
                text = MIMEText(message, "plain")
                self.msg.attach(text)
            for video in self.videos:
                self.a = coding_and_attach(types="video", obj=video)
                message = f"Ссылка на видео: {self.a}\n"
                text = MIMEText(message, "plain")
                self.msg.attach(text)
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
        self.msg.attach(text)
        MailSender(msg=self.msg, receiver=self.receiver).enter_to_send()

    def parse(self, mess: Message) -> None:
        """
        Парсинг сообщения
        :param mess: сообщения
        :return None:
        """
        if mess.forward_from:
            self.fors(mess=mess, forwarded=True)
        else:
            self.fors(mess=mess, forwarded=False)
