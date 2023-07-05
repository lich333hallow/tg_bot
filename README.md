# Настройка бота
### Библиотеки
Нужные библиотеки:
- pyTelegramBotAPI==4.12.0
- pandas==2.0.3
  
Установка с помощью pip:
```
pip install pyTelegramBotAPI
pip install pandas
```
### Файл settings.py
Файл settings.py должен заполнен следующим образом:
```py
settings = {
    "TOKEN": "<TG BOT TOKEN>",
    "LOGIN": "<SENDER MAIL ADDRESS>",
    "PASSWORD": "<SENDER MAIL AUTH KEY>",
    "SERVER": "<SENDER MAIL STMP SERVER>"
}
disk = {
    "TOKEN": "<YANDEX TOKEN>",
    "RESOURCES": "https://cloud-api.yandex.net/v1/disk/resources"
}
```
Вместо `<TG BOT TOKEN>` вставьте свой токен телеграмм бота.

Вместо `<SENDER MAIL ADDRESS>` вставьте адрес той почты с которой на вашу почту будут приходить письма.

Вместо `<SENDER MAIL AUTH KEY>` вставьте пароль от почты из `<SENDER MAIL ADDRESS>`.

Вместо `<SENDER MAIL STMP SERVER>` вставьте stmp сервер почты из `<SENDER MAIL ADDRESS>`

Вместо `<YANDEX TOKEN>` вставьте Яндекс Токен.

Список stmp серверов:
| Почта | SMTP сервер |
|:------|:------------|
| Gmail | smtp.gmail.com |
| Yahoo Mail | smtp.mail.yahoo.com |
| Yahoo Mail Plus | plus.smtp.mail.yahoo.com |
| mail.ru (рекомендуется) | smtp.mail.ru |
| Yandex.ru | smtp.yandex.ru |
