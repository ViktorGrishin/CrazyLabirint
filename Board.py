import random

import pygame
import os
import sys
from copy import deepcopy

# карты представлены числами для возможности изменения их облика. Нумерация начинается с единицы
CARDS = list(range(1, 25))
SPACING = 5  # Зазор между карточками на поле
COLOR_KEY = (255, 255, 255)
CELL_SIZE = 50
K = 0.5
SPECIAL_CELL_CORDS = 500, 500
DEFAULT_BOARD = [[101, 0, 1, 0, 2, 0, 102],
                 [0, 0, 0, 0, 0, 0, 0],
                 [3, 0, 4, 0, 5, 0, 6],
                 [0, 0, 0, 0, 0, 0, 0],
                 [7, 0, 8, 0, 9, 0, 10],
                 [0, 0, 0, 0, 0, 0, 0],
                 [103, 0, 11, 0, 12, 0, 104]]


def next_player():
    players = ['red', 'blue', 'green', 'yellow']
    random.shuffle(players)

    i = 0
    while True:
        yield players[i]
        i = (i + 1) % len(players)


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
        self.rotation = (-angle + self.rotation) % 360

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

    def info(self):
        return [self.kind, self.card, self.rotation]


class Board:
    def __init__(self, cords=(0, 0), board_size=(1, 1)):
        self.players = {'yellow': [[0, 1], self._load_player_images('yellow', K)],
                        'red': [[1, 0], self._load_player_images('red', K)],
                        'green': [[6, 1], self._load_player_images('green', K)],
                        'blue': [[1, 6], self._load_player_images('blue', K)]
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

    def _render_cells(self):
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

    def update_board_screen(self):
        self.board_screen = self.start_screen.copy()
        self._render_cells()
        # Отображаем игроков
        self._render_player(self.board_screen)
        # Изменяем размеры поля по коэффициентам
        w, h = self.board_screen.get_size()
        w1, h1 = w * self.board_size[0], h * self.board_size[1]
        self.board_screen = pygame.transform.scale(self.board_screen, (w1, h1))

    def move_labyrinth(self):
        move = target = None
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
            move = False, j
            target = 1


        elif self.special_cell_cords[0] == len(self.board):
            # Двигаем снизу вверх
            j = self.special_cell_cords[1]
            special = self.board[0][j]
            for i in range(0, len(self.board) - 1):
                self.board[i][j] = self.board[i + 1][j]

            self.board[len(self.board) - 1][j] = self.special_cell
            self.special_cell = special
            self.canceled_move = -1, j
            move = False, j
            target = -1

        elif self.special_cell_cords[1] == -1:
            # Двигаем слева направо
            i = self.special_cell_cords[0]
            special = self.board[i][len(self.board) - 1]
            for j in range(len(self.board) - 1, 0, -1):
                self.board[i][j] = self.board[i][j - 1]

            self.board[i][0] = self.special_cell
            self.special_cell = special
            self.canceled_move = i, len(self.board)
            move = True, i
            target = 1

        elif self.special_cell_cords[1] == len(self.board):
            # Двигаем справа налево
            i = self.special_cell_cords[0]
            special = self.board[i][0]
            for j in range(0, len(self.board) - 1):
                self.board[i][j] = self.board[i][j + 1]

            self.board[i][len(self.board) - 1] = self.special_cell
            self.special_cell = special
            self.canceled_move = i, -1
            move = True, i
            target = -1

        self._drop_players(move, target)
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

    def _get_vars_moving(self, cell):
        variants = []
        i, j = cell

        if not (0 <= i < len(self.board) and 0 <= j < len(self.board[0])):
            # Клетка не на поле
            return []
        kind, _, rotation = self.board[i][j].info()

        if kind == 3:
            # Прямая клетка
            if rotation in [0, 180]:
                # Горизонтальная
                variants.append([i, j + 1])
                variants.append([i, j - 1])
            elif rotation in [90, 270]:
                # Вертикальная
                variants.append([i + 1, j])
                variants.append([i - 1, j])
            else:
                print('Alarm!!!')

        elif kind == 1:
            # Угловая
            if rotation == 0:
                variants.append([i, j + 1])
                variants.append([i - 1, j])

            elif rotation == 90:
                variants.append([i, j + 1])
                variants.append([i + 1, j])

            elif rotation == 180:
                variants.append([i, j - 1])
                variants.append([i + 1, j])

            elif rotation == 270:
                variants.append([i, j - 1])
                variants.append([i - 1, j])
            else:
                print('Alarm!!!')

        else:
            # Т-образная
            if rotation == 0:
                variants.append([i, j + 1])
                variants.append([i, j - 1])
                variants.append([i - 1, j])

            elif rotation == 90:
                variants.append([i + 1, j])
                variants.append([i - 1, j])
                variants.append([i, j + 1])

            elif rotation == 180:
                variants.append([i, j + 1])
                variants.append([i, j - 1])
                variants.append([i + 1, j])

            elif rotation == 270:
                variants.append([i + 1, j])
                variants.append([i - 1, j])
                variants.append([i, j - 1])
            else:
                print('Alarm!!!')

        return variants

    def _is_correct_player_moving(self, start_cords, target, passed=[]):
        # Рекурсивная функция проверки возможных дорог
        i, j = start_cords[:]

        if not (0 <= i < len(self.board) and 0 <= j < len(self.board[0])):
            # Клетка не на поле
            return False
        if start_cords in passed:
            # Мы были уже в этой клетке
            return False
        passed.append(start_cords)
        if start_cords == target:
            # Мы уже жостигли цели
            return True


        corr_vars = []
        variants = self._get_vars_moving(start_cords)[:]
        for cell in variants:
            if start_cords in self._get_vars_moving(cell)[:]:
                corr_vars.append(cell[:])

        # Есть ли возможность добраться до цели?
        for var in corr_vars:
            if self._is_correct_player_moving(var[:], target[:], passed[:]):
                return True

        return False

    def move_player(self, player, mouse_pos):
        target = self.get_cell(mouse_pos)
        if target is not None:
            target = list(target)[:]
            start_cell = self.players[player][0][:]
            print(start_cell, target)
            if self._is_correct_player_moving(start_cell[:], target[:], passed=[]):
                self.players[player][0] = list(target)[:]
                self.update_board_screen()
                return True
            else:
                return 'Невозможно добраться'

        return 'Нажмите на клетку на поле'

    def _render_player(self, screen):
        for player, cords_image in self.players.items():
            cords, image = cords_image
            h, w = cords
            w1, h1 = image.get_size()
            dx, dy = 0, 0
            if player == 'red':
                dx = self.cell_size // 3 * 2
            elif player == 'green':
                dy = self.cell_size // 3 * 2
            elif player == 'blue':
                dx = dy = self.cell_size // 3 * 2

            screen.blit(image, ((self.cell_size + SPACING) * w + self.cell_size + dx,
                                (self.cell_size + SPACING) * h + self.cell_size + dy))

    def _load_player_images(self, color, k):
        fullname = os.path.join('data', 'images', 'players', color + '.png')
        image = pygame.image.load(fullname)
        # Обработка фона
        if COLOR_KEY is not None:
            image = image.convert()
            if COLOR_KEY == -1:
                color_key = image.get_at((0, 0))
                image.set_colorkey(color_key)
            else:
                image.set_colorkey(COLOR_KEY)
        else:
            image = image.convert_alpha()

        x, y = image.get_size()
        new_size = x * k, y * k
        image = pygame.transform.scale(image, new_size)
        return image

    def _drop_players(self, move, target):
        for player, cords_image in self.players.items():
            cords, _ = cords_image
            i, j = cords
            if move[0]:  # Проверяем строку перемещение
                if i == move[1]:
                    self.players[player][0] = [i, (j + target) % len(self.board)]
            else:  # столбец перемещения
                if j == move[1]:
                    self.players[player][0] = [(i + target) % len(self.board), j]


if __name__ == '__main__':

    pygame.init()
    size = width, height = 1800, 800
    # screen = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
    screen = pygame.display.set_mode(size)
    # k = 0
    a = Board((100, 100), (0.35, 0.35))
    # a.special_cell_cords = -1, -1
    # a.update_board_screen()

    running = True
    move_phase = True

    give_player = next_player()
    player = next(give_player)
    print(f'Ходит {player}')
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

                ret = a.move_player(player, event.pos)
                if ret is True:
                    move_phase = True
                    player = next(give_player)
                    print(f'Ходит {player}')
                else:
                    print(ret)

            elif event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE and (not move_phase):
                # Игрок не перемещается
                player = next(give_player)
                print(f'Ходит {player}')
                move_phase = True



        # if k == 1000:
        #     print(a.move_labyrinth())
        a.render(screen)
        pygame.display.flip()
        # k += 1

    terminate()
