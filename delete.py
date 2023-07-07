import requests
from settings import disk
import time

headers = {
    'Content-Type': 'application/json',
    'Accept': 'application/json',
    'Authorization': f'OAuth {disk["TOKEN"]}'
}


def delete_files() -> None:
    """
    Удаляет файлы на Яндекс.Диске
    :return None:
    """
    folders, minutes, days = ["Фото", "Видео", "Документы"], 0, 7

    while True:
        if days == 0 and minutes == 0:
            minutes, days = 0, 7
            for i in folders:
                res1 = requests.get(
                    f"{disk['RESOURCES']}/files",
                    headers=headers
                ).json()["items"]
                for file in res1:
                    print("Найден файл " + file["path"])
                    if file["path"] == f"disk:/files/{i}/{file['name']}":
                        requests.put(
                            f"{disk['RESOURCES']}/unpublish?path={file['path']}",
                            headers=headers
                        )
                        requests.delete(
                            f"{disk['RESOURCES']}?path={file['path']}&permanently=true",
                            headers=headers
                        )
                        print("Удалено")
        else:
            time.sleep(60)
            minutes += 1
            if minutes == 1440:
                days += 1
                minutes = 0
