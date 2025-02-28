"""
Генератор данных. Стирает всё содержимое books.txt и заполняет заново по некоторым
правилам. Заполнение происходит через DBWorker, чтобы гарантировать отсутствие
повторов названий книг. В условии цикла указано количество требуемых записей, можно
заменить 10000 на произвольное значение
Использование DBWorker вынуждает с большой скоростью перезаписывать файл на диске,
что круто насилует винчестер, поэтому лично от себя рекомендую по возможности вообще
это не запускать
"""
from random import choice, randint
from faker import Faker                # pip install faker
from server import DBWorker

fake = Faker("ru_RU")
genres = ["Фантастика", "Детектив", "Роман", "Научная литература", "История", "Поэзия"]

with open("books.txt", "w"): pass

db_worker = DBWorker("books.txt")
add_count = 0
while add_count < 10000:
    year = str(randint(1900, 2020))
    lib_date = str(randint(1,30))+"."+str(randint(1,11))+"."+str(int(year)+randint(1, 4))
    read_date = str(int(lib_date.split(".")[0])+randint(1, 31-int(lib_date.split(".")[0])))+"."+ \
                str(int(lib_date.split(".")[1])+randint(1, 12-int(lib_date.split(".")[1])))+"."+ \
                str(int(lib_date.split(".")[2])+randint(1, 2025-int(lib_date.split(".")[2])))
    book = [
        fake.catch_phrase(),                                        # Название
        choice(genres),                                             # Жанр
        fake.last_name()+" " +fake.first_name(),                    # Авторы
        year,                                                       # Год выпуска
        str(randint(30, 1000)),                                     # Ширина обложки
        str(randint(30, 1000)),                                     # Высота обложки
        choice(("мягкий", "твёрдый")),                              # Формат переплёта
        choice(("покупка", "подарок", "наследство")),               # Источник
        lib_date,                                                   # Дата появления в библиотеке
        read_date,                                                  # Дата прочтения
        str(randint(1, 5))+" "+fake.sentence()                      # Отзыв
    ]
    if db_worker.add_book(book):
        add_count += 1
        print(add_count)
