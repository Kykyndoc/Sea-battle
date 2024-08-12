from random import randint
from random import choice
class Dot:
    def __init__(self, x, y):
        self.x = x
        self.y = y

    def __eq__(self, other):
        return self.x == other.x and self.y == other.y

    def __str__(self):
        return f"({self.x}, {self.y})"
class BoardException(Exception):
    pass

class BoardOutException(BoardException):
    def __str__(self):
        return "Вы пытаетесь выстрелить за доску!"

class BoardUsedException(BoardException):
    def __str__(self):
        return "Вы уже стреляли в эту клетку"

class BoardWrongShipException(BoardException):
    pass

class Ship:
    def __init__(self, coord: Dot, course: bool, ship_len: int):
        self.coord = coord
        self.ship_len = ship_len
        self.XP = ship_len
        self.course = course

    @property
    def coors(self):
        res = []
        for i in range(self.ship_len):
            coor_x = self.coord.x - 1
            coor_y = self.coord.y - 1

            if not self.course:
                coor_x += i
            else:
                coor_y += i

            res.append(Dot(coor_x, coor_y))
        return res

    def shooten(self, shot):
        return shot in self.coors

class Board:
    def __init__(self, hid=False, size=6):
        self.size = size
        self.hid = hid
        self.ships = []
        self.field = [['O'] * size for i in range(size)]
        self.busy = []
        self.count = 0

    def __str__(self):
        dosk = ""
        dosk += "  | 1 | 2 | 3 | 4 | 5 | 6 |"
        for i, row in enumerate(self.field):
            dosk += f"\n{i + 1} | " + " | ".join(row) + " |"

        if self.hid:
            dosk = dosk.replace("■", "O")
        return dosk

    def chek_dot(self, d: Dot):
        return not ((0 <= d.x < self.size) and (0 <= d.y < self.size))

    def add_ship(self, ship):
        for d in ship.coors:
            if self.chek_dot(d) or d in self.busy:
                raise BoardWrongShipException()
        for d in ship.coors:
            self.field[d.x][d.y] = "■"
            self.busy.append(d)

        self.ships.append(ship)
        self.conter(ship)

    def conter(self, ship, gran=False):
        bron = [
            (-1, -1), (-1, 0), (-1, 1),
            (0, -1), (0, 0), (0, 1),
            (1, -1), (1, 0), (1, 1)]

        for d in ship.coors:
            for dx, dy in bron:
                cur = Dot(d.x + dx, d.y + dy)
                if not (self.chek_dot(cur)) and cur not in self.busy:
                    if gran:
                        self.field[cur.x][cur.y] = "."
                    self.busy.append(cur)

    def shot(self, d):
        if d in self.busy:
            raise BoardUsedException()
        self.busy.append(d)

        if self.chek_dot(d):
            raise BoardOutException()

        for ship in self.ships:
            if d in ship.coors:
                ship.XP -= 1
                self.field[d.x][d.y] = "X"
                if ship.XP == 0:
                    self.count += 1
                    self.conter(ship, gran = True)
                    print("Корабль уничтожен!")
                    return True
                else:
                    print("Корабль ранен!")
                    return True

        self.field[d.x][d.y] = "."
        print("Мимо!")
        return False

    def begin(self):
        self.busy = []


class Player:
    def __init__(self, board, enemy):
        self.board = board
        self.enemy = enemy

    def ask(self):
        raise NotImplementedError()

    def move(self):
        while True:
            try:
                target = self.ask()
                repeat = self.enemy.shot(target)
                return repeat
            except BoardException as e:
                print(e)


class AI(Player):
    def ask(self):
        d = Dot(randint(0, 5), randint(0, 5))
        print(f"Ход бота: {d.x} {d.y}")
        return d


class User(Player):
    def ask(self):
        while True:
            cords = input("Ваш ход: ").split()

            if len(cords) != 2:
                print(" Введите 2 координаты! ")
                continue

            x, y = cords

            if not (x.isdigit()) or not (y.isdigit()):
                print(" Введите числа! ")
                continue

            x, y = int(x) - 1, int(y) - 1

            return Dot(x, y)

class Game:
    def __init__(self, size=6):
        self.size = size
        user = self.random_board()
        comp = self.random_board()
        comp.hid = True

        self.ai = AI(comp, user)
        self.us = User(user, comp)

    def random_field(self):
        lens_ships = [3, 2, 2, 1, 1, 1, 1]
        board = Board(size = self.size)
        counter = 0
        for i in lens_ships:
            while True:
                counter += 1
                if counter > 3000:
                    return None
                ship = Ship(Dot(randint(0, self.size), randint(0, self.size)), choice([True, False]), i)
                try:
                    board.add_ship(ship)
                    break
                except BoardWrongShipException:
                    pass
        board.begin()
        return board

    def random_board(self):
        board = None
        while board is None:
            board = self.random_field()
        return board

    def greet(self):
        print("-------------------")
        print("  Игра морской бой ")
        print("-------------------")
        print(" формат ввода: x y ")
        print(" x - номер строки  ")
        print(" y - номер столбца ")

    def print_field(self):
        print()
        print("Доска игрока:")
        print()
        print(self.us.board)
        print()
        print("Доска бота:")
        print()
        print(self.ai.board)

    def gameplay(self):
        num = 0
        while True:
            self.print_field()
            if num % 2 == 0:
                print()
                print("Ход игрока!")
                repeat = self.us.move()
            else:
                print()
                print("Ход бота!")
                repeat = self.ai.move()
            if repeat:
                num -= 1
            if self.us.board.count == len(self.us.board.ships):
                self.print_field()
                print()
                print("Бот выиграл!")
                break
            if self.ai.board.count == len(self.ai.board.ships):
                self.print_field()
                print()
                print("Игрок выиграл!")
                break
            num += 1

    def start(self):
        self.greet()
        self.gameplay()

g = Game()
g.start()
















