import os # os понадобится для получения списка файлов в папке
from datetime import datetime # datetime используется для сравнения дат


# Функции проверки корректности ввода. Они возвращают True, если всё хорошо, а иначе False
def correct_book_name(book_name: str) -> bool:
    """
    Принимает название книги
    Забраковывает, если название пустое или какой-то символ не относится к списку разрешённых
    """
    if len(book_name) == 0:
        return False
    for symb in book_name:
        if symb not in \
           "абвгдеёжзийклмнопрстуфхцчшщъыьэюяАБВГДЕЁЖЗИЙКЛМНОПРСТУФХЦЧШЩЪЫЬЭЮЯ ,!?1234567890":
            return False
    return True

def correct_authors(authors: str) -> bool:
    """
    Принимает список авторов
    Забраковывает, если список пустой или какой-то символ не относится к списку разрешённых
    """
    if len(authors) == 0:
        return False
    for symb in authors:
        if symb not in \
           "абвгдеёжзийклмнопрстуфхцчшщъыьэюяАБВГДЕЁЖЗИЙКЛМНОПРСТУФХЦЧШЩЪЫЬЭЮЯ ,":
            return False
    return True

def correct_genre(genre: str) -> bool:
    """
    Принимает список жанров
    Забраковывает, если жанр пустой или какой-то символ не относится к списку разрешённых
    """
    if len(genre) == 0:
        return False
    for symb in genre:
        if symb not in \
           "абвгдеёжзийклмнопрстуфхцчшщъыьэюяАБВГДЕЁЖЗИЙКЛМНОПРСТУФХЦЧШЩЪЫЬЭЮЯ ,":
            return False
    return True

def correct_year(year: str) -> bool:
    """
    Принимает год
    Забраковывает, если какой-то символ не относится к списку разрешённых. Минус предусмотрен для лет до н.э.
    Забраковывает, если год больше текущего
    """
    if len(year) == 0:
        return False
    for symb in year:
        if symb not in \
           "-0123456789":
            return False
    if int(year) > datetime.now().year:
        return False
    if int(year) < 1500:
        return False
    return True

def correct_size(size: str) -> bool:
    """
    Принимает размер в мм
    Забраковывает, если это не число или если число меньше или равно нулю
    """
    try:
        return False if int(size) <= 0 else True
    except:
        return False

def correct_binding(binding: str) -> bool:
    """
    Принимает тип переплёта
    Забраковывает, если тип не относится к списку разрешённых
    """
    return True if binding in ("мягкий", "твёрдый") else False

def correct_source(source: str) -> bool:
    """
    Принимает источник
    Забраковывает, если источник не относится к списку разрешённых
    """
    return True if source in ("покупка", "подарок", "наследство") else False

def correct_date(old_date: str, date: str) -> bool:
    """
    Принимает предыдущую дату и текущую в формате "ДД.ММ.ГГГГ"
    Преподалагается, что старая дата всегда корректна
    Забраковывает, если новая дата не состоит из 3 частей, разделённых точкой
    Забраковывает, если день не представлен двумя, месяц двумя, год четырьмя символами
    Забраковывает, если день не в диапазоне от 1 до 31, месяц не в диапазоне от 1 до 12, год больше настоящего
    Забраковывает, если предыдущая дата меньше текущей
    """
    if len(date.split(".")) != 3:
        return False
    if len(date.split(".")[0]) != 2 or \
       len(date.split(".")[1]) != 2 or \
       len(date.split(".")[2]) != 4:
       return False
    try:
        if not (1 <= int(date.split(".")[0]) <= 31) or \
           not (1 <= int(date.split(".")[1]) <= 12) or \
           int(date.split(".")[2]) > datetime.now().year:
           return False
    except:
        return False
    if datetime.strptime(date, r"%d.%m.%Y") < \
       datetime.strptime(old_date, r"%d.%m.%Y"):
        return False
    return True

def correct_review(review: str) -> bool:
    """
    Принимает отзыв
    Забраковывает, если отзыв пустой или не начинается с оценки от 1 до 5
    """
    if len(review) == 0:
        return False
    if review[0] not in "12345":
        return False
    return True


