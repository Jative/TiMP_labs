import re                      # Библиотека для работы с регулярными выражениями
import json                    # Библиотека, которая умеет упаковывать данные для отправки
import socket                  # Библиотека для сетевого взаимодействия
from datetime import datetime  # Дата и время


CHUNK_SIZE = 4096              # Размер пачки, которую можно отправить и принять разом
PORT = 9090                    # Порт сервера
CMD_SEP = "*-*"                # Разделитель в командах, ставится между аргументами


# Переписанные проверки. Тут используются регулярные выражения
def correct_book_name(book_name):
    return re.match(r"^[A-Za-zА-Яа-я\s,!?]+$", book_name)

def correct_authors(authors):
    return re.match(r"^[A-Za-zА-Яа-я\s,]+$", authors)

def correct_genre(genre):
    return re.match(r"^[A-Za-zА-Яа-я\s,]+$", genre)

def correct_year(year):
    return re.match(r"^-?\d{1,4}$", year) and \
           int(year) <= datetime.now().year

def correct_size(size):
    return re.match(r"^\d+$", size)

def correct_binding(binding):
    return re.match(r"^(мягкий|твёрдый)$", binding)

def correct_source(source):
    return re.match(r"^(покупка|подарок|наследство)$", source)

def correct_date(old_date: str, date):
    if not re.match(r"^(0?[1-9]|[12][0-9]|3[01])\.(0?[1-9]|1[0-2])\.(\d{4})$",
                    date):
        return False
    if int(date.split(".")[2]) > datetime.now().year:
        return False
    if datetime.strptime(date, r"%d.%m.%Y") < \
       datetime.strptime(old_date, r"%d.%m.%Y"):
        return False
    return True

def correct_review(review):
    return re.match(r"^[1-5].*$", review)

# Класс для сетевого взаимодействия со стороны клиента. С ним просто удобнее работать
class Messenger:
    def __init__(self, addr, port, buf_size, cmd_sep):
        self.sock = socket.socket() # При создании нашего посыльного создаём сокет
        self.sock.connect((addr, port)) # Подключаемся к серверу
        self.__chunk_size = buf_size # Сохраняем параметры для работы
        self.__cmd_sep = cmd_sep
    
    def get_data(self): # Метод получения данных от сервера
        """
        Первым делом получаем число от сервера - количество байт, которое
        он должен отправить
        Дальше в цикле получаем эти данные до тех пор, пока не заберём все
        После производим десериализацию из json в понятный питону список
        """
        data_size = int.from_bytes(self.sock.recv(4), byteorder="big")
        received_data = b""
        while len(received_data) < data_size:
            remaining_bytes = data_size - len(received_data)
            received_data += self.sock.recv(min(self.__chunk_size, remaining_bytes))
        return json.loads(received_data) if received_data else []
    
    def get_bool(self): # Метод получения результата от сервера: да или нет
        return int.from_bytes(self.sock.recv(self.__chunk_size)) # 1 в случае успеха и 0 при неудаче
    
    def send_command(self, command, *args): # Метод отправки команды с аргументами
        try: # Пытаемся отправить номер команды и аргументы с разделителем
            message = self.__cmd_sep.join([command]+list(args))
            self.sock.send(message.encode("utf-8"))
            return True # Если получилось, возвращаем успех
        except:
            return False # Иначе неудачу
    
    def send_data(self, command, data):
        """
        Метод отправки малых данных на сервер (не больше одной почки)
        """
        try:
            message = self.__cmd_sep.join([command, json.dumps(data)])
            self.sock.send(message.encode("utf-8"))
            return True
        except:
            return False


