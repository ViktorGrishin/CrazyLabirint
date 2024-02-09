import pygame
import os
import sys

# карты представлены числами для возможности изменения их облика. Начинаем с 1 для возожности булевого сранения
CARDS = list(range(1, 25))
COLOR_KEY = None
CELL_SIZE = 50
DEFAULT_BOARD = [[0, 0, 0, 0, 0, 0, 0, 0, 0],
                 [0, 0, 0, 0, 0, 0, 0, 0, 0],
                 [0, 0, 0, 0, 0, 0, 0, 0, 0],
                 [0, 0, 0, 0, 0, 0, 0, 0, 0],
                 [0, 0, 0, 0, 0, 0, 0, 0, 0],
                 [0, 0, 0, 0, 0, 0, 0, 0, 0],
                 [0, 0, 0, 0, 0, 0, 0, 0, 0],
                 [0, 0, 0, 0, 0, 0, 0, 0, 0],
                 [0, 0, 0, 0, 0, 0, 0, 0, 0]]


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
                fullname = os.path.join('data', 'images', 'cards', str(self.card) + 'png')
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

        else:
            self.image = (self.kind, self.rotation)

    def rotate(self, clockwise=True):
        pass

    def give_card(self):
        return self.card

    def __str__(self):
        return self.kind, self.rotation, self.card


class Board:
    def __init__(self, size=7, classic=True):
        if classic:
            pass
        else:
            # Генерация случайного игрового поля
            self.board = [[] * size for _ in range(size)]