# Класс для взаимодействия с файлом
class DBWorker:
    def __init__(self, filename: str):
        """
        При создании получает название файла, с которым работает
        Если такого файла не существует в текущей папке, он создаётся
        Выполняется инициализация книг
        """
        self.filename = filename
        if self.filename not in os.listdir():
            f = open(self.filename, "w")
            f.close()
        self.__init_books()
    
    def __init_books(self):
        """
        Каждая книга представляется как список из 11 значений типа str
        Все книги собраны в один список books
        Этот метод открывает файл на чтение, читает по 11 строк и упаковывает эти строки в книги,
        которые затем отправляются в books
        """
        self.books = list()
        with open(self.filename, "r") as file:
            lines = file.readlines()
            for i in range(len(lines)//11):
                book = list()
                for j in range(11):
                    book.append(lines[i*11+j][:-1])
                self.books.append(book)
    
    def __write_data(self):
        """
        При сохранении перезаписывается файл с данными, старые значения в нём удаляются
        Запись производится построчно
        """
        with open(self.filename, "w") as file:
            for book in self.books:
                for line in book:
                    file.write(line+"\n")
    
    def print_book_list(self) -> None:
        """
        Перебирает все книги в поле books, выводит их на экран нумеруя
        Сообщает об отсуствии книг, если их нет
        """
        for i, book in enumerate(self.books):
            print(i+1, book[0], sep=". ")
        if not self.books:
            print("Книги не добавлены!")
    
    def print_book_data(self, book_name: str) -> None:
        """
        Принимает точное название книги
        Если такой книги не существует, сообщает об этом
        Иначе печатает все данные о книге
        """
        if book := self.get_book(book_name):
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
            print(f"Книга с названием '{book_name}' не найдена!")
    
    def find_books(self, string: str) -> list[list[str]]:
        """
        Принимает строку, совпадения с которой необходимо найти
        Если в какой-то книге полученная строка является частью названия, жанра или автора,
        добавляет книгу в список
        Возвращает список найденных книг
        """
        found_books = list()
        for book in self.books:
            if string in book[0] or \
               string in book[1] or \
               string in book[2]:
               found_books.append(book)
        return found_books
    
    def add_book(self, data: list[str]) -> bool:
        """
        Принимает в себя список корректных значений для внесения в список в книг
        Если книга с таким названием существует, сообщаем о неудаче
        Иначе добавляем её в список книг и перезаписываем файл, сообщаем об успехе
        """
        for book in self.books:
            if book[0] == data[0]:
                return False
        self.books.append(data)
        self.__write_data()
        return True
    
    def edit_book(self, book_name: str, index: int, string: str) -> bool:
        """
        Принимает точное название книги, номер строки для изменения и новое значения
        Предполагается, что всё, кроме названия книги, обязано быть корректным
        Перебирает все книги, и в случае совпадения с названием меняет заданную строку,
        перезаписывает файл
        Если книга не найдена, сообщаем о неудаче
        """
        for book in self.books:
            if book_name == book[0]:
                book[index] = string
                self.__write_data()
                return True
        return False
    
    def remove_book(self, book_name: str) -> bool:
        """
        Принимает точное название книги
        Если такая книга существует, удаляет её и перезаписывает файл
        Иначе сообщает о неудаче
        """
        for i, book in enumerate(self.books):
            if book_name == book[0]:
                del self.books[i]
                self.__write_data()
                return True
        return False
    
    def get_book(self, book_name: str) -> list[str]:
        """
        Принимает точное название книги
        Если книга существует, возвращает её
        Иначе возвращает пустой список
        """
        for book in self.books:
            if book[0] == book_name:
                return book
        return []


def main() -> None:
    """
    Главная функция. Выводит список доступных команд, создаёт объект DBWorker'а,
    запускает бесконечный цикл для получения и обработки команд
    """
    print("Команды")
    print("1. Список книг")
    print("2. Поиск по названию, жанру, автору")
    print("3. Добавление книги")
    print("4. Редактирование данных книги")
    print("5. Удаление книги")
    print("6. Информация о книге")
    print("0. Выход")

    db_worker = DBWorker("books.txt") # Указано название файла с книгами
    running = True
    while running:
        print("="*40) # Разделитель между командами
        inp = input("Команда: ")
        match inp: # switch в Python оформляется так
            case "1":
                db_worker.print_book_list()
            case "2":
                search_string = input("Название, жанр или автор: ")
                if books := db_worker.find_books(search_string): # Если найдено хоть что-то, выводим
                    print("Найденные совпадения:")
                    for i, book in enumerate(books):
                        print(i+1, book[0], sep=". ")
                else:
                    print("Ничего не найдено!") # Иначе сообщаем о неудаче
            case "3":
                data = ["" for i in range(11)] # По-умолчанию все поля для внесения пустые
                temp = "" # Переменная для сохранения последнего ввода
                # Дальше выполняются проверки на корректность ввода. У пользователя будут запрашиваться
                # данные до тех пор, пока он не введёт корректные. Функции проверки определены выше
                while not correct_book_name(temp := input("Название книги: ")):
                    print("Некорректный ввод!")
                data[0] = temp # При удачном вводе сохраняем его
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
                if db_worker.add_book(data): # Если такой книги не существовало и внесение прошло успешно
                    print(f"Книга '{data[0]}' добавлена успешно!")
                else: # В случае ошибки
                    print("Книга с таким названием уже существует!")
            case "4":
                while True: # Пользователь вводит название книги до тех пор, пока не введёт существующее
                    book_name = input("Точное название книги: ")
                    if book := db_worker.get_book(book_name):
                        break
                    print("Совпадений не найдено!")
                print("1. Название книги") # Предлагаются варианты для изменения
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
                while not (1 <= index <= 11): # До корректного ввода запрашивается номер изменяемой строки
                    try:
                        index = int(input("Что изменить(число): "))
                    except: pass
                while True: # Запрашивается новое значение строки, пока оно не будет корректно
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
                if db_worker.edit_book(book_name, index-1, string): # Если книга существует, изменения вносятся
                    print("Изменения внесены успешно!")
                else: # О неудаче сообщается пользователю
                    print("Книга с таким названием не найдена!")
            case "5":
                book_name = input("Точное название книги: ")
                if db_worker.remove_book(book_name):
                    print(f"Книга '{book_name}' удалена успешна")
                else:
                    print(f"Книга '{book_name}' не найдена")
            case "6":
                book_name = input("Точное название книги: ")
                db_worker.print_book_data(book_name)
            case "0":
                running = False
            case _: # Аналог default в Python
                print("Неизвестная команда!")


if __name__ == "__main__": # Если программа запускается из этого файла, вызываем главную функцию
    main()