def main(): # Главная функция
    try: # Пытаемся подключиться к серверу
        messenger = Messenger("localhost", PORT, CHUNK_SIZE, CMD_SEP)
    except: # При неудаче сообщаем об этом, завершаем выполнение
        print("Сервер недоступен. Завершение работы")
        return
    print(f"Установлено соединение на порте {messenger.sock.getsockname()[1]}")

    print("Команды")
    print("1. Список книг")
    print("2. Поиск по названию, жанру, автору")
    print("3. Добавление книги")
    print("4. Редактирование данных книги")
    print("5. Удаление книги")
    print("6. Информация о книге")
    print("0. Выход")

    running = True
    while running:
        print("="*40)
        while not (inp := input("Команда: ")): pass
        match inp: # Обработка команд по смыслу не изменилась, только теперь они
                   # отправляются на сервер вместо db_worker'а
            case "1":
                messenger.send_command("1")
                book_list = messenger.get_data()
                for i, book_name in enumerate(book_list):
                    print(i+1, book_name, sep=". ")
            case "2":
                search_string = input("Название, жанр или автор: ")
                messenger.send_command("2", search_string)
                if books := messenger.get_data():
                    print("Найденные совпадения:")
                    for i, book in enumerate(books):
                        print(i+1, book[0], sep=". ")
                else:
                    print("Ничего не найдено!")
            case "3":
                data = ["" for i in range(11)]
                temp = ""
                while not correct_book_name(temp := input("Название книги: ")):
                    print("Некорректный ввод!")
                data[0] = temp
                while not correct_authors(temp := input("Авторы: ")):
                    print("Некорректный ввод!")
                data[1] = temp
                while not correct_genre(temp := input("Жанр: ")):
                    print("Некорректный ввод!")
                data[2] = temp
                while not correct_year(temp := input("Год выпуска: ")):
                    print("Некорректный ввод!")
                data[3] = temp
                while not correct_size(temp := input("Ширина обложки: ")):
                    print("Некорректный ввод!")
                data[4] = temp
                while not correct_size(temp := input("Высота обложки: ")):
                    print("Некорректный ввод!")
                data[5] = temp
                while not correct_binding(temp := input("Формат переплёта(мягкий, твёрдый): ")):
                    print("Некорректный ввод!")
                data[6] = temp
                while not correct_source(temp := input("Источник(покупка, подарок, наследство): ")):
                    print("Некорректный ввод!")
                data[7] = temp
                while not correct_date("01.01."+data[3], temp := input("Дата появления в библиотеке(ДД.ММ.ГГГГ): ")):
                    print("Некорректный ввод!")
                data[8] = temp
                while not correct_date(data[8], temp := input("Дата прочтения(ДД.ММ.ГГГГ): ")):
                    print("Некорректный ввод!")
                data[9] = temp
                while not correct_review(temp := input("Оценка с комментарием: ")):
                    print("Некорректный ввод!")
                data[10] = temp
                messenger.send_data("3", data)
                if messenger.get_bool():
                    print(f"Книга '{data[0]}' добавлена успешно!")
                else:
                    print("Книга с таким названием уже существует!")
            case "4":
                while True:
                    book_name = input("Точное название книги: ")
                    messenger.send_command("6", book_name)
                    if book := messenger.get_data():
                        break
                    print("Совпадений не найдено!")
                print("1. Название книги")
                print("2. Авторы")
                print("3. Жанр")
                print("4. Год выпуска")
                print("5. Ширина обложки")
                print("6. Высота обложки")
                print("7. Формат переплёта")
                print("8. Источник появления")
                print("9. Дата появления в библиотеке")
                print("10. Дата прочтения")
                print("11. Оценка с комментарием")
                index = 0
                while not (1 <= index <= 11):
                    try:
                        index = int(input("Что изменить(число): "))
                    except: pass
                while True:
                    string = input("Новое значение: ")
                    if index == 1 and correct_book_name(string):
                        break
                    if index == 2 and correct_authors(string):
                        break
                    if index == 3 and correct_genre(string):
                        break
                    if index == 4 and correct_year(string):
                        break
                    if index in (5, 6) and correct_size(string):
                        break
                    if index == 7 and correct_binding(string):
                        break
                    if index == 8 and correct_source(string):
                        break
                    if index == 9 and correct_date("01.01."+book[3], string) and \
                                      correct_date(string, book[9]):
                        break
                    if index == 10 and correct_date(book[8], string):
                        break
                    if index == 11 and correct_review(string):
                        break
                    print("Некорректное значение")
                messenger.send_command("4", book_name, str(index-1), string)
                if messenger.get_bool():
                    print("Изменения внесены успешно!")
                else:
                    print("Книга с таким названием не найдена!")
            case "5":
                book_name = input("Точное название книги: ")
                messenger.send_command("5", book_name)
                if messenger.get_bool():
                    print(f"Книга '{book_name}' удалена успешно")
                else:
                    print(f"Книга '{book_name}' не найдена")
            case "6":
                book_name = input("Точное название книги: ")
                messenger.send_command("6", book_name)
                if book := messenger.get_data():
                    print(f"Название: {book[0]}")
                    print(f"Авторы: {book[1]}")
                    print(f"Жанр: {book[2]}")
                    print(f"Год выпуска: {book[3]}")
                    print(f"Ширина облоки: {book[4]}")
                    print(f"Высота обложки: {book[5]}")
                    print(f"Формат переплёта: {book[6]}")
                    print(f"Источник появления: {book[7]}")
                    print(f"Дата появления в библиотеке: {book[8]}")
                    print(f"Дата прочтения: {book[9]}")
                    print(f"Оценка с комментарием: {book[10]}")
                else:
                    print(f"Книга '{book_name}' не найдена")
            case "0":
                messenger.send_command("0") # При завершении работы сообщаем об этом
                                            # серверу, чтобы он со своей стороны
                                            # также закрыл подключение
                running = False
            case _:
                print("Неизвестная команда!")
    messenger.sock.close() # После работы закрываем соединение


if __name__ == "__main__":
    main()
