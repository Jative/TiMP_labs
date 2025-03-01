import os                  # Нужна для определения файлов в папке
import json                # Нужна для "запаковывания" данных
import socket              # Нужна для отправки и получения данных от клиентов
import threading           # Нужна для работы с несколькими клиентами разом


CHUNK_SIZE = 4096          # Размер пачки, которую можно отправить и принять разом
MAX_BAD_REQ_COUNT = 5      # Сколько плохих запросов нужно для закрытия соединения
PORT = 9090                # Порт сервера
CMD_SEP = "*-*"            # Разделитель в командах, ставится между аргументами


class DBWorker: # Класс для работы с файлом
    def __init__(self, filename: str):
        self.lock = threading.Lock()              # Создаём мьютекс для работы внутри
        self.filename = filename                  # объекта класса
        if self.filename not in os.listdir():
            f = open(self.filename, "w")
            f.close()
        self.__books = list()
        self.__init_books()
    
    @property                                     # books теперь свойство, чтобы мы могли
    def books(self):                              # использовать мьютекс при работе с ним
        return self.__books
    
    @books.setter                                 # Одновременно список книг
    def books(self, value):                       # может изменять только один поток.
        with self.lock:                           # Эта конструкция с with позволяет
            self.__books = value                  # удобно использовать мьютекс
    
    def __init_books(self):
        with open(self.filename, "r") as file:
            lines = file.readlines()
            for i in range(len(lines)//11):
                book = list()
                for j in range(11):
                    book.append(lines[i*11+j][:-1])
                self.books.append(book)
    
    def __write_data(self):
        with self.lock:                            # Одновременно с файлом может работать
            with open(self.filename, "w") as file: # только один поток
                for book in self.books:
                    for line in book:
                        file.write(line+"\n")
    
    def get_book_list(self):
        return list(map(lambda x: x[0], self.books))
    
    def find_books(self, string):
        found_books = list()
        for book in self.books:
            if string in book[0] or \
               string in book[1] or \
               string in book[2]:
               found_books.append(book)
        return found_books
    
    def add_book(self, data):
        for book in self.books:
            if book[0] == data[0]:
                return False
        self.books.append(data)
        self.__write_data()
        return True
    
    def edit_book(self, book_name, index, string):
        for book in self.books:
            if book_name == book[0]:
                book[index] = string
                self.__write_data()
                return True
        return False
    
    def remove_book(self, book_name):
        for i, book in enumerate(self.books):
            if book_name == book[0]:
                del self.books[i]
                self.__write_data()
                return True
        return False
    
    def get_book(self, book_name):
        for book in self.books:
            if book[0] == book_name:
                return book
        return []


def send_data(cl_sock, data):
    """
    Функция для отправки данных любого размера. Сначала происходит сериализация
    данных в json и кодирование, считается размер в байтах. Размер отправляется
    клиенту, чтобы он знал, сколько данных ему следует принять.
    После этого отправляются данные пачками размером CHUNK_SIZE
    """
    dumped_data = json.dumps(data).encode("utf-8")
    cl_sock.sendall((len(dumped_data) if data
                    else 0).to_bytes(4, byteorder="big"))
    if data:
        cl_sock.sendall(dumped_data)

def send_bool(cl_sock, value):
    """
    Функция отправки булевых значений. В этом проекте используется для отправки
    результата работы сервера. Единица при успехе и ноль при неудаче
    """
    cl_sock.send(bytes([1] if value else [0]))


def work_thread(cl_sock: socket.socket, cl_addr: tuple, db_worker: DBWorker) -> None:
    """
    Функция работы с отдельным потоком. Она слушает порт сервера и реагирует на
    сообщения от определённого порта клиента. В остальном, всё работает также
    """
    print(cl_addr[1], "соединение установлено", sep=": ")
    bad_req_count = 0
    running = True
    while running:
        try:
            command = cl_sock.recv(CHUNK_SIZE).decode("utf-8")
        except:
            command = ""
        print(cl_addr[1], command.split(CMD_SEP)[0] if command
                          else "подозрительный запрос", sep=": ")
        match command.split(CMD_SEP)[0]:
            case "1":
                book_list = db_worker.get_book_list()
                send_data(cl_sock, book_list)
            case "2":
                search_string = command.split(CMD_SEP)[1]
                found_books = db_worker.find_books(search_string)
                send_data(cl_sock, found_books)
            case "3":
                data = json.loads(command.split(CMD_SEP)[1])
                added = db_worker.add_book(data)
                send_bool(cl_sock, added)
            case "4":
                book_name = command.split(CMD_SEP)[1]
                index = int(command.split(CMD_SEP)[2])
                string = command.split(CMD_SEP)[3]
                edited = db_worker.edit_book(book_name, index, string)
                send_bool(cl_sock, edited)
            case "5":
                book_name = command.split(CMD_SEP)[1]
                removed = db_worker.remove_book(book_name)
                send_bool(cl_sock, removed)
            case "6":
                book_name = command.split(CMD_SEP)[1]
                book = db_worker.get_book(book_name)
                send_data(cl_sock, book)
            case "0":
                running = False
                print(cl_addr[1], "соединение разорвано клиентом", sep=": ")
            case _:
                bad_req_count += 1 # Если клиент отправляет что-то невразумительное,
                                   # увеличиваем счётчик его плохих запросов
                if bad_req_count == MAX_BAD_REQ_COUNT:
                    running = False
                    print(cl_addr[1], "соединение разорвано сервером", sep=": ")
    cl_sock.close() # По завершении работы закрываем подключение


def main():
    db_worker = DBWorker("books.txt")    # Создание "работника" с книгами
    sock = socket.socket()               # Создание сокета
    sock.bind(("localhost", PORT))       # Прибивание порта к сокету
    sock.listen(1)                       # Единовременно может подключиться лишь один
    while True:                          # клиент, но их максимальное число не ограничено
        cl_sock, cl_addr = sock.accept() # В цикле принимаем подключения
        t = threading.Thread(target=work_thread, # И для каждого создаём по потоку
                             args=(cl_sock, cl_addr, db_worker))
        t.start()                        # Этот поток запускаем

main()
