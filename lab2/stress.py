"""
Считывает первые две строки из файла books.txt и создаёт THREAD_COUNT потоков,
которые бесконечно делают запросы на изменение второй строки в файле. В результате
файл не изменится, но появится возможность наглядно оценить отказоустойчивость сервера
"""
import socket
import threading

PORT = 9090
THREAD_COUNT = 32
CMD_SEP = "*-*"

with open("books.txt", "r") as file:
    book_name = file.readline()[:-1]
    value = file.readline()[:-1]

def thr():
    sock = socket.socket()
    sock.connect(("localhost", PORT))
    while True:
        sock.send(("4"+CMD_SEP+book_name+CMD_SEP+"1"+
                CMD_SEP+value).encode("utf-8"))
        sock.recv(16384)

for i in range(THREAD_COUNT):
    t = threading.Thread(target=thr)
    t.start()