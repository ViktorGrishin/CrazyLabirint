import random

# карты представлены числами для возможности изменения их облика. Начинаем с 1 для возожности булевого сранения
CARDS = list(range(1, 25))


class Cell:
    def __init__(self, up, right, down, left, content=None):
        # Направления клетки - то, откуда из неё есть выходы - булевые значения
        self.up = up
        self.right = right
        self.down = down
        self.left = left
        # Номер значка или его отсутствие
        self.content = content

    def rotate(self, clockwise=True):
        if clockwise:
            self.up, self.right, self.down, self.left = self.left, self.up, self.right, self.down
        else:
            self.up, self.right, self.down, self.left = self.right, self.down, self.left, self.up


class Board:
    def __init__(self, size=7, classic=True):
        if classic:
            pass
        else:
            # Генерация случайного игрового поля
            self.board = [[] * size for _ in range(size)]
