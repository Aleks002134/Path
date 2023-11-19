import os
import sys
import subprocess
import csv
from typing import Union
from datetime import datetime

# Базовый класс для наследования классами систем


class BaseSystem:
    # получение общих данных базового класса

    def __init__(self, system_path: str) -> None:
        self.system_path = system_path
        self.content = {}
        self.timestamp_format = "%Y-%m-%d %H:%M:%S"
        self.get_folder_content()

    # форматирование вывода даты создания файла

    def data_format_output(self, data: float) -> str:
        date_birth_class_exemplar = datetime.fromtimestamp(data)
        file_date_birth = date_birth_class_exemplar.strftime(self.timestamp_format)
        return file_date_birth

    # получение данных для записи их в словарь

    def get_folder_content(self) -> None:
        os_directory_list = os.listdir(self.system_path)
        content = {"file": [], "folder": []}
        for element in os_directory_list:
            full_element_path = os.path.join(self.system_path, element)
            if os.path.isdir(full_element_path):
                content["folder"].append(full_element_path)
            else:
                content["file"].append(full_element_path)
        self.content = content

    # шаблон списка для файлов
    def files_attributes(self) -> list[tuple[str, str, str, str, str, str]]:
        # abc = [('abc.txt', 'txt', '10B', 'C:\\data\\abc.txt', '2023-10-19 16:38:41', '2023-11-07 12:56:43'), ]
        # return abc
        pass

    # шаблон списка для папок
    def folders_attributes(self) -> list[tuple[str, str, str]]:
        # adc = [('adc', 'C:\\data\\adc', '2023-10-19 16:38:41'), ]
        # return adc
        pass


# класс сбора данных для Windows
class WinSystem(BaseSystem):
    # получение списка данных для файлов Windows
    def files_attributes(self) -> list[tuple[str, str, str, str, str, str]]:
        win_files_attributes_list = []
        for file in self.content["file"]:
            name = os.path.basename(file)
            _, ext = os.path.splitext(name)
            file_size = calculate_size(os.path.getsize(file))
            win_cr_time = os.path.getctime(file)
            win_ch_time = os.path.getmtime(file)
            file_date_cr = self.data_format_output(win_cr_time)
            file_date_ch = self.data_format_output(win_ch_time)
            win_attributes = (name, ext, file_size, file, file_date_cr, file_date_ch)
            win_files_attributes_list.append(win_attributes)
        return win_files_attributes_list

    # получение списка данных для папок Windows
    def folders_attributes(self) -> list[tuple[str, str, str]]:
        win_folders_attributes_list = []
        for folder in self.content["folder"]:
            name = os.path.basename(folder)
            win_cr_time = os.path.getctime(folder)
            folder_date_cr = self.data_format_output(win_cr_time)
            win_attributes = (name, folder, folder_date_cr)
            win_folders_attributes_list.append(win_attributes)
        return win_folders_attributes_list


# класс сбора данных для Linux
class LinSystem(BaseSystem):
    # функция получения даты создания файла или папки для Linux
    # в зависимости от функционала ОС
    @staticmethod
    def birth(location: str) -> float:
        stat_output = os.stat(location)
        birthtime = getattr(stat_output, "st_birthtime", None)
        if birthtime is None:
            lin_cr_time = ["stat", "--format=%W", location]
            stat_linux = subprocess.check_output(lin_cr_time)
            output_decode = stat_linux.decode("utf-8")
            birthtime = float(output_decode)
            if birthtime == 0:
                birthtime = os.stat(location).st_mtime
        return birthtime

    # получение списка данных для файлов Linux
    def files_attributes(self) -> list[tuple[str, str, str, str, str, str]]:
        lin_files_attributes_list = []
        for file in self.content["file"]:
            name = os.path.basename(file)
            _, ext = os.path.splitext(name)
            file_size = calculate_size(os.path.getsize(file))
            file_date_ch = os.stat(file).st_mtime
            file_birth = self.birth(file)
            file_date_birth = self.data_format_output(file_birth)
            file_date_ch_format = self.data_format_output(file_date_ch)
            lin_attributes = (
                name,
                ext,
                file_size,
                file,
                file_date_birth,
                file_date_ch_format,
            )
            lin_files_attributes_list.append(lin_attributes)
        return lin_files_attributes_list

    # получение списка данных для папок Linux
    def folders_attributes(self) -> list[tuple[str, str, str]]:
        lin_folders_attributes_list = []
        for folder in self.content["folder"]:
            name = os.path.basename(folder)
            folder_birth = self.birth(folder)
            folder_date_cr = self.data_format_output(folder_birth)
            lin_attributes = (name, folder, folder_date_cr)
            lin_folders_attributes_list.append(lin_attributes)
        return lin_folders_attributes_list


# Фабрика для получения экземпляра в зависимости от ОС, на которой запускается код
class Factory:
    # Функция получения экземпляра класса
    @staticmethod
    def extraction(system_path) -> Union[WinSystem, LinSystem]:
        if os.name == "nt":
            return WinSystem(system_path)
        elif os.name == "posix":
            return LinSystem(system_path)
        else:
            raise NotImplementedError("На данной системе функционал не поддерживается")


# функция перевода размерности файлов
def calculate_size(size: int) -> str:
    if size < 1024:
        size = f"{size} B"
    elif 1024 < size < 1024**2:
        formula = size / 1024
        size = f"{formula:0.2f} kB"
    elif 1024**2 < size < 1024**3:
        formula = size / 1024**2
        size = f"{formula:0.2f} MB"
    elif size > 1024**3:
        formula = size / 1024**3
        size = f"{formula:0.2f} GB"
    return size


# функция создания csv-файлов и записи в них данных
def reports(files_data: list, folders_data: list) -> None:
    try:
        with open("files.csv", "w", newline="") as file:
            table = csv.writer(file)
            table.writerow(
                ["Name", "Extension", "Size", "Full Path", "Date Create", "Date Change"]
            )
            table.writerows(files_data)
    except PermissionError:
        print("Не достаточно прав")
    except IOError:
        print("Ошибка записи в файл")

    try:
        with open("folders.csv", "w", newline="") as folder:
            table = csv.writer(folder)
            table.writerow(["Name", "Full Path", "Date Create"])
            table.writerows(folders_data)
    except PermissionError:
        print("Не достаточно прав")
    except IOError:
        print("Ошибка записи в файл")


def main() -> None:
    if len(sys.argv) != 2:
        print("Введите путь")
        return

    path = sys.argv[1]
    if not os.path.exists(path):
        print("Введите правильный путь")
        return

    if not os.path.isdir(path):
        print("Можно просматривать только директории")
        return

    worker = Factory.extraction(path)
    files_data = worker.files_attributes()
    folders_data = worker.folders_attributes()
    reports(files_data, folders_data)


if __name__ == "__main__":
    main()
