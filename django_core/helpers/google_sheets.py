import logging
from typing import Any, Callable

from django.conf import settings

import httplib2
import apiclient.discovery
from apiclient.discovery import Resource as GoogleServiceConnection
from oauth2client.service_account import ServiceAccountCredentials

logger = logging.getLogger(__name__)


class GoogleSheetsConnection:
    """
        Класс, хранящий информацию
        о подключении к Google API
    """
    credentials = settings.GOOGLE_CREDENTIALS

    def __new__(cls) -> Any:
        """
            Реализация синглтона (храним подключение к таблице)
        """
        if not hasattr(cls, "instance"):
            cls.instance = super(GoogleSheetsConnection, cls).__new__(cls)
            cls.connection = cls.__authorize_connection()
        return cls.instance

    @classmethod
    def __authorize_connection(cls) -> Any:
        credentials = ServiceAccountCredentials.from_json_keyfile_name(
            cls.credentials,
            [
                "https://www.googleapis.com/auth/spreadsheets",
                "https://www.googleapis.com/auth/drive"
            ]
        )
        http_auth = credentials.authorize(httplib2.Http())
        return apiclient.discovery.build("sheets", "v4", http=http_auth)

    def get_connection(self) -> Any:
        return self.connection


class GoogleSheetsAdapter:
    """
        Адаптер для работы с Google Sheets
    """
    spreadsheet_id = settings.GOOGLE_SPREADSHEET_ID

    @classmethod
    def __new__(cls, *args, **kwargs) -> Any:
        """ Синглтон (храним instance подключения) """
        if not hasattr(cls, "instance"):
            cls.instance = super(GoogleSheetsAdapter, cls).__new__(cls)
        return cls.instance

    def __init__(self, connection: GoogleServiceConnection) -> None:
        self.connection = connection

    def spreadsheet_provided(method: Callable) -> Callable:
        """
            Декоратор для проверки переменной среды
            GOOGLE_SPREADSHEET_ID в app.env
        """
        def wrapped(self, *args: tuple, **kwargs: dict) -> None:
            if self.spreadsheet_id: method(self, *args, **kwargs)
            else: logger.critical(f"GOOGLE_SPREADSHEET_ID not found. Check app.env file")
        return wrapped

    def __get_first_empty_row_number(self, sheet_name: str) -> int:
        """
            Получаем номер первой пустой строки
        """
        return len(self.connection.spreadsheets().values().get(
            spreadsheetId=self.spreadsheet_id,
            range=f"{sheet_name}"
        ).execute().get("values", list()))

    def __set_headers_if_not_exist(self, sheet_name: str, range_: str, values: list[list[str]]) -> None:
        """
            Задаем заголовки таблицы, если их нет
        """
        self.connection.spreadsheets().values().update(
            spreadsheetId=self.spreadsheet_id,
            range=f"{sheet_name}!{range_}",
            valueInputOption="USER_ENTERED",
            body={"values": values}
        ).execute()

    @spreadsheet_provided
    def update_profile_course_finished(self, data: dict) -> None:
        """
            Обновление статистики по пользователям, закончивших курс
            Формат таблицы:
                A1 (isu)    B1 (username)   C1 (finished_at)
                000000      test            01.01.1970
        """
        sheet_name = "Окончившие курс. Баки"
        headers = [["ИСУ", "Имя пользователя", "Дата завершения"]]
        headers_range = "A1:C1"

        sheet_row_number = self.__get_first_empty_row_number(sheet_name) + 1

        # Если не было заголовков
        if sheet_row_number == 1:
            self.__set_headers_if_not_exist(sheet_name, headers_range, headers)
            sheet_row_number += 1  # Обновили заголовки (1 строка), записываем во 2ю

        self.connection.spreadsheets().values().update(
            spreadsheetId=self.spreadsheet_id,
            range=f"{sheet_name}!A{sheet_row_number}:C{sheet_row_number}",
            valueInputOption="USER_ENTERED",
            body={
                "values": [
                    [data["isu"], data["username"], data["finished_at"]]
                ]
            }
        ).execute()

    @spreadsheet_provided
    def upload_statistics(self, data: list) -> None:
        """
            Выгрузка текущей статистики по пользователям
            Формат таблицы:
                A1 (isu)    B1 (username)   C1 (email)      D1 (current_lesson)     E1 (current_quest)
                000000      test            test@test.com   test_lesson             first_quest
        """
        sheet_name = "Статистика. Баки"
        headers = [["ИСУ", "Имя пользователя", "Почта", "Текущий урок", "Текущий квест"]]
        headers_range = "A1:E1"

        if not self.__get_first_empty_row_number(sheet_name):
            self.__set_headers_if_not_exist(sheet_name, headers_range, headers)

        self.connection.spreadsheets().values().batchUpdate(
            spreadsheetId=self.spreadsheet_id,
            body={
                "valueInputOption": "USER_ENTERED",
                "data": [
                    {
                        "range": f"{sheet_name}!A2:E{len(data)+1}",
                        "majorDimension": "ROWS",
                        "values": data
                    }
                ]
            }
        ).execute()
