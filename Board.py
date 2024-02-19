import random

import pygame
import os
import sys
from copy import deepcopy

# карты представлены числами для возможности изменения их облика. Начинаем с 1 для возожности булевого сранения
CARDS = list(range(1, 25))
SPACING = 5  # Зазор между карточками на поле
COLOR_KEY = (255, 255, 255)
CELL_SIZE = 50
SPECIAL_CELL_CORDS = 500, 500
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

        fullname = os.path.join('data', 'images', 'cells', str(self.kind) + '.png')
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
                self.card_image = card_image
            else:
                self.card_image = None
            self.image = pygame.transform.rotate(self.image, -self.rotation)

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
        if not self.card_image is None:
            # Накладываем изображение карточки на тайл ровно по центру
            w, h = self.image.get_size()
            w1, h2 = self.card_image.get_size()
            self.image.blit(self.card_image, (w // 2 - w1 // 2, h // 2 - h2 // 2))
        screen.blit(self.image, cords)

    def __str__(self):
        return ' '.join(map(str, (self.kind, self.rotation, self.card)))


class Board:
    def __init__(self, cords=(0, 0), board_size=(1, 1)):
        self.players = {'yellow': [0, 0],
                        'red': [0, 6],
                        'green': [6, 0],
                        'blue': [6, 6]
                        }

        self.board_size = board_size  # Коэффициент увеличения изображения поля в зависимости от экрана
        self.cords = self.left, self.top = cords

        kinds = {1: 16,  # Угловые
                 2: 6,  # Т-образные
                 3: 12  # Прямые
                 }
        ost_cards = list(range(13, 25)) + [0] * 34
        self.board = deepcopy(DEFAULT_BOARD)
        self.width, self.height = len(self.board), len(self.board[0])
        for j in range(len(self.board)):
            for i in range(len(self.board[0])):
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
                    if (i, j) == (0, 0):
                        rotation = 90
                    elif (i, j) == (0, len(DEFAULT_BOARD[0]) - 1):
                        rotation = 180
                    elif (i, j) == (len(DEFAULT_BOARD[0]) - 1, 0):
                        rotation = 0
                    else:
                        rotation = 270

                else:
                    # Т-образный перекрёсток со строго определённой карточкой
                    kind = 2
                    if i == 0:
                        rotation = 180

                    elif i == len(DEFAULT_BOARD[0]) - 1:
                        rotation = 0

                    elif j == 0:
                        rotation = 90

                    elif i == len(DEFAULT_BOARD[0]) - 1:
                        rotation = 270

                    elif (i, j) == (2, 2):
                        rotation = 90

                    elif (i, j) == (2, 4):
                        rotation = 180

                    elif (i, j) == (4, 2):
                        rotation = 0

                    else:  # (4, 4)
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
        self.canceled_move = None
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

    def render(self, screen):
        screen.blit(self.board_screen, self.cords)

    def set_view(self, cords, board_size):
        self.cords = cords
        self.board_size = board_size
        self.update_board_screen()

    def update_board_screen(self):
        self.board_screen = self.start_screen.copy()
        for j in range(len(self.board)):
            for i in range(len(self.board[0])):
                self.board[j][i].render(self.board_screen,
                                        ((self.cell_size + SPACING) * i + self.cell_size,
                                         (self.cell_size + SPACING) * j + self.cell_size))
        if not self.special_cell_cords is None:
            self.special_cell.render(self.board_screen,
                                     (((self.cell_size + SPACING) * self.special_cell_cords[1] + self.cell_size),
                                      ((self.cell_size + SPACING) * self.special_cell_cords[0] + self.cell_size)),
                                     )

        else:
            self.special_cell.render(self.board_screen,
                                     ((self.cell_size + SPACING) * 7 + self.cell_size,
                                      (self.cell_size + SPACING) * 0 + self.cell_size))
        # Изменяем размеры поля по коэффициентам
        w, h = self.board_screen.get_size()
        w1, h1 = w * self.board_size[0], h * self.board_size[1]
        self.board_screen = pygame.transform.scale(self.board_screen, (w1, h1))
        self._render_player(self.board_screen)

    def move_labyrinth(self):
        if self.special_cell_cords is None:
            return 'Выберите ряд'
        if self.special_cell_cords == self.canceled_move:
            return 'Этот ход уже был'
        if self.special_cell_cords[0] == -1:
            # Двигаем сверху вниз
            j = self.special_cell_cords[1]
            special = self.board[len(self.board) - 1][j]
            for i in range(len(self.board) - 1, 0, -1):
                self.board[i][j] = self.board[i - 1][j]

            self.board[0][j] = self.special_cell
            self.special_cell = special
            self.canceled_move = len(self.board), j


        elif self.special_cell_cords[0] == len(self.board):
            # Двигаем снизу вверх
            j = self.special_cell_cords[1]
            special = self.board[0][j]
            for i in range(0, len(self.board) - 1):
                self.board[i][j] = self.board[i + 1][j]

            self.board[len(self.board) - 1][j] = self.special_cell
            self.special_cell = special
            self.canceled_move = -1, j

        elif self.special_cell_cords[1] == -1:
            # Двигаем справа налево
            i = self.special_cell_cords[0]
            special = self.board[i][len(self.board) - 1]
            for j in range(len(self.board) - 1, 0, -1):
                self.board[i][j] = self.board[i][j - 1]

            self.board[i][0] = self.special_cell
            self.special_cell = special
            self.canceled_move = i, len(self.board)

        elif self.special_cell_cords[1] == len(self.board):
            # Двигаем справа налево
            i = self.special_cell_cords[0]
            special = self.board[i][0]
            for j in range(0, len(self.board) - 1):
                self.board[i][j] = self.board[i][j + 1]

            self.board[i][len(self.board) - 1] = self.special_cell
            self.special_cell = special
            self.canceled_move = i, -1

        self.special_cell_cords = None
        self.update_board_screen()
        return True

    def get_cell(self, mouse_pos):
        k = self.board_size[0]
        left = self.left + (self.cell_size + SPACING) * k
        top = self.top + (self.cell_size + SPACING) * k
        # Проверка наличия мыши в пределах поля
        if (mouse_pos[0] < left or mouse_pos[0] > (
                left + self.width * (self.cell_size + SPACING) * k) or
                mouse_pos[1] < top or mouse_pos[1] > (
                        top + self.height * (self.cell_size + SPACING) * k)):
            return None

        # Находим столбец
        cell = [0, 0]
        for i in range(self.width):
            if mouse_pos[0] < left + (self.cell_size + SPACING) * (i + 1) * k:
                cell[1] = i
                break

        # Находим строку
        for i in range(self.height):
            if mouse_pos[1] < top + (self.cell_size + SPACING) * (i + 1) * k:
                cell[0] = i
                break

        return tuple(cell)

    def select_row(self, mouse_pos):
        cell = self.get_cell(mouse_pos)
        if cell is not None:
            if cell[0] == 0 and cell[1] in (1, 3, 5):
                self.special_cell_cords = -1, cell[1]

            elif cell[0] == len(self.board) - 1 and cell[1] in (1, 3, 5):
                self.special_cell_cords = len(self.board), cell[1]

            elif cell[1] == 0 and cell[0] in (1, 3, 5):
                self.special_cell_cords = cell[0], -1

            elif cell[1] == len(self.board) - 1 and cell[0] in (1, 3, 5):
                self.special_cell_cords = cell[0], len(self.board)

            self.update_board_screen()
            return True
        return False

    def rotate_cell(self):
        self.special_cell.rotate()
        self.update_board_screen()

    def move_player(self, color):
        pass

    def _render_player(self, screen):
        pass


if __name__ == '__main__':

    pygame.init()
    size = width, height = 1800, 800
    # screen = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
    screen = pygame.display.set_mode(size)
    # k = 0
    a = Board((100, 100), (0.35, 0.35))
    a.special_cell_cords = -1, -1
    a.update_board_screen()

    running = True
    move_phase = True

    while running:
        for event in pygame.event.get():

            if event.type == pygame.QUIT or (event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE):
                running = False

            elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1 and move_phase:
                a.select_row(event.pos)

            elif event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE and move_phase:
                ret = a.move_labyrinth()
                if ret == True:
                    move_phase = False
                else:
                    print(ret)

            elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 3:
                a.rotate_cell()

            elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1 and (not move_phase):
                print('Ведём работу')

        # if k == 1000:
        #     print(a.move_labyrinth())
        a.render(screen)
        pygame.display.flip()
        # k += 1

    terminate()
