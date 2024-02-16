import random

import pygame
import os
import sys
from copy import deepcopy

# карты представлены числами для возможности изменения их облика. Начинаем с 1 для возожности булевого сранения
CARDS = list(range(1, 25))
SPACING = 5  # Зазор между карточками на поле
COLOR_KEY = None
CELL_SIZE = 50
SPECIAL_CELL_CORDS = 50, 50
DEFAULT_BOARD = [[101, 0, 1, 0, 2, 0, 102],
                 [0, 0, 0, 0, 0, 0, 0],
                 [3, 0, 4, 0, 5, 0, 6],
                 [0, 0, 0, 0, 0, 0, 0],
                 [7, 0, 8, 0, 9, 0, 10],
                 [0, 0, 0, 0, 0, 0, 0],
                 [103, 0, 11, 0, 12, 0, 104]]


def terminate():
    pygame.quit()
    sys.exit()


class Cell:
    def __init__(self, kind, card, rotation=0):
        self.kind = kind
        self.card = card
        self.rotation = rotation

        # Генерация изображения тайла

        # Загрузка основы

        fullname = os.path.join('data', 'images', 'cells', str(self.kind) + 'png')
        if os.path.isfile(fullname):
            self.image = pygame.image.load(fullname)
            # Обработка фона
            if COLOR_KEY is not None:
                self.image = self.image.convert()
                if COLOR_KEY == -1:
                    color_key = self.image.get_at((0, 0))
                    self.image.set_colorkey(color_key)
                else:
                    self.image.set_colorkey(COLOR_KEY)
            else:
                self.image = self.image.convert_alpha()

            # Загрузка "card"
            if card != 0:
                fullname = os.path.join('data', 'images', 'cards', str(self.card) + '.png')
                card_image = pygame.image.load(fullname)
                # Обработка фона
                if COLOR_KEY is not None:
                    card_image = card_image.convert()
                    if COLOR_KEY == -1:
                        color_key = card_image.get_at((0, 0))
                        card_image.set_colorkey(color_key)
                    else:
                        card_image.set_colorkey(COLOR_KEY)
                else:
                    card_image = card_image.convert_alpha()

                # Накладываем изображение карточки на тайл ровно по центру
                width, height = self.image.get_size()
                self.image.blit(card_image, (width // 2, height // 2))

            self.image = pygame.transform.rotate(self.image, self.rotation)

        else:
            print('Нет изображений')
            terminate()

    def rotate(self, clockwise=True):
        angle = 90
        if clockwise:
            angle = -90
        self.image = pygame.transform.rotate(self.image, angle)
        self.rotation = (angle + self.rotation) % 360

    def get_card(self):
        return self.card

    def render(self, screen, cords):
        screen.blit(self.image, cords)

    def __str__(self):
        return self.kind, self.rotation, self.card


class Board:
    def __init__(self, cords):
        self.cords = cords

        kinds = {1: 16,  # Угловые
                 2: 6,  # Т-образные
                 3: 12  # Прямые
                 }
        ost_cards = list(range(13, 25)) + [0] * 34
        self.board = deepcopy(DEFAULT_BOARD)
        for i in range(len(self.board)):
            for j in range(len(self.board[0])):
                card = self.board[i][j]
                if card == 0:
                    # Пустая клетка
                    # Случайным образом определяем тип и карточку клетки
                    cans = []
                    if kinds[1]:
                        cans.append(1)
                    if kinds[2]:
                        cans.append(2)
                    if kinds[3]:
                        cans.append(3)

                    kind = random.choice(cans)
                    kinds[kind] -= 1
                    # Если тип клетки - прямая, то на ней ничего не размещается
                    if kind == 3:
                        rotation = random.choice([0, 90])
                    else:
                        card = random.choice(ost_cards)
                        ost_cards.remove(card)
                        rotation = random.choice([0, 90, 180, 270])

                elif 101 <= card <= 104:
                    # Угловая стартовая клетка
                    kind = 1
                    if (i, j) == (1, 1):
                        rotation = 90
                    elif (i, j) == (1, len(DEFAULT_BOARD[0]) - 1):
                        rotation = 180
                    elif (i, j) == (len(DEFAULT_BOARD[0]) - 1, 1):
                        rotation = 0
                    else:
                        rotation = 270

                else:
                    # Т-образный перекрёсток со строго определённой карточкой
                    kind = 2
                    if i == 1:
                        rotation = 180

                    elif i == len(DEFAULT_BOARD[0]) - 1:
                        rotation = 0

                    elif j == 1:
                        rotation = 90

                    elif i == len(DEFAULT_BOARD[0]) - 1:
                        rotation = 270

                    elif (i, j) == (3, 3):
                        rotation = 90

                    elif (i, j) == (3, 5):
                        rotation = 180

                    elif (i, j) == (5, 3):
                        rotation = 0

                    else:  # (5, 5)
                        rotation = 270

                cell = Cell(kind, card, rotation)
                self.board[i][j] = cell

        cans = []
        if kinds[1]:
            cans.append(1)
        if kinds[2]:
            cans.append(2)
        if kinds[3]:
            cans.append(3)

        card = random.choice(ost_cards)
        ost_cards.remove(card)

        kind = random.choice(cans)
        kinds[kind] -= 1
        # Если тип клетки - прямая, то на ней ничего не размещается
        if kind == 3:
            rotation = random.choice([0, 90])
        else:

            rotation = random.choice([0, 90, 180, 270])

        self.special_cell = Cell(kind, card, rotation)  # карточка, которой всех двигают
        self.cell_size = self.special_cell.image.get_size()[0]
        self.special_cell_cords = None
        # Загружаем фон
        fullname = os.path.join('data', 'images', 'board.png')
        if os.path.isfile(fullname):
            self.start_screen = pygame.image.load(fullname)
            # Обработка фона
            if COLOR_KEY is not None:
                self.start_screen = self.start_screen.convert()
                if COLOR_KEY == -1:
                    color_key = self.start_screen.get_at((0, 0))
                    self.start_screen.set_colorkey(color_key)
                else:
                    self.start_screen.set_colorkey(COLOR_KEY)
            else:
                self.start_screen = self.start_screen.convert_alpha()

        # Отрисовываем карточки на основном экране поля
        self.board_screen = self.start_screen.copy()
        self.update_board_screen()

        # self.board[i][j]
        # self.board_screen = self.bo

        # else:
        #     # Генерация случайного игрового поля
        #     self.board = [[] * size for _ in range(size)]

    def update_board_screen(self):
        self.board_screen = self.start_screen.copy()
        left, top = self.cords
        for i in range(len(self.board)):
            for j in range(len(self.board[0])):
                self.board[i][j].render(self.board_screen,
                                        (left + (self.cell_size + SPACING) * i, top + (self.cell_size + SPACING) * j))
        if not self.special_cell_cords is None:
            self.special_cell.render(self.board_screen,
                                     (left + (self.cell_size + SPACING) * self.special_cell_cords[0],
                                      top + (self.cell_size + SPACING) * self.special_cell_cords[1]))

        else:
            self.special_cell.render(self.board_screen, SPECIAL_CELL_CORDS)
